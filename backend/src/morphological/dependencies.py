"""
Зависимости для модуля Morphological

Определяет FastAPI зависимости для морфологического анализа
"""

from typing import Optional
from fastapi import Depends

from .service import MorphologicalService
from .models import MorphologicalRepository, get_morphological_repository


async def get_morphological_service(
    repository: MorphologicalRepository = Depends(
        get_morphological_repository
    ),
) -> MorphologicalService:
    """
    Получить сервис морфологического анализа

    Args:
        repository: Репозиторий морфологического анализа

    Returns:
        MorphologicalService: Сервис морфологического анализа
    """
    return MorphologicalService(repository)


# Экспорт зависимостей
__all__ = [
    "get_morphological_service",
]
