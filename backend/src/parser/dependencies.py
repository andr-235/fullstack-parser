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
        None: Репозиторий удален, используется TaskManager
    """
    # TaskRepository удален, используется TaskManager в service.py
    return None


async def get_parser_vk_api_service():
    """
    Получить VK API сервис

    Returns:
        VKAPIService: Сервис для работы с VK API
    """
    return await create_vk_api_service()


# Глобальный экземпляр сервиса парсера для сохранения состояния задач
_parser_service_instance = None


async def get_parser_service(
    repository=Depends(get_parser_repository),
    vk_api_service=Depends(get_parser_vk_api_service),
):
    """
    Получить сервис парсера (синглтон)

    Args:
        repository: Репозиторий парсера
        vk_api_service: VK API сервис

    Returns:
        ParserService: Сервис для бизнес-логики парсинга
    """
    global _parser_service_instance

    # Создаем экземпляр только один раз
    if _parser_service_instance is None:
        # Импорт здесь для избежания циклических зависимостей
        from .service import ParserService

        _parser_service_instance = ParserService(repository, vk_api_service)

    return _parser_service_instance


# Экспорт зависимостей
__all__ = [
    "get_parser_repository",
    "get_parser_vk_api_service",
    "get_parser_service",
]
