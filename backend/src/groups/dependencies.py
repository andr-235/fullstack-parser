"""
Зависимости для модуля Comments

Определяет FastAPI зависимости для работы с комментариями
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session


async def get_group_repository(db: AsyncSession = Depends(get_db_session)):
    """
    Получить репозиторий групп

    Args:
        db: Сессия базы данных

    Returns:
        GroupRepository: Репозиторий для работы с группами
    """
    # Импорт здесь для избежания циклических зависимостей
    from .models import GroupRepository

    return GroupRepository(db)


async def get_group_service(repository=Depends(get_group_repository)):
    """
    Получить сервис групп

    Args:
        repository: Репозиторий групп

    Returns:
        GroupService: Сервис для бизнес-логики групп
    """
    # Импорт здесь для избежания циклических зависимостей
    from .service import GroupService

    return GroupService(repository)


# Экспорт зависимостей
__all__ = [
    "get_group_repository",
    "get_group_service",
]
