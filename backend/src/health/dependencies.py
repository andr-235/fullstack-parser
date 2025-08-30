"""
Зависимости для модуля Health

Определяет FastAPI зависимости для работы с проверками здоровья
"""

from fastapi import Depends

from .service import HealthService
from .models import get_health_repository


async def get_health_service() -> HealthService:
    """
    Получить сервис здоровья

    Returns:
        HealthService: Сервис здоровья
    """
    return HealthService()


# Экспорт зависимостей
__all__ = [
    "get_health_service",
]
