"""
Зависимости для модуля Comments

Определяет FastAPI зависимости для работы с комментариями
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session


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
):
    """
    Получить сервис парсера

    Args:
        repository: Репозиторий парсера
        client: Клиент VK API

    Returns:
        ParserService: Сервис для бизнес-логики парсинга
    """
    # Импорт здесь для избежания циклических зависимостей
    from .service import ParserService

    return ParserService(repository, client)


# Экспорт зависимостей
__all__ = [
    "get_parser_repository",
    "get_parser_client",
    "get_parser_service",
]
