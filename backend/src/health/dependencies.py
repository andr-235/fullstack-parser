"""
Зависимости для модуля Health
"""

from health.service import HealthService


def get_health_service() -> HealthService:
    """Получить сервис здоровья"""
    return HealthService()


__all__ = ["get_health_service"]
