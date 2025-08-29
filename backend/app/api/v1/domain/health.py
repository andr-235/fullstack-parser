"""
Domain сущности для системы мониторинга здоровья (DDD)
"""

from datetime import datetime
from typing import Dict, Any, Optional
from .base import ValueObject


class HealthStatus(ValueObject):
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
            if status != "healthy"
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


class HealthCheckResult(ValueObject):
    """Результат проверки здоровья компонента"""

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
        return self.status == "healthy"
