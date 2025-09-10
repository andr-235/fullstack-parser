"""
Зависимости для модуля Keywords

Определяет FastAPI зависимости для управления ключевыми словами
"""

from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import KeywordsService
from .models import KeywordsRepository, get_keywords_repository
from ..database import get_db_session


async def get_keywords_repository(
    db: AsyncSession = Depends(get_db_session),
) -> KeywordsRepository:
    """
    Получить репозиторий ключевых слов с сессией БД

    Args:
        db: Сессия базы данных

    Returns:
        KeywordsRepository: Репозиторий ключевых слов
    """
    return KeywordsRepository(db)


async def get_keywords_service(
    repository: KeywordsRepository = Depends(get_keywords_repository),
) -> KeywordsService:
    """
    Получить сервис ключевых слов

    Args:
        repository: Репозиторий ключевых слов

    Returns:
        KeywordsService: Сервис ключевых слов
    """
    return KeywordsService(repository)


# Экспорт зависимостей
__all__ = [
    "get_keywords_service",
]
