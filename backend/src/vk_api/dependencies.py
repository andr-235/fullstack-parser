"""
Фабрика для создания VK API сервиса

Простая фабрика для создания экземпляров VKAPIService для внутреннего использования
"""

from typing import Optional

from .service import VKAPIService
from .models import VKAPIRepository, get_vk_api_repository


def create_vk_api_service_sync(
    repository: Optional[VKAPIRepository] = None,
) -> VKAPIService:
    """
    Создать экземпляр VK API сервиса (синхронная версия)

    Args:
        repository: Репозиторий VK API (опционально)

    Returns:
        VKAPIService: Экземпляр сервиса
    """
    if repository is None:
        # Создаем репозиторий синхронно для внутреннего использования
        from .models import VKAPIRepository

        repository = VKAPIRepository()

    return VKAPIService(repository)


async def create_vk_api_service(
    repository: Optional[VKAPIRepository] = None,
) -> VKAPIService:
    """
    Создать экземпляр VK API сервиса (асинхронная версия)

    Args:
        repository: Репозиторий VK API (опционально)

    Returns:
        VKAPIService: Экземпляр сервиса
    """
    if repository is None:
        repository = await get_vk_api_repository()

    return VKAPIService(repository)


# Экспорт функций
__all__ = [
    "create_vk_api_service",
    "create_vk_api_service_sync",
]
