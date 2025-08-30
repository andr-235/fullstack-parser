"""
Зависимости для модуля VK API

Определяет FastAPI зависимости для работы с VK API
"""

from typing import Optional
from fastapi import Depends

from .service import VKAPIService
from .models import VKAPIRepository, get_vk_api_repository


async def get_vk_api_service(
    repository: VKAPIRepository = Depends(get_vk_api_repository),
) -> VKAPIService:
    """
    Получить сервис VK API

    Args:
        repository: Репозиторий VK API

    Returns:
        VKAPIService: Сервис VK API
    """
    return VKAPIService(repository)


# Экспорт зависимостей
__all__ = [
    "get_vk_api_service",
]
