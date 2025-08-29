"""
MonitoringService - DDD Application Service для мониторинга групп VK

Мигрирован из app/services/monitoring_service.py
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

import structlog
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy import and_, or_, select

from app.models.vk_group import VKGroup


class MonitoringService:
    """
    DDD Application Service для автоматического мониторинга групп VK.

    Предоставляет высокоуровневый интерфейс для:
    - Управления автоматическим мониторингом групп
    - Планирования задач мониторинга
    - Статистики мониторинга
    - Включения/отключения мониторинга
    """

    def __init__(self, db=None, vk_service=None):
        """
        Инициализация MonitoringService.

        Args:
            db: Асинхронная сессия базы данных
            vk_service: Сервис VK API
        """
        self.db = db
        self.vk_service = vk_service
        self.logger = structlog.get_logger(__name__)
        self.redis_pool = None

    # =============== МИГРАЦИЯ MonitoringService В DDD ===============

    async def get_groups_for_monitoring_ddd(self) -> Dict[str, Any]:
        """
        Получить группы, готовые для мониторинга (мигрировано из MonitoringService)

        Returns:
            Список групп для мониторинга с метаданными
        """
        try:
            now = datetime.now(timezone.utc)

            # Получаем активные группы с включенным мониторингом
            query = (
                select(VKGroup)
                .where(
                    and_(
                        VKGroup.is_active == True,
                        VKGroup.auto_monitoring_enabled == True,
                        or_(
                            VKGroup.next_monitoring_at.is_(None),
                            VKGroup.next_monitoring_at <= now,
                        ),
                    )
                )
                .order_by(
                    VKGroup.monitoring_priority.desc(),
                    VKGroup.next_monitoring_at.asc().nulls_last(),
                )
                .limit(50)
            )

            result = await self.db.execute(query)
            groups = list(result.scalars().all())

            # Преобразуем в response формат
            groups_response = []
            for group in groups:
                groups_response.append(
                    {
                        "id": group.id,
                        "name": group.name,
                        "screen_name": group.screen_name,
                        "next_monitoring_at": (
                            group.next_monitoring_at.isoformat()
                            if group.next_monitoring_at
                            else None
                        ),
                        "monitoring_priority": group.monitoring_priority,
                        "is_active": group.is_active,
                        "auto_monitoring_enabled": group.auto_monitoring_enabled,
                    }
                )

            return {
                "groups": groups_response,
                "total": len(groups_response),
                "current_time": now.isoformat(),
                "monitoring_ready": len(groups_response) > 0,
            }

        except Exception as e:
            self.logger.error(f"Error getting groups for monitoring: {e}")
            raise

    async def schedule_group_monitoring_ddd(
        self, group_id: int, delay_minutes: int = 0
    ) -> Dict[str, Any]:
        """
        Запланировать мониторинг группы (мигрировано из MonitoringService)

        Args:
            group_id: ID группы VK
            delay_minutes: Задержка в минутах

        Returns:
            Результат планирования
        """
        try:
            # Находим группу
            query = select(VKGroup).where(VKGroup.id == group_id)
            result = await self.db.execute(query)
            group = result.scalar_one_or_none()

            if not group:
                return {
                    "scheduled": False,
                    "reason": "Group not found",
                    "group_id": group_id,
                }

            # Вычисляем время следующего мониторинга
            now = datetime.now(timezone.utc)
            next_monitoring = now + timedelta(minutes=delay_minutes)

            # Обновляем время мониторинга
            group.next_monitoring_at = next_monitoring
            group.updated_at = now

            await self.db.commit()

            # Получаем Redis pool для планирования задачи
            redis_pool = await self._get_redis_pool()

            # Планируем задачу в ARQ
            await redis_pool.enqueue_job(
                "monitor_group",
                group.id,
                _defer_by=timedelta(minutes=delay_minutes),
            )

            return {
                "scheduled": True,
                "group_id": group_id,
                "group_name": group.name,
                "next_monitoring_at": next_monitoring.isoformat(),
                "delay_minutes": delay_minutes,
                "scheduled_at": now.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error scheduling group monitoring: {e}")
            raise

    async def start_group_monitoring_ddd(
        self, group_id: int
    ) -> Dict[str, Any]:
        """
        Начать мониторинг группы (мигрировано из MonitoringService)

        Args:
            group_id: ID группы VK

        Returns:
            Результат запуска мониторинга
        """
        try:
            # Находим группу
            query = select(VKGroup).where(VKGroup.id == group_id)
            result = await self.db.execute(query)
            group = result.scalar_one_or_none()

            if not group:
                return {
                    "started": False,
                    "reason": "Group not found",
                    "group_id": group_id,
                }

            if not group.is_active:
                return {
                    "started": False,
                    "reason": "Group is not active",
                    "group_id": group_id,
                }

            # Включаем мониторинг
            now = datetime.now(timezone.utc)
            group.auto_monitoring_enabled = True
            group.last_monitoring_at = now
            group.next_monitoring_at = now  # Начать сразу
            group.monitoring_success_count = 0
            group.monitoring_error_count = 0
            group.updated_at = now

            await self.db.commit()

            # Запускаем задачу мониторинга
            redis_pool = await self._get_redis_pool()
            await redis_pool.enqueue_job("monitor_group", group.id)

            return {
                "started": True,
                "group_id": group_id,
                "group_name": group.name,
                "monitoring_enabled": True,
                "started_at": now.isoformat(),
                "next_monitoring_at": now.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error starting group monitoring: {e}")
            raise

    async def run_monitoring_cycle_ddd(self) -> Dict[str, Any]:
        """
        Запустить цикл мониторинга (мигрировано из MonitoringService)

        Returns:
            Результат цикла мониторинга
        """
        try:
            # Получаем группы для мониторинга
            groups_data = await self.get_groups_for_monitoring_ddd()
            groups = groups_data["groups"]

            if not groups:
                return {
                    "cycle_completed": True,
                    "groups_processed": 0,
                    "message": "No groups ready for monitoring",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Обрабатываем группы
            processed = 0
            successful = 0
            failed = 0

            for group_data in groups:
                try:
                    group_id = group_data["id"]
                    result = await self.start_group_monitoring_ddd(group_id)

                    if result["started"]:
                        successful += 1
                    else:
                        failed += 1

                    processed += 1

                    # Небольшая задержка между группами
                    await asyncio.sleep(0.1)

                except Exception as e:
                    self.logger.error(
                        f"Error monitoring group {group_data['id']}: {e}"
                    )
                    failed += 1
                    processed += 1

            return {
                "cycle_completed": True,
                "groups_processed": processed,
                "successful": successful,
                "failed": failed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Monitoring cycle completed: {successful}/{processed} successful",
            }

        except Exception as e:
            self.logger.error(f"Error running monitoring cycle: {e}")
            raise

    async def enable_group_monitoring_ddd(
        self, group_id: int, priority: int = 1, interval_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Включить мониторинг группы (мигрировано из MonitoringService)

        Args:
            group_id: ID группы VK
            priority: Приоритет мониторинга (1-10)
            interval_hours: Интервал мониторинга в часах

        Returns:
            Результат включения мониторинга
        """
        try:
            # Находим группу
            query = select(VKGroup).where(VKGroup.id == group_id)
            result = await self.db.execute(query)
            group = result.scalar_one_or_none()

            if not group:
                return {
                    "enabled": False,
                    "reason": "Group not found",
                    "group_id": group_id,
                }

            if not group.is_active:
                return {
                    "enabled": False,
                    "reason": "Group is not active",
                    "group_id": group_id,
                }

            # Включаем мониторинг
            now = datetime.now(timezone.utc)
            group.auto_monitoring_enabled = True
            group.monitoring_priority = priority
            group.monitoring_interval_hours = interval_hours
            group.next_monitoring_at = now
            group.updated_at = now

            await self.db.commit()

            return {
                "enabled": True,
                "group_id": group_id,
                "group_name": group.name,
                "priority": priority,
                "interval_hours": interval_hours,
                "next_monitoring_at": now.isoformat(),
                "enabled_at": now.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error enabling group monitoring: {e}")
            raise

    async def disable_group_monitoring_ddd(
        self, group_id: int
    ) -> Dict[str, Any]:
        """
        Отключить мониторинг группы (мигрировано из MonitoringService)

        Args:
            group_id: ID группы VK

        Returns:
            Результат отключения мониторинга
        """
        try:
            # Находим группу
            query = select(VKGroup).where(VKGroup.id == group_id)
            result = await self.db.execute(query)
            group = result.scalar_one_or_none()

            if not group:
                return {
                    "disabled": False,
                    "reason": "Group not found",
                    "group_id": group_id,
                }

            # Отключаем мониторинг
            now = datetime.now(timezone.utc)
            group.auto_monitoring_enabled = False
            group.next_monitoring_at = None
            group.updated_at = now

            await self.db.commit()

            return {
                "disabled": True,
                "group_id": group_id,
                "group_name": group.name,
                "disabled_at": now.isoformat(),
                "message": f"Monitoring disabled for group {group.name}",
            }

        except Exception as e:
            self.logger.error(f"Error disabling group monitoring: {e}")
            raise

    async def get_monitoring_stats_ddd(self) -> Dict[str, Any]:
        """
        Получить статистику мониторинга (мигрировано из MonitoringService)

        Returns:
            Статистика мониторинга
        """
        try:
            # Получаем все группы
            query = select(VKGroup)
            result = await self.db.execute(query)
            all_groups = result.scalars().all()

            # Подсчитываем статистику
            total_groups = len(all_groups)
            active_groups = len([g for g in all_groups if g.is_active])
            monitoring_enabled = len(
                [g for g in all_groups if g.auto_monitoring_enabled]
            )
            monitoring_ready = len(
                [
                    g
                    for g in all_groups
                    if g.is_active
                    and g.auto_monitoring_enabled
                    and (
                        g.next_monitoring_at is None
                        or g.next_monitoring_at <= datetime.now(timezone.utc)
                    )
                ]
            )

            # Группируем по приоритетам
            priorities = {}
            for group in all_groups:
                if group.auto_monitoring_enabled:
                    priority = group.monitoring_priority or 1
                    if priority not in priorities:
                        priorities[priority] = 0
                    priorities[priority] += 1

            return {
                "total_groups": total_groups,
                "active_groups": active_groups,
                "monitoring_enabled": monitoring_enabled,
                "monitoring_ready": monitoring_ready,
                "monitoring_disabled": total_groups - monitoring_enabled,
                "priorities": priorities,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting monitoring stats: {e}")
            raise

    async def reset_monitoring_times_ddd(self) -> Dict[str, Any]:
        """
        Сбросить времена мониторинга (мигрировано из MonitoringService)

        Returns:
            Результат сброса
        """
        try:
            # Сбрасываем времена мониторинга для всех активных групп
            query = select(VKGroup).where(
                and_(
                    VKGroup.is_active == True,
                    VKGroup.auto_monitoring_enabled == True,
                )
            )

            result = await self.db.execute(query)
            groups = result.scalars().all()

            now = datetime.now(timezone.utc)
            reset_count = 0

            for group in groups:
                group.next_monitoring_at = now
                group.updated_at = now
                reset_count += 1

            await self.db.commit()

            return {
                "reset": True,
                "groups_reset": reset_count,
                "reset_at": now.isoformat(),
                "message": f"Monitoring times reset for {reset_count} groups",
            }

        except Exception as e:
            self.logger.error(f"Error resetting monitoring times: {e}")
            raise

    # =============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===============

    async def _get_redis_pool(self):
        """
        Получить Redis pool для ARQ
        """
        if self.redis_pool is None:
            from app.core.config import settings

            self.redis_pool = await create_pool(
                RedisSettings.from_dsn(settings.redis_url)
            )
        return self.redis_pool

    # =============== МИГРАЦИЯ SchedulerService В DDD ===============

    async def initialize_scheduler_ddd(self):
        """
        Инициализация планировщика (мигрировано из SchedulerService)

        Returns:
            Результат инициализации
        """
        try:
            redis_pool = await self._get_redis_pool()

            return {
                "initialized": True,
                "redis_connected": True,
                "message": "Scheduler initialized successfully",
                "initialized_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error initializing scheduler: {e}")
            return {
                "initialized": False,
                "error": str(e),
                "redis_connected": False,
            }

    async def start_monitoring_scheduler_ddd(
        self, interval_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Запустить планировщик мониторинга (мигрировано из SchedulerService)

        Args:
            interval_seconds: Интервал между циклами в секундах

        Returns:
            Результат запуска планировщика
        """
        try:
            # Проверяем, не запущен ли уже планировщик
            if hasattr(self, "_scheduler_running") and self._scheduler_running:
                return {
                    "started": False,
                    "error": "Scheduler is already running",
                    "interval_seconds": interval_seconds,
                }

            # Инициализируем планировщик
            init_result = await self.initialize_scheduler_ddd()
            if not init_result["initialized"]:
                return {
                    "started": False,
                    "error": init_result["error"],
                    "interval_seconds": interval_seconds,
                }

            # Запускаем планировщик
            self._scheduler_running = True
            self._scheduler_interval = interval_seconds

            # Запускаем фоновую задачу
            import asyncio

            asyncio.create_task(self._run_scheduler_loop_ddd(interval_seconds))

            return {
                "started": True,
                "interval_seconds": interval_seconds,
                "message": f"Monitoring scheduler started with {interval_seconds}s interval",
                "started_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error starting monitoring scheduler: {e}")
            return {
                "started": False,
                "error": str(e),
                "interval_seconds": interval_seconds,
            }

    async def stop_monitoring_scheduler_ddd(self) -> Dict[str, Any]:
        """
        Остановить планировщик мониторинга (мигрировано из SchedulerService)

        Returns:
            Результат остановки планировщика
        """
        try:
            if (
                not hasattr(self, "_scheduler_running")
                or not self._scheduler_running
            ):
                return {
                    "stopped": False,
                    "message": "Scheduler is not running",
                }

            self._scheduler_running = False

            return {
                "stopped": True,
                "message": "Monitoring scheduler stopped",
                "stopped_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error stopping monitoring scheduler: {e}")
            return {
                "stopped": False,
                "error": str(e),
            }

    async def run_manual_monitoring_cycle_ddd(self) -> Dict[str, Any]:
        """
        Запустить цикл мониторинга вручную (мигрировано из SchedulerService)

        Returns:
            Результат выполнения цикла
        """
        try:
            redis_pool = await self._get_redis_pool()

            # Ставим задачу в очередь
            job = await redis_pool.enqueue_job("run_monitoring_cycle")

            if job:
                return {
                    "executed": True,
                    "job_id": job.job_id,
                    "message": "Manual monitoring cycle enqueued",
                    "enqueued_at": datetime.now(timezone.utc).isoformat(),
                }
            else:
                return {
                    "executed": False,
                    "error": "Failed to enqueue monitoring cycle",
                }

        except Exception as e:
            self.logger.error(f"Error running manual monitoring cycle: {e}")
            return {
                "executed": False,
                "error": str(e),
            }

    async def process_scheduled_tasks_ddd(
        self, redis_manager=None
    ) -> Dict[str, Any]:
        """
        Обработать запланированные задачи (мигрировано из SchedulerService)

        Args:
            redis_manager: Менеджер Redis (опционально)

        Returns:
            Результат обработки задач
        """
        try:
            # Используем переданный менеджер или получаем свой
            redis_pool = redis_manager or await self._get_redis_pool()

            # Получаем активные задачи
            active_jobs = await redis_pool.get_active_jobs()

            # Получаем ожидающие задачи
            pending_jobs = await redis_pool.get_pending_jobs()

            # Обрабатываем просроченные задачи
            expired_count = 0
            for job in pending_jobs:
                # Проверяем, не просрочена ли задача
                enqueued_at = job.get("enqueued_at")
                if enqueued_at:
                    # Если задача ждет больше часа, считаем ее просроченной
                    import time

                    if time.time() - enqueued_at.timestamp() > 3600:
                        await redis_pool.abort_job(job["job_id"])
                        expired_count += 1

            return {
                "processed": True,
                "active_jobs": len(active_jobs),
                "pending_jobs": len(pending_jobs),
                "expired_jobs": expired_count,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error processing scheduled tasks: {e}")
            return {
                "processed": False,
                "error": str(e),
            }

    async def get_scheduler_status_ddd(self) -> Dict[str, Any]:
        """
        Получить статус планировщика (мигрировано из SchedulerService)

        Returns:
            Статус планировщика
        """
        try:
            status = {
                "service": "monitoring_scheduler",
                "is_running": getattr(self, "_scheduler_running", False),
                "interval_seconds": getattr(self, "_scheduler_interval", None),
                "redis_connected": self.redis_pool is not None,
            }

            # Получаем статистику задач
            if self.redis_pool:
                try:
                    active_jobs = await self.redis_pool.get_active_jobs()
                    pending_jobs = await self.redis_pool.get_pending_jobs()

                    status.update(
                        {
                            "active_jobs_count": len(active_jobs),
                            "pending_jobs_count": len(pending_jobs),
                            "total_queued_jobs": len(active_jobs)
                            + len(pending_jobs),
                        }
                    )
                except Exception as e:
                    status["queue_error"] = str(e)

            status["checked_at"] = datetime.now(timezone.utc).isoformat()

            return status

        except Exception as e:
            self.logger.error(f"Error getting scheduler status: {e}")
            return {
                "service": "monitoring_scheduler",
                "status": "error",
                "error": str(e),
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

    # =============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ SchedulerService ===============

    async def _run_scheduler_loop_ddd(self, interval_seconds: int):
        """
        Основной цикл планировщика
        """
        try:
            while getattr(self, "_scheduler_running", False):
                try:
                    # Запускаем цикл мониторинга
                    await self._run_monitoring_cycle_ddd()
                except Exception as e:
                    self.logger.error(f"Error in monitoring cycle: {e}")

                # Ждем следующий интервал
                await asyncio.sleep(interval_seconds)

        except Exception as e:
            self.logger.error(f"Error in scheduler loop: {e}")
        finally:
            self._scheduler_running = False

    async def _run_monitoring_cycle_ddd(self):
        """
        Запустить один цикл мониторинга
        """
        try:
            if not self.redis_pool:
                self.logger.error("Redis pool not initialized")
                return

            # Ставим задачу в очередь
            job = await self.redis_pool.enqueue_job("run_monitoring_cycle")

            if job:
                self.logger.info(
                    "Monitoring cycle task enqueued",
                    job_id=job.job_id,
                )
            else:
                self.logger.warning("Failed to enqueue monitoring cycle")

        except Exception as e:
            self.logger.error(f"Error running monitoring cycle: {e}")

    async def close_scheduler_ddd(self):
        """
        Закрыть соединения планировщика
        """
        try:
            if self.redis_pool:
                await self.redis_pool.close()
                self.redis_pool = None

            self._scheduler_running = False

            return {
                "closed": True,
                "message": "Scheduler connections closed",
                "closed_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error closing scheduler: {e}")
            return {
                "closed": False,
                "error": str(e),
            }
