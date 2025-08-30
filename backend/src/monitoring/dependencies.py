"""
Зависимости для модуля Monitoring

Определяет FastAPI зависимости для мониторинга групп
"""

from typing import Optional
from fastapi import Depends

from .service import MonitoringService
from .models import MonitoringRepository, get_monitoring_repository


async def get_monitoring_service(
    repository: MonitoringRepository = Depends(get_monitoring_repository),
) -> MonitoringService:
    """
    Получить сервис мониторинга

    Args:
        repository: Репозиторий мониторинга

    Returns:
        MonitoringService: Сервис мониторинга
    """
    return MonitoringService(repository)


# Экспорт зависимостей
__all__ = [
    "get_monitoring_service",
]
