"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, backref
Модели для модуля Health

Определяет модели данных для проверки здоровья системы
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..database import get_db_session
from .config import health_config


class HealthStatus:
    """
    Модель статуса здоровья системы

    Представляет текущее состояние здоровья системы и ее компонентов
    """

    def __init__(
        self,
        status: str = "healthy",
        service_name: str = "vk-comments-parser",
        version: str = "1.0.0",
        components: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
        uptime_seconds: Optional[int] = None,
    ):
        self.status = status
        self.service_name = service_name
        self.version = version
        self.components = components or {}
        self.timestamp = timestamp or datetime.utcnow()
        self.uptime_seconds = uptime_seconds

    def is_healthy(self) -> bool:
        """Проверить, является ли система здоровой"""
        return self.status == "healthy"

    def is_degraded(self) -> bool:
        """Проверить, является ли система degraded"""
        return self.status == "degraded"

    def is_unhealthy(self) -> bool:
        """Проверить, является ли система нездоровой"""
        return self.status == "unhealthy"

    def add_component_status(self, component: str, status: str) -> None:
        """Добавить статус компонента"""
        self.components[component] = status

    def get_unhealthy_components(self) -> Dict[str, str]:
        """Получить нездоровые компоненты"""
        return {
            component: status
            for component, status in self.components.items()
            if status not in ["healthy", "ready", "alive"]
        }

    def update_overall_status(self) -> None:
        """Обновить общий статус на основе компонентов"""
        unhealthy_components = self.get_unhealthy_components()

        if not unhealthy_components:
            self.status = "healthy"
        elif len(unhealthy_components) == len(self.components):
            self.status = "unhealthy"
        else:
            self.status = "degraded"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "status": self.status,
            "service": self.service_name,
            "version": self.version,
            "components": self.components,
            "timestamp": self.timestamp.isoformat(),
            "uptime_seconds": self.uptime_seconds,
        }


class HealthCheckResult:
    """
    Модель результата проверки здоровья компонента

    Содержит информацию о результате проверки конкретного компонента
    """

    def __init__(
        self,
        component: str,
        status: str,
        response_time_ms: Optional[float] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.component = component
        self.status = status
        self.response_time_ms = response_time_ms
        self.error_message = error_message
        self.details = details or {}
        self.checked_at = datetime.utcnow()

    def is_successful(self) -> bool:
        """Проверить, успешен ли результат"""
        return self.status in ["healthy", "ready", "alive"]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "component": self.component,
            "status": self.status,
            "response_time_ms": self.response_time_ms,
            "error_message": self.error_message,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
        }


class HealthRepository:
    """
    Репозиторий для работы с данными здоровья системы

    Предоставляет интерфейс для хранения и получения данных о здоровье
    """

    def __init__(self, db=None):
        self.db = db
        # In-memory кеш для простоты (в продакшене использовать Redis)
        self._health_cache = {}
        self._history = []

    async def get_db(self):
        """Получить сессию БД"""
        return self.db or get_db_session()

    async def save_health_status(self, health_status: HealthStatus) -> None:
        """
        Сохранить статус здоровья системы

        Args:
            health_status: Статус здоровья для сохранения
        """
        # В простой реализации сохраняем только в кеш
        cache_key = "system_health"
        self._health_cache[cache_key] = {
            "status": health_status.to_dict(),
            "saved_at": datetime.utcnow().isoformat(),
        }

    async def get_health_status(self) -> Optional[HealthStatus]:
        """
        Получить статус здоровья системы

        Returns:
            Optional[HealthStatus]: Статус здоровья или None
        """
        cache_key = "system_health"
        cached_data = self._health_cache.get(cache_key)

        if cached_data:
            status_data = cached_data["status"]
            return HealthStatus(
                status=status_data["status"],
                service_name=status_data["service"],
                version=status_data["version"],
                components=status_data["components"],
                uptime_seconds=status_data.get("uptime_seconds"),
            )

        return None

    async def save_check_result(self, result: HealthCheckResult) -> None:
        """
        Сохранить результат проверки здоровья

        Args:
            result: Результат проверки для сохранения
        """
        # Сохраняем в историю (последние 100 результатов)
        self._history.append(result.to_dict())
        if len(self._history) > 100:
            self._history = self._history[-100:]

    async def get_check_history(
        self, component: Optional[str] = None, limit: int = 50
    ) -> list:
        """
        Получить историю проверок здоровья

        Args:
            component: Фильтр по компоненту
            limit: Максимальное количество результатов

        Returns:
            list: История проверок
        """
        history = self._history[::-1]  # Новые сначала

        if component:
            history = [
                item for item in history if item["component"] == component
            ]

        return history[:limit]

    async def save_component_status(
        self,
        component: str,
        status: str,
        response_time_ms: Optional[float] = None,
    ) -> None:
        """
        Сохранить статус компонента

        Args:
            component: Название компонента
            status: Статус компонента
            response_time_ms: Время ответа в мс
        """
        cache_key = f"component:{component}"
        self._health_cache[cache_key] = {
            "status": status,
            "response_time_ms": response_time_ms,
            "updated_at": datetime.utcnow().isoformat(),
        }

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
        cache_key = f"component:{component}"
        return self._health_cache.get(cache_key)

    async def get_all_components_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Получить статусы всех компонентов

        Returns:
            Dict[str, Dict[str, Any]]: Статусы всех компонентов
        """
        components_status = {}
        for key, value in self._health_cache.items():
            if key.startswith("component:"):
                component_name = key.replace("component:", "")
                components_status[component_name] = value

        return components_status

    async def clear_cache(self) -> None:
        """Очистить кеш здоровья"""
        self._health_cache.clear()
        self._history.clear()

    async def get_health_metrics(self) -> Dict[str, Any]:
        """
        Получить метрики здоровья системы

        Returns:
            Dict[str, Any]: Метрики здоровья
        """
        total_checks = len(self._history)
        successful_checks = sum(
            1
            for check in self._history
            if check["status"] in ["healthy", "ready", "alive"]
        )
        failed_checks = total_checks - successful_checks

        response_times = [
            check["response_time_ms"]
            for check in self._history
            if check["response_time_ms"] is not None
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        return {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": failed_checks,
            "success_rate": (
                successful_checks / total_checks if total_checks > 0 else 0
            ),
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_health_summary(self) -> Dict[str, Any]:
        """
        Получить сводку по здоровью системы

        Returns:
            Dict[str, Any]: Сводка здоровья
        """
        health_status = await self.get_health_status()
        components_status = await self.get_all_components_status()
        metrics = await self.get_health_metrics()

        unhealthy_components = {}
        if health_status:
            for component, status in health_status.components.items():
                if status not in ["healthy", "ready", "alive"]:
                    unhealthy_components[component] = status

        return {
            "overall_status": (
                health_status.status if health_status else "unknown"
            ),
            "total_components": len(components_status),
            "healthy_components": len(components_status)
            - len(unhealthy_components),
            "unhealthy_components": unhealthy_components,
            "last_check": (
                health_status.timestamp.isoformat() if health_status else None
            ),
            "uptime_seconds": (
                health_status.uptime_seconds if health_status else None
            ),
            "metrics": metrics,
        }

    async def export_health_data(self, format: str = "json") -> Dict[str, Any]:
        """
        Экспортировать данные здоровья

        Args:
            format: Формат экспорта

        Returns:
            Dict[str, Any]: Экспортированные данные
        """
        health_status = await self.get_health_status()
        components_status = await self.get_all_components_status()
        history = await self.get_check_history(limit=50)
        metrics = await self.get_health_metrics()

        return {
            "export_format": format,
            "exported_at": datetime.utcnow().isoformat(),
            "health_status": (
                health_status.to_dict() if health_status else None
            ),
            "components_status": components_status,
            "recent_history": history,
            "metrics": metrics,
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить здоровье репозитория

        Returns:
            Dict[str, Any]: Результат проверки здоровья
        """
        try:
            cache_size = len(self._health_cache)
            history_size = len(self._history)
            last_check = None

            if self._history:
                last_check = self._history[-1]["checked_at"]

            return {
                "status": "healthy",
                "cache_entries": cache_size,
                "history_entries": history_size,
                "last_check": last_check,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Функции для создания репозитория
async def get_health_repository(db=None) -> HealthRepository:
    """Создать репозиторий здоровья"""
    return HealthRepository(db)


# Экспорт
__all__ = [
    "HealthStatus",
    "HealthCheckResult",
    "HealthRepository",
    "get_health_repository",
]
