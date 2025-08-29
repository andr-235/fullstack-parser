"""
Application Service для системы мониторинга здоровья (DDD)
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import time
import psutil
from ..domain.health import HealthStatus, HealthCheckResult
from .base import ApplicationService


class HealthApplicationService(ApplicationService):
    """Application Service для работы с мониторингом здоровья системы"""

    def __init__(
        self, database_checker=None, redis_checker=None, vk_api_checker=None
    ):
        self.database_checker = database_checker
        self.redis_checker = redis_checker
        self.vk_api_checker = vk_api_checker
        self.start_time = datetime.utcnow()

    async def perform_basic_health_check(self) -> HealthStatus:
        """Выполнить базовую проверку здоровья"""
        health_status = HealthStatus()

        # Проверка компонентов
        await self._check_database(health_status)
        await self._check_redis(health_status)
        await self._check_vk_api(health_status)

        # Обновление общего статуса
        health_status.update_overall_status()
        health_status.uptime_seconds = int(
            (datetime.utcnow() - self.start_time).total_seconds()
        )

        return health_status

    async def perform_detailed_health_check(self) -> HealthStatus:
        """Выполнить детальную проверку здоровья"""
        health_status = await self.perform_basic_health_check()

        # Дополнительные проверки
        await self._check_memory_usage(health_status)
        await self._check_disk_space(health_status)
        await self._check_cpu_usage(health_status)

        return health_status

    async def perform_readiness_check(self) -> HealthStatus:
        """Выполнить проверку готовности (readiness probe)"""
        health_status = HealthStatus(status="ready")

        # Критически важные компоненты
        db_result = await self._check_database_component()
        if not db_result.is_successful():
            health_status.status = "not_ready"
            health_status.add_component_status("database", "unhealthy")

        return health_status

    async def perform_liveness_check(self) -> HealthStatus:
        """Выполнить проверку живости (liveness probe)"""
        health_status = HealthStatus(status="alive")

        # Простая проверка того, что процесс работает
        health_status.add_component_status("process", "healthy")
        health_status.uptime_seconds = int(
            (datetime.utcnow() - self.start_time).total_seconds()
        )

        return health_status

    async def _check_database(self, health_status: HealthStatus) -> None:
        """Проверка базы данных"""
        try:
            if self.database_checker:
                result = await self.database_checker.check_health()
                health_status.add_component_status("database", result.status)
            else:
                # Базовая проверка
                health_status.add_component_status("database", "unknown")
        except Exception as e:
            health_status.add_component_status("database", "unhealthy")

    async def _check_redis(self, health_status: HealthStatus) -> None:
        """Проверка Redis"""
        try:
            if self.redis_checker:
                result = await self.redis_checker.check_health()
                health_status.add_component_status("redis", result.status)
            else:
                health_status.add_component_status("redis", "unknown")
        except Exception as e:
            health_status.add_component_status("redis", "unhealthy")

    async def _check_vk_api(self, health_status: HealthStatus) -> None:
        """Проверка VK API"""
        try:
            if self.vk_api_checker:
                result = await self.vk_api_checker.check_health()
                health_status.add_component_status("vk_api", result.status)
            else:
                health_status.add_component_status("vk_api", "unknown")
        except Exception as e:
            health_status.add_component_status("vk_api", "unhealthy")

    async def _check_memory_usage(self, health_status: HealthStatus) -> None:
        """Проверка использования памяти"""
        try:
            memory = psutil.virtual_memory()
            memory_usage_percent = memory.percent

            if memory_usage_percent > 90:
                health_status.add_component_status("memory", "critical")
            elif memory_usage_percent > 80:
                health_status.add_component_status("memory", "warning")
            else:
                health_status.add_component_status("memory", "healthy")

        except Exception:
            health_status.add_component_status("memory", "unknown")

    async def _check_disk_space(self, health_status: HealthStatus) -> None:
        """Проверка дискового пространства"""
        try:
            disk = psutil.disk_usage("/")
            disk_usage_percent = disk.percent

            if disk_usage_percent > 95:
                health_status.add_component_status("disk", "critical")
            elif disk_usage_percent > 85:
                health_status.add_component_status("disk", "warning")
            else:
                health_status.add_component_status("disk", "healthy")

        except Exception:
            health_status.add_component_status("disk", "unknown")

    async def _check_cpu_usage(self, health_status: HealthStatus) -> None:
        """Проверка загрузки CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > 95:
                health_status.add_component_status("cpu", "critical")
            elif cpu_percent > 80:
                health_status.add_component_status("cpu", "warning")
            else:
                health_status.add_component_status("cpu", "healthy")

        except Exception:
            health_status.add_component_status("cpu", "unknown")

    async def _check_database_component(self) -> HealthCheckResult:
        """Проверка компонента базы данных"""
        start_time = time.time()
        try:
            if self.database_checker:
                await self.database_checker.check_health()
                response_time = (time.time() - start_time) * 1000
                return HealthCheckResult(
                    component="database",
                    status="healthy",
                    response_time_ms=response_time,
                )
            else:
                return HealthCheckResult(
                    component="database",
                    status="unknown",
                    error_message="Database checker not configured",
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="database",
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )
