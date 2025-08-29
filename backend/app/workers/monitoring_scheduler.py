#!/usr/bin/env python3
"""
Скрипт для запуска планировщика автоматического мониторинга
"""

import asyncio
import signal
import sys
from datetime import datetime, timezone

import structlog
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.vk_group import VKGroup
from app.services.monitoring_service import MonitoringService
from app.services.vk_api_service import VKAPIService

# Интеграция с Domain Events системой
from app.api.v1.infrastructure.events.domain_event_publisher import (
    publish_domain_event,
)
from app.api.v1.infrastructure.events.comment_events import (
    CommentBulkOperationEvent,
)

logger = structlog.get_logger(__name__)


async def check_and_fix_outdated_monitoring_times(db: AsyncSession):
    """Проверить и исправить устаревшее время мониторинга"""
    try:
        now = datetime.now(timezone.utc)

        # Находим группы с устаревшим временем мониторинга
        result = await db.execute(
            select(VKGroup).where(
                and_(
                    VKGroup.is_active == True,
                    VKGroup.auto_monitoring_enabled == True,
                    VKGroup.next_monitoring_at <= now,
                )
            )
        )
        outdated_groups = result.scalars().all()

        if outdated_groups:
            logger.warning(
                f"Найдено {len(outdated_groups)} групп с устаревшим временем мониторинга"
            )

            # Обновляем время для всех устаревших групп
            next_time = (
                now  # Устанавливаем на текущее время для немедленного запуска
            )

            await db.execute(
                update(VKGroup)
                .where(
                    and_(
                        VKGroup.is_active == True,
                        VKGroup.auto_monitoring_enabled == True,
                        VKGroup.next_monitoring_at <= now,
                    )
                )
                .values(next_monitoring_at=next_time)
            )
            await db.commit()

            logger.info(
                f"Обновлено время мониторинга для {len(outdated_groups)} групп на {next_time.isoformat()}"
            )
        else:
            logger.info("Все группы имеют актуальное время мониторинга")

    except Exception as e:
        logger.error(f"Ошибка при проверке устаревшего времени: {e}")
        await db.rollback()


async def main():
    """Основная функция запуска планировщика"""
    logger.info("🚀 Запуск планировщика автоматического мониторинга")

    # Настройка обработчика сигналов для graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"📡 Получен сигнал {signum}, завершение работы...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Инициализируем Redis pool
        redis_pool = await create_pool(
            RedisSettings.from_dsn(settings.redis_url)
        )
        logger.info("✅ Подключение к Redis установлено")

        # Получаем интервал мониторинга
        monitoring_interval = getattr(
            settings, "monitoring_interval_seconds", 300
        )

        logger.info(
            "⏰ Планировщик запущен",
            interval_seconds=monitoring_interval,
            start_time=datetime.now(timezone.utc).isoformat(),
        )

        # Основной цикл планировщика
        while True:
            try:
                logger.info("🔄 Запуск цикла мониторинга")

                # Создаем сессию БД
                async with AsyncSessionLocal() as db:
                    # Проверяем и исправляем устаревшее время мониторинга
                    await check_and_fix_outdated_monitoring_times(db)

                    # Инициализируем сервисы
                    vk_service = VKAPIService(
                        token=settings.vk_access_token,
                        api_version=settings.vk_api_version,
                    )
                    monitoring_service = MonitoringService(db, vk_service)

                    # Запускаем цикл мониторинга
                    result = await monitoring_service.run_monitoring_cycle()

                    # Интеграция с Domain Events системой
                    await _publish_monitoring_domain_events(result)

                    logger.info("✅ Цикл мониторинга завершен", result=result)

                # Ждем до следующего цикла
                logger.info(
                    f"⏳ Ожидание {monitoring_interval} секунд до следующего цикла"
                )
                await asyncio.sleep(monitoring_interval)

            except Exception as e:
                logger.error(
                    "💥 Ошибка в цикле мониторинга",
                    error=str(e),
                    exc_info=True,
                )
                # Ждем 60 секунд перед повторной попыткой
                await asyncio.sleep(60)

    except KeyboardInterrupt:
        logger.info("🛑 Планировщик остановлен пользователем")
    except Exception as e:
        logger.error(
            "💥 Критическая ошибка планировщика", error=str(e), exc_info=True
        )
        sys.exit(1)
    finally:
        if "redis_pool" in locals():
            await redis_pool.close()
            logger.info("🔌 Соединение с Redis закрыто")


# Вспомогательные функции для работы с Domain Events


async def _publish_monitoring_domain_events(result: Dict) -> None:
    """
    Публикует Domain Events на основе результатов мониторинга

    Args:
        result: Результаты цикла мониторинга
    """
    try:
        processed_groups = result.get("processed_groups", [])
        total_comments = result.get("total_comments_found", 0)

        # Создаем групповое событие для всех обработанных комментариев
        if total_comments > 0 and processed_groups:
            bulk_event = CommentBulkOperationEvent(
                operation_type="monitoring_cycle",
                comment_ids=[],  # Для мониторинга у нас нет конкретных ID комментариев
                operation_params={
                    "processed_groups": len(processed_groups),
                    "total_comments_found": total_comments,
                    "monitoring_cycle": True,
                },
                affected_count=total_comments,
            )
            await publish_domain_event(bulk_event)

        # Можно добавить более детальные события для каждой группы
        for group_data in processed_groups:
            group_id = group_data.get("group_id")
            comments_found = group_data.get("comments_found", 0)

            if comments_found > 0:
                logger.debug(
                    f"Group {group_id} monitoring found {comments_found} comments"
                )
                # Здесь можно добавить специфические события для группы

        logger.info(
            f"Published monitoring domain events: {len(processed_groups)} groups, "
            f"{total_comments} total comments"
        )

    except Exception as e:
        logger.error(f"Error publishing monitoring domain events: {e}")
        # Не прерываем выполнение цикла из-за ошибок в событиях


async def _update_group_monitoring_status(
    db: AsyncSession, group_id: int, success: bool
) -> None:
    """
    Обновляет статус мониторинга группы с использованием DDD методов

    Args:
        db: Сессия базы данных
        group_id: ID группы
        success: Успешность выполнения мониторинга
    """
    try:
        from sqlalchemy import select

        stmt = select(VKGroup).where(VKGroup.id == group_id)
        result = await db.execute(stmt)
        group = result.scalar_one_or_none()

        if group:
            if success:
                # Используем DDD метод для записи успешного мониторинга
                group.record_monitoring_success()
            else:
                # Для ошибок можно добавить специальную логику
                group.record_monitoring_error("Monitoring cycle failed")

            await db.commit()
            logger.debug(
                f"Updated monitoring status for group {group_id}: success={success}"
            )

    except Exception as e:
        logger.error(f"Error updating group monitoring status {group_id}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
