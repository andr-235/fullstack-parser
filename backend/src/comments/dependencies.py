"""
Зависимости для модуля Comments

Определяет FastAPI зависимости для работы с комментариями
"""

from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from .interfaces import (
    CommentRepositoryInterface,
    CommentServiceInterface,
    CacheServiceInterface,
    LoggerInterface,
)
from .repository import CommentRepository
from .service import CommentService


async def get_comment_repository(
    db: AsyncSession = Depends(get_db_session),
) -> CommentRepositoryInterface:
    """
    Получить репозиторий комментариев

    Args:
        db: Сессия базы данных

    Returns:
        CommentRepositoryInterface: Репозиторий для работы с комментариями
    """
    return CommentRepository(db)


async def get_cache_service() -> Optional[CacheServiceInterface]:
    """
    Получить сервис кеширования

    Returns:
        CacheServiceInterface: Сервис кеширования или None
    """
    try:
        from ..infrastructure import cache_service

        return cache_service
    except ImportError:
        return None


async def get_logger() -> Optional[LoggerInterface]:
    """
    Получить логгер

    Returns:
        LoggerInterface: Логгер или None
    """
    try:
        from ..infrastructure.logging import get_loguru_logger

        return get_loguru_logger("comments")
    except ImportError:
        return None


async def get_comment_service(
    repository: CommentRepositoryInterface = Depends(get_comment_repository),
    cache_service: Optional[CacheServiceInterface] = Depends(
        get_cache_service
    ),
    logger: Optional[LoggerInterface] = Depends(get_logger),
) -> CommentServiceInterface:
    """
    Получить сервис комментариев

    Args:
        repository: Репозиторий комментариев
        cache_service: Сервис кеширования
        logger: Логгер

    Returns:
        CommentServiceInterface: Сервис для бизнес-логики комментариев
    """
    return CommentService(
        repository=repository, cache_service=cache_service, logger=logger
    )


# Экспорт зависимостей
__all__ = [
    "get_comment_repository",
    "get_comment_service",
    "get_cache_service",
    "get_logger",
]
