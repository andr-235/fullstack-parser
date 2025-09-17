"""
Зависимости для модуля Keywords
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db_session
from keywords.models import KeywordsRepository
from keywords.service import KeywordsService


async def get_keywords_repository(
    db: AsyncSession = Depends(get_db_session),
) -> KeywordsRepository:
    """Получить репозиторий ключевых слов"""
    return KeywordsRepository(db)


async def get_keywords_service(
    repository: KeywordsRepository = Depends(get_keywords_repository),
) -> KeywordsService:
    """Получить сервис ключевых слов"""
    return KeywordsService(repository)
