"""
Сервис для модуля Health

Содержит бизнес-логику для проверки здоровья системы
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..exceptions import ServiceUnavailableError
from .models import HealthRepository, HealthStatus, HealthCheckResult
from .config import health_config
from .constants import (
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_UNHEALTHY,
    HEALTH_COMPONENT_DATABASE,
    HEALTH_COMPONENT_REDIS,
    HEALTH_COMPONENT_VK_API,
    HEALTH_COMPONENT_MEMORY,
    HEALTH_COMPONENT_DISK,
    HEALTH_COMPONENT_CPU,
    HEALTH_COMPONENT_PROCESS,
    MEMORY_CRITICAL_THRESHOLD,
    MEMORY_WARNING_THRESHOLD,
    DISK_CRITICAL_THRESHOLD,
    DISK_WARNING_THRESHOLD,
    CPU_CRITICAL_THRESHOLD,
    CPU_WARNING_THRESHOLD,
)


class HealthService:
    """
    Сервис для работы с проверками здоровья системы

    Реализует бизнес-логику для мониторинга здоровья системы
    и ее компонентов
    """

    def __init__(self, repository: HealthRepository = None):
        self.repository = repository or HealthRepository()
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.utcnow()

    async def perform_basic_health_check(self) -> HealthStatus:
        """
        Выполнить базовую проверку здоровья

        Returns:
            HealthStatus: Статус здоровья системы
        """
        health_status = HealthStatus()

        try:
            # Проверка компонентов
            await self._check_database(health_status)
            await self._check_redis(health_status)
            await self._check_vk_api(health_status)

            # Обновление общего статуса
            health_status.update_overall_status()
            health_status.uptime_seconds = int(
                (datetime.utcnow() - self.start_time).total_seconds()
            )

            # Сохраняем результат
            await self.repository.save_health_status(health_status)

        except Exception as e:
            self.logger.error(f"Error performing basic health check: {e}")
            health_status.status = HEALTH_STATUS_UNHEALTHY
            health_status.add_component_status("health_service", "unhealthy")

        return health_status

    async def perform_detailed_health_check(self) -> HealthStatus:
        """
        Выполнить детальную проверку здоровья

        Returns:
            HealthStatus: Детальный статус здоровья системы
        """
        health_status = await self.perform_basic_health_check()

        try:
            # Дополнительные проверки
            await self._check_memory_usage(health_status)
            await self._check_disk_space(health_status)
            await self._check_cpu_usage(health_status)

        except Exception as e:
            self.logger.error(f"Error performing detailed health check: {e}")
            health_status.status = HEALTH_STATUS_UNHEALTHY

        return health_status

    async def perform_readiness_check(self) -> HealthStatus:
        """
        Выполнить проверку готовности (readiness probe)

        Returns:
            HealthStatus: Статус готовности
        """
        health_status = HealthStatus(status="ready")

        try:
            # Критически важные компоненты
            db_result = await self._check_database_component()
            if not db_result.is_successful():
                health_status.status = "not_ready"
                health_status.add_component_status(
                    HEALTH_COMPONENT_DATABASE, "unhealthy"
                )

        except Exception as e:
            self.logger.error(f"Error performing readiness check: {e}")
            health_status.status = "not_ready"

        return health_status

    async def perform_liveness_check(self) -> HealthStatus:
        """
        Выполнить проверку живости (liveness probe)

        Returns:
            HealthStatus: Статус живости
        """
        health_status = HealthStatus(status="alive")

        try:
            # Простая проверка того, что процесс работает
            health_status.add_component_status(
                HEALTH_COMPONENT_PROCESS, "healthy"
            )
            health_status.uptime_seconds = int(
                (datetime.utcnow() - self.start_time).total_seconds()
            )

        except Exception as e:
            self.logger.error(f"Error performing liveness check: {e}")
            health_status.status = "dead"

        return health_status

    async def check_component_health(
        self, component: str
    ) -> HealthCheckResult:
        """
        Проверить здоровье конкретного компонента

        Args:
            component: Название компонента

        Returns:
            HealthCheckResult: Результат проверки
        """
        start_time = time.time()

        try:
            if component == HEALTH_COMPONENT_DATABASE:
                result = await self._check_database_component()
            elif component == HEALTH_COMPONENT_REDIS:
                result = await self._check_redis_component()
            elif component == HEALTH_COMPONENT_VK_API:
                result = await self._check_vk_api_component()
            elif component == HEALTH_COMPONENT_MEMORY:
                result = await self._check_memory_component()
            elif component == HEALTH_COMPONENT_DISK:
                result = await self._check_disk_component()
            elif component == HEALTH_COMPONENT_CPU:
                result = await self._check_cpu_component()
            else:
                result = HealthCheckResult(
                    component=component,
                    status="unknown",
                    error_message=f"Unknown component: {component}",
                )

            # Сохраняем результат
            await self.repository.save_check_result(result)
            await self.repository.save_component_status(
                component, result.status, result.response_time_ms
            )

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
        """
        Получить текущий статус здоровья

        Returns:
            Optional[HealthStatus]: Текущий статус или None
        """
        return await self.repository.get_health_status()

    async def get_component_status(
        self, component: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получить статус компонента

        Args:
            component: Название компонента

        Returns:
            Optional[Dict[str, Any]]: Статус компонента или None
        """
        return await self.repository.get_component_status(component)

    async def get_all_components_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Получить статусы всех компонентов

        Returns:
            Dict[str, Dict[str, Any]]: Статусы всех компонентов
        """
        return await self.repository.get_all_components_status()

    async def get_health_history(
        self, component: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Получить историю проверок здоровья

        Args:
            component: Фильтр по компоненту
            limit: Максимальное количество записей

        Returns:
            List[Dict[str, Any]]: История проверок
        """
        return await self.repository.get_check_history(component, limit)

    async def get_health_metrics(self) -> Dict[str, Any]:
        """
        Получить метрики здоровья

        Returns:
            Dict[str, Any]: Метрики здоровья
        """
        return await self.repository.get_health_metrics()

    async def get_health_summary(self) -> Dict[str, Any]:
        """
        Получить сводку по здоровью системы

        Returns:
            Dict[str, Any]: Сводка здоровья
        """
        return await self.repository.get_health_summary()

    async def export_health_data(self, format: str = "json") -> Dict[str, Any]:
        """
        Экспортировать данные здоровья

        Args:
            format: Формат экспорта

        Returns:
            Dict[str, Any]: Экспортированные данные
        """
        return await self.repository.export_health_data(format)

    async def clear_health_cache(self) -> bool:
        """
        Очистить кеш здоровья

        Returns:
            bool: True если кеш очищен успешно
        """
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
            health_status.add_component_status(
                HEALTH_COMPONENT_DATABASE, result.status
            )
        except Exception as e:
            self.logger.error(f"Database health check error: {e}")
            health_status.add_component_status(
                HEALTH_COMPONENT_DATABASE, "unhealthy"
            )

    async def _check_redis(self, health_status: HealthStatus) -> None:
        """Проверка Redis"""
        try:
            result = await self._check_redis_component()
            health_status.add_component_status(
                HEALTH_COMPONENT_REDIS, result.status
            )
        except Exception as e:
            self.logger.error(f"Redis health check error: {e}")
            health_status.add_component_status(
                HEALTH_COMPONENT_REDIS, "unknown"
            )

    async def _check_vk_api(self, health_status: HealthStatus) -> None:
        """Проверка VK API"""
        try:
            result = await self._check_vk_api_component()
            health_status.add_component_status(
                HEALTH_COMPONENT_VK_API, result.status
            )
        except Exception as e:
            self.logger.error(f"VK API health check error: {e}")
            health_status.add_component_status(
                HEALTH_COMPONENT_VK_API, "unknown"
            )

    async def _check_memory_usage(self, health_status: HealthStatus) -> None:
        """Проверка использования памяти"""
        try:
            result = await self._check_memory_component()
            health_status.add_component_status(
                HEALTH_COMPONENT_MEMORY, result.status
            )
        except Exception as e:
            self.logger.error(f"Memory health check error: {e}")
            health_status.add_component_status(
                HEALTH_COMPONENT_MEMORY, "unknown"
            )

    async def _check_disk_space(self, health_status: HealthStatus) -> None:
        """Проверка дискового пространства"""
        try:
            result = await self._check_disk_component()
            health_status.add_component_status(
                HEALTH_COMPONENT_DISK, result.status
            )
        except Exception as e:
            self.logger.error(f"Disk health check error: {e}")
            health_status.add_component_status(
                HEALTH_COMPONENT_DISK, "unknown"
            )

    async def _check_cpu_usage(self, health_status: HealthStatus) -> None:
        """Проверка загрузки CPU"""
        try:
            result = await self._check_cpu_component()
            health_status.add_component_status(
                HEALTH_COMPONENT_CPU, result.status
            )
        except Exception as e:
            self.logger.error(f"CPU health check error: {e}")
            health_status.add_component_status(HEALTH_COMPONENT_CPU, "unknown")

    async def _check_database_component(self) -> HealthCheckResult:
        """Проверка компонента базы данных"""
        start_time = time.time()

        try:
            # Импортируем сервис базы данных для проверки
            from ..database import get_db_session

            db = await get_db_session()
            # Выполняем простой запрос для проверки соединения
            result = await db.execute("SELECT 1")
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component=HEALTH_COMPONENT_DATABASE,
                status="healthy",
                response_time_ms=response_time,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=HEALTH_COMPONENT_DATABASE,
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )

    async def _check_redis_component(self) -> HealthCheckResult:
        """Проверка компонента Redis"""
        start_time = time.time()

        try:
            # В простой реализации возвращаем unknown
            # В продакшене здесь должна быть проверка Redis
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component=HEALTH_COMPONENT_REDIS,
                status="unknown",
                response_time_ms=response_time,
                error_message="Redis check not implemented",
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=HEALTH_COMPONENT_REDIS,
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )

    async def _check_vk_api_component(self) -> HealthCheckResult:
        """Проверка компонента VK API"""
        start_time = time.time()

        try:
            # В простой реализации возвращаем unknown
            # В продакшене здесь должна быть проверка VK API
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component=HEALTH_COMPONENT_VK_API,
                status="unknown",
                response_time_ms=response_time,
                error_message="VK API check not implemented",
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=HEALTH_COMPONENT_VK_API,
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

            if memory_usage_percent > MEMORY_CRITICAL_THRESHOLD:
                status = "critical"
            elif memory_usage_percent > MEMORY_WARNING_THRESHOLD:
                status = "warning"
            else:
                status = "healthy"

            return HealthCheckResult(
                component=HEALTH_COMPONENT_MEMORY,
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
                component=HEALTH_COMPONENT_MEMORY,
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

            if disk_usage_percent > DISK_CRITICAL_THRESHOLD:
                status = "critical"
            elif disk_usage_percent > DISK_WARNING_THRESHOLD:
                status = "warning"
            else:
                status = "healthy"

            return HealthCheckResult(
                component=HEALTH_COMPONENT_DISK,
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
                component=HEALTH_COMPONENT_DISK,
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

            if cpu_percent > CPU_CRITICAL_THRESHOLD:
                status = "critical"
            elif cpu_percent > CPU_WARNING_THRESHOLD:
                status = "warning"
            else:
                status = "healthy"

            return HealthCheckResult(
                component=HEALTH_COMPONENT_CPU,
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
                component=HEALTH_COMPONENT_CPU,
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
            )


# Экспорт
__all__ = [
    "HealthService",
]
