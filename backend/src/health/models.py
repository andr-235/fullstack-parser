"""
Модели для модуля Health
"""

from datetime import datetime
from typing import Any, Dict, Optional


class HealthStatus:
    """Статус здоровья системы"""

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

    def add_component_status(self, component: str, status: str) -> None:
        """Добавить статус компонента"""
        self.components[component] = status

    def update_overall_status(self) -> None:
        """Обновить общий статус на основе компонентов"""
        unhealthy = [s for s in self.components.values() if s not in ["healthy", "ready", "alive"]]

        if not unhealthy:
            self.status = "healthy"
        elif len(unhealthy) == len(self.components):
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
    """Результат проверки компонента"""

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
    """Репозиторий для работы с данными здоровья"""

    def __init__(self):
        self._cache = {}
        self._history = []

    async def save_health_status(self, health_status: HealthStatus) -> None:
        """Сохранить статус здоровья"""
        self._cache["system_health"] = {
            "status": health_status.to_dict(),
            "saved_at": datetime.utcnow().isoformat(),
        }

    async def get_health_status(self) -> Optional[HealthStatus]:
        """Получить статус здоровья"""
        cached_data = self._cache.get("system_health")
        if not cached_data:
            return None

        status_data = cached_data["status"]
        return HealthStatus(
            status=status_data["status"],
            service_name=status_data["service"],
            version=status_data["version"],
            components=status_data["components"],
            uptime_seconds=status_data.get("uptime_seconds"),
        )

    async def save_check_result(self, result: HealthCheckResult) -> None:
        """Сохранить результат проверки"""
        self._history.append(result.to_dict())
        if len(self._history) > 100:
            self._history = self._history[-100:]

    async def get_check_history(self, component: Optional[str] = None, limit: int = 50) -> list:
        """Получить историю проверок"""
        history = self._history[::-1]

        if component:
            history = [item for item in history if item["component"] == component]

        return history[:limit]

    async def get_health_metrics(self) -> Dict[str, Any]:
        """Получить метрики здоровья"""
        total_checks = len(self._history)
        successful_checks = sum(
            1 for check in self._history
            if check["status"] in ["healthy", "ready", "alive"]
        )
        failed_checks = total_checks - successful_checks

        response_times = [
            check["response_time_ms"] for check in self._history
            if check["response_time_ms"] is not None
        ]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": failed_checks,
            "success_rate": successful_checks / total_checks if total_checks > 0 else 0,
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def clear_cache(self) -> None:
        """Очистить кеш"""
        self._cache.clear()
        self._history.clear()


__all__ = ["HealthStatus", "HealthCheckResult", "HealthRepository"]
