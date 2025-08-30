"""
Зависимости для модуля Comments

Определяет FastAPI зависимости для работы с комментариями
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session


async def get_comment_repository(db: AsyncSession = Depends(get_db_session)):
    """
    Получить репозиторий комментариев

    Args:
        db: Сессия базы данных

    Returns:
        CommentRepository: Репозиторий для работы с комментариями
    """
    # Импорт здесь для избежания циклических зависимостей
    from .models import CommentRepository

    return CommentRepository(db)


async def get_comment_service(repository=Depends(get_comment_repository)):
    """
    Получить сервис комментариев

    Args:
        repository: Репозиторий комментариев

    Returns:
        CommentService: Сервис для бизнес-логики комментариев
    """
    # Импорт здесь для избежания циклических зависимостей
    from .service import CommentService

    return CommentService(repository)


# Экспорт зависимостей
__all__ = [
    "get_comment_repository",
    "get_comment_service",
]
