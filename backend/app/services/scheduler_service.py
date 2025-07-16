"""
Сервис планировщика для автоматического мониторинга
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

import structlog
from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings

logger = structlog.get_logger(__name__)


class SchedulerService:
    """Сервис для планирования автоматических задач мониторинга"""

    def __init__(self):
        self.redis_pool = None
        self.is_running = False
        self.monitoring_interval_seconds = 300  # 5 минут по умолчанию
        self.logger = logger

    async def initialize(self):
        """Инициализация подключения к Redis"""
        try:
            self.redis_pool = await create_pool(
                RedisSettings.from_dsn(settings.redis_url)
            )
            self.logger.info("SchedulerService инициализирован")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации SchedulerService: {e}")
            raise

    async def start_monitoring_scheduler(self, interval_seconds: int = 300):
        """Запустить планировщик мониторинга"""
        if self.is_running:
            self.logger.warning("Планировщик уже запущен")
            return

        if not self.redis_pool:
            await self.initialize()

        self.monitoring_interval_seconds = interval_seconds
        self.is_running = True

        self.logger.info(
            "Запуск планировщика мониторинга",
            interval_seconds=interval_seconds,
        )

        try:
            while self.is_running:
                await self._run_monitoring_cycle()
                await asyncio.sleep(interval_seconds)
        except Exception as e:
            self.logger.error(
                "Ошибка в планировщике мониторинга",
                error=str(e),
                exc_info=True,
            )
        finally:
            self.is_running = False

    async def stop_monitoring_scheduler(self):
        """Остановить планировщик мониторинга"""
        self.logger.info("Остановка планировщика мониторинга")
        self.is_running = False

    async def _run_monitoring_cycle(self):
        """Запустить один цикл мониторинга"""
        try:
            if not self.redis_pool:
                self.logger.error("Redis pool не инициализирован")
                return

            # Ставим задачу в очередь
            job = await self.redis_pool.enqueue_job("run_monitoring_cycle")

            if job:
                self.logger.info(
                    "Задача мониторинга поставлена в очередь",
                    job_id=job.job_id,
                )
            else:
                self.logger.warning("Не удалось поставить задачу мониторинга")

        except Exception as e:
            self.logger.error(
                "Ошибка запуска цикла мониторинга", error=str(e), exc_info=True
            )

    async def run_manual_monitoring_cycle(self) -> Optional[str]:
        """Запустить цикл мониторинга вручную"""
        try:
            if not self.redis_pool:
                await self.initialize()

            job = await self.redis_pool.enqueue_job("run_monitoring_cycle")

            if job:
                self.logger.info(
                    "Ручной запуск цикла мониторинга", job_id=job.job_id
                )
                return job.job_id
            else:
                self.logger.warning(
                    "Не удалось запустить ручной цикл мониторинга"
                )
                return None

        except Exception as e:
            self.logger.error(
                "Ошибка ручного запуска мониторинга",
                error=str(e),
                exc_info=True,
            )
            return None

    async def get_scheduler_status(self) -> dict:
        """Получить статус планировщика"""
        return {
            "is_running": self.is_running,
            "monitoring_interval_seconds": self.monitoring_interval_seconds,
            "redis_connected": self.redis_pool is not None,
            "last_check": datetime.now(timezone.utc).isoformat(),
        }

    async def close(self):
        """Закрыть соединения"""
        if self.redis_pool:
            await self.redis_pool.close()
            self.logger.info("SchedulerService соединения закрыты")


# Глобальный экземпляр планировщика
_scheduler_service: Optional[SchedulerService] = None


async def get_scheduler_service() -> SchedulerService:
    """Получить глобальный экземпляр планировщика"""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
        await _scheduler_service.initialize()
    return _scheduler_service


async def start_background_scheduler(interval_seconds: int = 300):
    """Запустить планировщик в фоновом режиме"""
    scheduler = await get_scheduler_service()
    await scheduler.start_monitoring_scheduler(interval_seconds)
