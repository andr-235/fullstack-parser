"""
Сервис автоматического мониторинга групп ВК
"""

print("DEBUG: Загрузка monitoring_service.py")

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List

import structlog
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from arq import create_pool
from arq.connections import RedisSettings

from app.models.vk_group import VKGroup
from app.services.arq_enqueue import enqueue_run_parsing_task
from app.services.vk_api_service import VKAPIService
from app.core.config import settings
from app.core.time_utils import (
    format_datetime_for_display,
    format_monitoring_time_for_display,
)

logger = structlog.get_logger(__name__)


class MonitoringService:
    """Сервис для автоматического мониторинга групп ВК"""

    def __init__(self, db: AsyncSession, vk_service: VKAPIService):
        print("DEBUG: Инициализация MonitoringService")
        self.db = db
        self.vk_service = vk_service
        self.logger = logger
        self.redis_pool = None

    async def _get_redis_pool(self):
        """Получить Redis pool для ARQ"""
        if self.redis_pool is None:
            self.redis_pool = await create_pool(
                RedisSettings.from_dsn(settings.redis_url)
            )
        return self.redis_pool

    async def get_groups_for_monitoring(self) -> List[VKGroup]:
        """Получить группы, готовые для мониторинга"""
        # Используем UTC время для сравнения
        from datetime import timezone

        now = datetime.now(timezone.utc)

        # Получаем активные группы с включенным мониторингом,
        # которые нужно проверить сейчас или уже просрочены
        # Обрабатываем как время с часовым поясом, так и без него
        query = (
            select(VKGroup)
            .where(
                and_(
                    VKGroup.is_active,
                    VKGroup.auto_monitoring_enabled,
                    # Сравниваем время мониторинга
                    VKGroup.next_monitoring_at <= now,
                )
            )
            .order_by(
                VKGroup.monitoring_priority.desc(),  # Сначала высокий приоритет
                VKGroup.next_monitoring_at.asc(),  # Потом по времени
            )
            .limit(50)  # Ограничиваем количество групп за раз
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def schedule_group_monitoring(self, group: VKGroup) -> None:
        """Запланировать следующий мониторинг группы"""
        if not group.auto_monitoring_enabled:
            return

        # Используем UTC время для планирования
        from datetime import timezone

        # Рассчитываем время следующего мониторинга в UTC
        next_time = datetime.now(timezone.utc) + timedelta(
            minutes=group.monitoring_interval_minutes
        )

        # Сохраняем в UTC без удаления часового пояса
        group.next_monitoring_at = next_time
        await self.db.commit()

        self.logger.info(
            "Запланирован следующий мониторинг группы",
            group_id=group.id,
            group_name=group.name,
            next_monitoring_at=next_time.isoformat(),
        )

    async def start_group_monitoring(self, group: VKGroup) -> bool:
        """Запустить мониторинг конкретной группы"""
        try:
            self.logger.info(
                "Запуск мониторинга группы",
                group_id=group.id,
                group_name=group.name,
            )

            # Получаем Redis pool
            redis_pool = await self._get_redis_pool()

            # Создаём уникальный ID задачи
            task_id = f"monitor_{group.id}_{int(datetime.now().timestamp())}"

            # Ставим задачу в очередь ARQ
            job = await redis_pool.enqueue_job(
                "run_parsing_task",
                group_id=group.id,
                max_posts=group.max_posts_to_check,
                force_reparse=False,
                _job_id=task_id,
            )

            if job:
                self.logger.info(
                    "Задача парсинга поставлена в очередь ARQ",
                    group_id=group.id,
                    job_id=job.job_id,
                )

                # Обновляем статистику
                group.monitoring_runs_count += 1
                group.last_monitoring_success = datetime.now(timezone.utc)
                group.last_monitoring_error = None

                # Планируем следующий мониторинг
                await self.schedule_group_monitoring(group)

                self.logger.info(
                    "Мониторинг группы успешно запущен",
                    group_id=group.id,
                    group_name=group.name,
                    task_id=task_id,
                )

                return True
            else:
                self.logger.error(
                    "Не удалось поставить задачу в очередь ARQ",
                    group_id=group.id,
                )
                return False

        except Exception as e:
            self.logger.error(
                "Ошибка запуска мониторинга группы",
                group_id=group.id,
                group_name=group.name,
                error=str(e),
                exc_info=True,
            )

            # Записываем ошибку
            group.last_monitoring_error = str(e)
            await self.db.commit()

            return False

    async def run_monitoring_cycle(self) -> dict:
        """Запустить цикл мониторинга всех готовых групп"""
        start_time = datetime.now(timezone.utc)

        self.logger.info("Запуск цикла автоматического мониторинга")

        # Получаем группы для мониторинга
        groups = await self.get_groups_for_monitoring()

        if not groups:
            self.logger.info("Нет групп, готовых для мониторинга")
            return {
                "total_groups": 0,
                "monitored_groups": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "duration_seconds": 0,
            }

        self.logger.info("Найдено групп для мониторинга", count=len(groups))

        # Запускаем мониторинг для каждой группы
        successful_runs = 0
        failed_runs = 0

        for group in groups:
            try:
                success = await self.start_group_monitoring(group)
                if success:
                    successful_runs += 1
                else:
                    failed_runs += 1

                # Небольшая задержка между группами, чтобы не перегружать VK API
                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(
                    "Критическая ошибка при мониторинге группы",
                    group_id=group.id,
                    group_name=group.name,
                    error=str(e),
                    exc_info=True,
                )
                failed_runs += 1

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        stats = {
            "total_groups": len(groups),
            "monitored_groups": successful_runs + failed_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "duration_seconds": duration,
        }

        self.logger.info("Цикл мониторинга завершён", **stats)

        return stats

    async def enable_group_monitoring(
        self, group_id: int, interval_minutes: int = 60, priority: int = 5
    ) -> bool:
        """Включить автоматический мониторинг для группы"""
        try:
            result = await self.db.execute(
                select(VKGroup).where(VKGroup.id == group_id)
            )
            group = result.scalar_one_or_none()

            if not group:
                self.logger.warning("Группа не найдена", group_id=group_id)
                return False

            if not group.is_active:
                self.logger.warning(
                    "Нельзя включить мониторинг для неактивной группы",
                    group_id=group_id,
                )
                return False

            # Включаем мониторинг
            group.auto_monitoring_enabled = True
            group.monitoring_interval_minutes = max(
                1, min(1440, interval_minutes)
            )  # 1-1440 минут
            group.monitoring_priority = max(1, min(10, priority))  # 1-10
            group.next_monitoring_at = datetime.now(timezone.utc)

            await self.db.commit()

            self.logger.info(
                "Включен автоматический мониторинг группы",
                group_id=group_id,
                group_name=group.name,
                interval_minutes=group.monitoring_interval_minutes,
                priority=group.monitoring_priority,
            )

            return True

        except Exception as e:
            self.logger.error(
                "Ошибка включения мониторинга группы",
                group_id=group_id,
                error=str(e),
                exc_info=True,
            )
            return False

    async def disable_group_monitoring(self, group_id: int) -> bool:
        """Отключить автоматический мониторинг для группы"""
        try:
            result = await self.db.execute(
                select(VKGroup).where(VKGroup.id == group_id)
            )
            group = result.scalar_one_or_none()

            if not group:
                self.logger.warning("Группа не найдена", group_id=group_id)
                return False

            # Отключаем мониторинг
            group.auto_monitoring_enabled = False
            group.next_monitoring_at = None

            await self.db.commit()

            self.logger.info(
                "Отключен автоматический мониторинг группы",
                group_id=group_id,
                group_name=group.name,
            )

            return True

        except Exception as e:
            self.logger.error(
                "Ошибка отключения мониторинга группы",
                group_id=group_id,
                error=str(e),
                exc_info=True,
            )
            return False

    async def get_monitoring_stats(self) -> dict:
        """Получить статистику мониторинга"""
        print("DEBUG: Начало получения статистики мониторинга")
        self.logger.info("Начало получения статистики мониторинга")
        try:
            # Общая статистика
            total_groups = await self.db.execute(select(VKGroup))
            total_groups = len(total_groups.scalars().all())

            active_groups = await self.db.execute(
                select(VKGroup).where(VKGroup.is_active)
            )
            active_groups = len(active_groups.scalars().all())

            monitored_groups = await self.db.execute(
                select(VKGroup).where(
                    and_(
                        VKGroup.is_active,
                        VKGroup.auto_monitoring_enabled,
                    )
                )
            )
            monitored_groups = len(monitored_groups.scalars().all())

            # Группы, готовые для мониторинга
            from datetime import timezone

            now = datetime.now(timezone.utc)
            ready_groups = await self.db.execute(
                select(VKGroup).where(
                    and_(
                        VKGroup.is_active,
                        VKGroup.auto_monitoring_enabled,
                        # Сравниваем время мониторинга
                        VKGroup.next_monitoring_at <= now,
                    )
                )
            )
            ready_groups = len(ready_groups.scalars().all())

            # Следующий мониторинг
            next_monitoring = await self.db.execute(
                select(VKGroup.next_monitoring_at)
                .where(
                    and_(
                        VKGroup.is_active,
                        VKGroup.auto_monitoring_enabled,
                        VKGroup.next_monitoring_at.isnot(None),
                    )
                )
                .order_by(VKGroup.next_monitoring_at.asc())
                .limit(1)
            )
            next_monitoring_time = next_monitoring.scalar()

            # Конвертируем в локальное время для отображения
            self.logger.info("Начинаем конвертацию времени")
            from app.core.time_utils import format_datetime_for_display

            next_monitoring_local = None
            if next_monitoring_time:
                try:
                    self.logger.info(
                        "Конвертируем время",
                        utc_time=next_monitoring_time.isoformat(),
                    )
                    next_monitoring_local = format_monitoring_time_for_display(
                        next_monitoring_time
                    )
                    self.logger.info(
                        "Время сконвертировано",
                        local_time=next_monitoring_local,
                    )
                except Exception as e:
                    self.logger.error(
                        "Ошибка конвертации времени",
                        error=str(e),
                        exc_info=True,
                    )
                    next_monitoring_local = None
            else:
                self.logger.info("Нет времени для конвертации")

            result = {
                "total_groups": total_groups,
                "active_groups": active_groups,
                "monitored_groups": monitored_groups,
                "ready_for_monitoring": ready_groups,
                "next_monitoring_at": (
                    next_monitoring_time.isoformat()
                    if next_monitoring_time
                    else None
                ),
                "next_monitoring_at_local": next_monitoring_local,
            }

            self.logger.info("Возвращаем результат", result=result)
            return result

        except Exception as e:
            self.logger.error(
                "Ошибка получения статистики мониторинга",
                error=str(e),
                exc_info=True,
            )
            return {
                "total_groups": 0,
                "active_groups": 0,
                "monitored_groups": 0,
                "ready_for_monitoring": 0,
                "next_monitoring_at": None,
                "next_monitoring_at_local": None,
            }
