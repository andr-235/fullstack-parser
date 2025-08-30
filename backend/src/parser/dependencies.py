"""
Зависимости для модуля Comments

Определяет FastAPI зависимости для работы с комментариями
"""

from typing import AsyncGenerator, Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..vk_api.dependencies import create_vk_api_service
from ..vk_api.service import VKAPIService


async def get_parser_repository(db: AsyncSession = Depends(get_db_session)):
    """
    Получить репозиторий парсера

    Args:
        db: Сессия базы данных

    Returns:
        ParserRepository: Репозиторий для работы с парсингом
    """
    # Импорт здесь для избежания циклических зависимостей
    from .models import ParserRepository

    return ParserRepository(db)


async def get_parser_client():
    """
    Получить клиент VK API

    Returns:
        VKAPIClient: Клиент для работы с VK API
    """
    # Импорт здесь для избежания циклических зависимостей
    from .client import VKAPIClient

    return VKAPIClient()


async def get_parser_service(
    repository=Depends(get_parser_repository),
    client=Depends(get_parser_client),
    vk_api_service=None,
):
    """
    Получить сервис парсера

    Args:
        repository: Репозиторий парсера
        client: Клиент VK API
        vk_api_service: VK API сервис (опционально)

    Returns:
        ParserService: Сервис для бизнес-логики парсинга
    """
    # Импорт здесь для избежания циклических зависимостей
    from .service import ParserService

    # Если VK API сервис не передан, создаем его
    if vk_api_service is None:
        vk_api_service = create_vk_api_service()

    return ParserService(repository, client, vk_api_service)


# Экспорт зависимостей
__all__ = [
    "get_parser_repository",
    "get_parser_client",
    "get_parser_service",
]
