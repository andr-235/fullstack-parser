"""
Сервис для модуля Health
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil

from health.config import health_config
from health.models import HealthCheckResult, HealthRepository, HealthStatus


class HealthService:
    """Сервис для работы с проверками здоровья системы"""

    def __init__(self, repository: HealthRepository = None):
        self.repository = repository or HealthRepository()
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.utcnow()

    async def perform_basic_health_check(self) -> HealthStatus:
        """Выполнить базовую проверку здоровья"""
        health_status = HealthStatus()

        try:
            # Проверка критических компонентов
            await self._check_database(health_status)

            # Обновление общего статуса
            health_status.update_overall_status()
            health_status.uptime_seconds = int(
                (datetime.utcnow() - self.start_time).total_seconds()
            )

            # Сохраняем результат
            await self.repository.save_health_status(health_status)

        except Exception as e:
            self.logger.error(f"Error performing basic health check: {e}")
            health_status.status = "unhealthy"
            health_status.add_component_status("health_service", "unhealthy")

        return health_status

    async def perform_detailed_health_check(self) -> HealthStatus:
        """Выполнить детальную проверку здоровья"""
        health_status = await self.perform_basic_health_check()

        try:
            # Дополнительные проверки
            await self._check_memory(health_status)
            await self._check_disk(health_status)
            await self._check_cpu(health_status)

            # Обновляем статус после всех проверок
            health_status.update_overall_status()

        except Exception as e:
            self.logger.error(f"Error performing detailed health check: {e}")
            health_status.status = "unhealthy"

        return health_status

    async def perform_readiness_check(self) -> HealthStatus:
        """Выполнить проверку готовности"""
        health_status = HealthStatus(status="ready")

        try:
            # Проверяем только критически важные компоненты
            db_result = await self._check_database_component()
            if not db_result.is_successful():
                health_status.status = "not_ready"
                health_status.add_component_status("database", "unhealthy")
            else:
                health_status.add_component_status("database", "healthy")

        except Exception as e:
            self.logger.error(f"Error performing readiness check: {e}")
            health_status.status = "not_ready"

        return health_status

    async def perform_liveness_check(self) -> HealthStatus:
        """Выполнить проверку живости"""
        health_status = HealthStatus(status="alive")

        try:
            # Простая проверка того, что процесс работает
            health_status.add_component_status("process", "healthy")
            health_status.uptime_seconds = int(
                (datetime.utcnow() - self.start_time).total_seconds()
            )

        except Exception as e:
            self.logger.error(f"Error performing liveness check: {e}")
            health_status.status = "dead"

        return health_status

    async def check_component_health(self, component: str) -> HealthCheckResult:
        """Проверить здоровье конкретного компонента"""
        start_time = time.time()

        try:
            if component == "database":
                result = await self._check_database_component()
            elif component == "memory":
                result = await self._check_memory_component()
            elif component == "disk":
                result = await self._check_disk_component()
            elif component == "cpu":
                result = await self._check_cpu_component()
            else:
                result = HealthCheckResult(
                    component=component,
                    status="unknown",
                    error_message=f"Unknown component: {component}",
                )

            # Сохраняем результат
            await self.repository.save_check_result(result)

            return result

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                component=component,
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )

            await self.repository.save_check_result(result)
            return result

    async def get_health_status(self) -> Optional[HealthStatus]:
        """Получить текущий статус здоровья"""
        return await self.repository.get_health_status()

    async def get_health_history(self, component: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю проверок здоровья"""
        return await self.repository.get_check_history(component, limit)

    async def get_health_metrics(self) -> Dict[str, Any]:
        """Получить метрики здоровья"""
        return await self.repository.get_health_metrics()

    async def clear_health_cache(self) -> bool:
        """Очистить кеш здоровья"""
        try:
            await self.repository.clear_cache()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing health cache: {e}")
            return False

    async def _check_database(self, health_status: HealthStatus) -> None:
        """Проверка базы данных"""
        try:
            result = await self._check_database_component()
            health_status.add_component_status("database", result.status)
        except Exception as e:
            self.logger.error(f"Database health check error: {e}")
            health_status.add_component_status("database", "unhealthy")

    async def _check_memory(self, health_status: HealthStatus) -> None:
        """Проверка памяти"""
        try:
            result = await self._check_memory_component()
            health_status.add_component_status("memory", result.status)
        except Exception as e:
            self.logger.error(f"Memory health check error: {e}")
            health_status.add_component_status("memory", "unknown")

    async def _check_disk(self, health_status: HealthStatus) -> None:
        """Проверка диска"""
        try:
            result = await self._check_disk_component()
            health_status.add_component_status("disk", result.status)
        except Exception as e:
            self.logger.error(f"Disk health check error: {e}")
            health_status.add_component_status("disk", "unknown")

    async def _check_cpu(self, health_status: HealthStatus) -> None:
        """Проверка CPU"""
        try:
            result = await self._check_cpu_component()
            health_status.add_component_status("cpu", result.status)
        except Exception as e:
            self.logger.error(f"CPU health check error: {e}")
            health_status.add_component_status("cpu", "unknown")

    async def _check_database_component(self) -> HealthCheckResult:
        """Проверка компонента базы данных"""
        start_time = time.time()

        try:
            from sqlalchemy import text

            from ..database import database_service

            async with database_service.get_session() as db:
                await db.execute(text("SELECT 1"))

            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="database",
                status="healthy",
                response_time_ms=response_time,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="database",
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )

    async def _check_memory_component(self) -> HealthCheckResult:
        """Проверка компонента памяти"""
        start_time = time.time()

        try:
            memory = psutil.virtual_memory()
            memory_usage_percent = memory.percent
            response_time = (time.time() - start_time) * 1000

            if memory_usage_percent > health_config.MEMORY_CRITICAL:
                status = "critical"
            elif memory_usage_percent > health_config.MEMORY_WARNING:
                status = "warning"
            else:
                status = "healthy"

            return HealthCheckResult(
                component="memory",
                status=status,
                response_time_ms=response_time,
                details={
                    "usage_percent": memory_usage_percent,
                    "total_mb": memory.total / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="memory",
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )

    async def _check_disk_component(self) -> HealthCheckResult:
        """Проверка компонента диска"""
        start_time = time.time()

        try:
            disk = psutil.disk_usage("/")
            disk_usage_percent = disk.percent
            response_time = (time.time() - start_time) * 1000

            if disk_usage_percent > health_config.DISK_CRITICAL:
                status = "critical"
            elif disk_usage_percent > health_config.DISK_WARNING:
                status = "warning"
            else:
                status = "healthy"

            return HealthCheckResult(
                component="disk",
                status=status,
                response_time_ms=response_time,
                details={
                    "usage_percent": disk_usage_percent,
                    "total_gb": disk.total / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="disk",
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )

    async def _check_cpu_component(self) -> HealthCheckResult:
        """Проверка компонента CPU"""
        start_time = time.time()

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            response_time = (time.time() - start_time) * 1000

            if cpu_percent > health_config.CPU_CRITICAL:
                status = "critical"
            elif cpu_percent > health_config.CPU_WARNING:
                status = "warning"
            else:
                status = "healthy"

            return HealthCheckResult(
                component="cpu",
                status=status,
                response_time_ms=response_time,
                details={
                    "usage_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="cpu",
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )


__all__ = ["HealthService"]
