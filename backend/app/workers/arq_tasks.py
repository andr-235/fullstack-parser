"""
ARQ задачи для фоновой обработки - Интегрированы с Domain Events системой
"""

from datetime import datetime, timezone
from typing import Any, Dict

import structlog

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.api.v1.infrastructure.events.domain_event_publisher import (
    publish_domain_event,
)
from app.api.v1.infrastructure.events.comment_events import (
    CommentCreatedEvent,
    CommentProcessedEvent,
    CommentKeywordMatchedEvent,
)
from app.api.v1.infrastructure.services.cache_service import RedisCacheService

# Импорты старых сервисов для обратной совместимости
from app.services.monitoring_service import MonitoringService
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import get_redis_parser_manager
from app.services.scheduler_service import SchedulerService
from app.services.vk_api_service import VKAPIService

logger = structlog.get_logger(__name__)


async def run_parsing_task(
    ctx: Dict[str, Any],
    group_id: int,
    max_posts: int | None = None,
    force_reparse: bool = False,
) -> Dict[str, Any]:
    """
    Задача парсинга группы VK

    Args:
        ctx: Контекст ARQ
        group_id: ID группы для парсинга
        max_posts: Максимальное количество постов
        force_reparse: Принудительный перепарсинг

    Returns:
        Результат выполнения задачи
    """
    start_time = datetime.now(timezone.utc)
    task_id = ctx.get("job_id")

    logger.info(
        "Запуск задачи парсинга",
        task_id=task_id,
        group_id=group_id,
        max_posts=max_posts,
        force_reparse=force_reparse,
    )

    try:
        # Получаем зависимости
        redis_manager = get_redis_parser_manager()
        vk_service = VKAPIService(
            token=settings.vk_access_token, api_version=settings.vk_api_version
        )

        # Создаем сессию БД
        async with AsyncSessionLocal() as db:
            parser_service = ParserService(db, vk_service)

            # Запускаем парсинг
            result = await parser_service.parse_group_posts(
                group_id=group_id,
                max_posts_count=max_posts,
                force_reparse=force_reparse,
            )

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        # Интеграция с Domain Events системой
        await _publish_parsing_domain_events(result, group_id)

        logger.info(
            "Задача парсинга завершена успешно",
            task_id=task_id,
            group_id=group_id,
            duration=duration,
            result=result,
        )

        return {
            "status": "success",
            "duration": duration,
            "result": result,
        }

    except Exception as e:
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.error(
            "Ошибка выполнения задачи парсинга",
            task_id=task_id,
            group_id=group_id,
            duration=duration,
            error=str(e),
            exc_info=True,
        )

        return {
            "status": "error",
            "duration": duration,
            "error": str(e),
        }


async def run_monitoring_cycle(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Задача мониторинга групп VK

    Args:
        ctx: Контекст ARQ

    Returns:
        Результат выполнения задачи
    """
    start_time = datetime.now(timezone.utc)
    task_id = ctx.get("job_id")

    logger.info("Запуск цикла мониторинга", task_id=task_id)

    try:
        # Получаем зависимости
        redis_manager = get_redis_parser_manager()
        vk_service = VKAPIService(
            token=settings.vk_access_token, api_version=settings.vk_api_version
        )

        # Создаем сессию БД
        async with AsyncSessionLocal() as db:
            monitoring_service = MonitoringService(db, vk_service)

            # Запускаем мониторинг
            result = await monitoring_service.run_monitoring_cycle()

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info(
            "Цикл мониторинга завершен успешно",
            task_id=task_id,
            duration=duration,
            result=result,
        )

        return {
            "status": "success",
            "duration": duration,
            "result": result,
        }

    except Exception as e:
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.error(
            "Ошибка выполнения цикла мониторинга",
            task_id=task_id,
            duration=duration,
            error=str(e),
            exc_info=True,
        )

        return {
            "status": "error",
            "duration": duration,
            "error": str(e),
        }


async def run_scheduler_task(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Задача планировщика для запуска мониторинга

    Args:
        ctx: Контекст ARQ

    Returns:
        Результат выполнения задачи
    """
    start_time = datetime.now(timezone.utc)
    task_id = ctx.get("job_id")

    logger.info("Запуск задачи планировщика", task_id=task_id)

    try:
        # Получаем зависимости
        redis_manager = get_redis_parser_manager()

        # Создаем сессию БД
        async with AsyncSessionLocal() as db:
            scheduler_service = SchedulerService()

            # Проверяем и запускаем задачи мониторинга
            result = await scheduler_service.process_scheduled_tasks(
                redis_manager
            )

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info(
            "Задача планировщика завершена успешно",
            task_id=task_id,
            duration=duration,
            result=result,
        )

        return {
            "status": "success",
            "duration": duration,
            "result": result,
        }

    except Exception as e:
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.error(
            "Ошибка выполнения задачи планировщика",
            task_id=task_id,
            duration=duration,
            error=str(e),
            exc_info=True,
        )

        return {
            "status": "error",
            "duration": duration,
            "error": str(e),
        }


# Вспомогательные функции для работы с Domain Events


async def _publish_parsing_domain_events(
    result: Dict[str, Any], group_id: int
) -> None:
    """
    Публикует Domain Events на основе результатов парсинга

    Args:
        result: Результаты парсинга
        group_id: ID группы VK
    """
    try:
        # Создаем события для новых комментариев
        new_comments = result.get("new_comments", [])
        for comment_data in new_comments:
            if isinstance(comment_data, dict):
                comment_id = comment_data.get("id")
                post_id = comment_data.get("post_id")
                author_id = comment_data.get("author_id")
                text_length = len(comment_data.get("text", ""))

                if comment_id:
                    # Публикуем событие создания комментария
                    event = CommentCreatedEvent(
                        comment_id=comment_id,
                        group_id=group_id,
                        post_id=post_id,
                        author_id=author_id,
                        text_length=text_length,
                    )
                    await publish_domain_event(event)

                    # Проверяем на ключевые слова и публикуем соответствующее событие
                    matched_keywords = comment_data.get("matched_keywords", [])
                    if matched_keywords:
                        keyword_event = CommentKeywordMatchedEvent(
                            comment_id=comment_id,
                            keyword_id=matched_keywords[0].get(
                                "keyword_id", 0
                            ),  # Первый найденный
                            keyword_word=matched_keywords[0].get("word", ""),
                            match_context=f"Found {len(matched_keywords)} keywords",
                        )
                        await publish_domain_event(keyword_event)

        # Создаем событие обработки для всех найденных комментариев
        total_comments = result.get("total_comments", 0)
        if total_comments > 0:
            processed_event = CommentProcessedEvent(
                comment_id=0,  # Групповое событие
                processing_result="success",
                matched_keywords=[],  # Можно добавить агрегированную информацию
            )
            # Для групповых событий используем специальный comment_id = 0
            await publish_domain_event(processed_event)

        logger.info(
            f"Published {len(new_comments)} domain events for group {group_id}"
        )

    except Exception as e:
        logger.error(f"Error publishing domain events: {e}")
        # Не прерываем выполнение задачи из-за ошибок в событиях


async def _invalidate_cache_for_group(group_id: int) -> None:
    """
    Инвалидирует кеш для группы после парсинга

    Args:
        group_id: ID группы VK
    """
    try:
        cache_service = RedisCacheService()
        await cache_service.invalidate_entity_collection("comment")
        await cache_service.delete(f"group_stats:{group_id}")
        await cache_service.delete(f"group:{group_id}")

        logger.debug(f"Cache invalidated for group {group_id}")

    except Exception as e:
        logger.error(f"Error invalidating cache for group {group_id}: {e}")


async def _update_monitoring_statistics(
    group_id: int, result: Dict[str, Any]
) -> None:
    """
    Обновляет статистику мониторинга группы

    Args:
        group_id: ID группы VK
        result: Результаты парсинга
    """
    try:
        async with AsyncSessionLocal() as db:
            # Импортируем модель группы
            from app.models.vk_group import VKGroup
            from sqlalchemy import select

            # Получаем группу
            stmt = select(VKGroup).where(VKGroup.id == group_id)
            result_db = await db.execute(stmt)
            group = result_db.scalar_one_or_none()

            if group:
                # Обновляем статистику
                posts_parsed = result.get("posts_parsed", 0)
                comments_found = result.get("comments_found", 0)

                group.update_statistics(
                    posts_parsed=posts_parsed, comments_found=comments_found
                )

                # Записываем успешное выполнение мониторинга
                group.record_monitoring_success()

                await db.commit()

                logger.debug(
                    f"Updated monitoring statistics for group {group_id}"
                )

    except Exception as e:
        logger.error(
            f"Error updating monitoring statistics for group {group_id}: {e}"
        )


class WorkerSettings:
    """Настройки ARQ воркера"""

    functions = [
        run_parsing_task,
        run_monitoring_cycle,
        run_scheduler_task,
    ]

    redis_settings = settings.redis_url
    max_jobs = 5
    job_timeout = 1800  # 30 минут
    keep_result = 3600  # Хранить результат 1 час
    max_tries = 3
    retry_delay = 60  # 1 минута между попытками
