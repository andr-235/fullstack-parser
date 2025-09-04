"""
Зависимости для модуля Keywords

Определяет FastAPI зависимости для управления ключевыми словами
"""

from typing import Optional
from fastapi import Depends

from .service import KeywordsService
from .models import KeywordsRepository, get_keywords_repository

# Глобальный экземпляр репозитория для сохранения данных между запросами
_keywords_repository: Optional[KeywordsRepository] = None


async def get_keywords_repository_singleton() -> KeywordsRepository:
    """
    Получить синглтон репозитория ключевых слов

    Returns:
        KeywordsRepository: Единственный экземпляр репозитория
    """
    global _keywords_repository
    if _keywords_repository is None:
        _keywords_repository = KeywordsRepository()
    return _keywords_repository


async def get_keywords_service(
    repository: KeywordsRepository = Depends(
        get_keywords_repository_singleton
    ),
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
