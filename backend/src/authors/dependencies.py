"""
Зависимости для работы с авторами VK

Масштабируемая архитектура с правильным управлением зависимостями
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from ..database import get_db_session
from ..infrastructure.cache import get_redis_cache
from ..infrastructure.task_queue import get_celery_app
from .infrastructure.repositories import AuthorRepository
from .infrastructure.cache import AuthorRedisCache
from .infrastructure.task_queue import AuthorCeleryTaskQueue
from .application.services import AuthorService

logger = logging.getLogger(__name__)


async def get_author_repository_dependency(
    db: AsyncSession = Depends(get_db_session),
) -> AuthorRepository:
    """
    Получить репозиторий авторов через FastAPI dependency injection

    Args:
        db: Сессия БД из FastAPI dependency

    Returns:
        AuthorRepository: Репозиторий авторов
    """
    return AuthorRepository(db)


async def get_author_cache_dependency() -> Optional[AuthorRedisCache]:
    """
    Получить кэш авторов через FastAPI dependency injection

    Returns:
        Optional[AuthorRedisCache]: Кэш авторов или None
    """
    try:
        redis_client = await get_redis_cache()
        if redis_client:
            return AuthorRedisCache(redis_client)
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize author cache: {e}")
        return None


async def get_author_task_queue_dependency() -> Optional[AuthorCeleryTaskQueue]:
    """
    Получить очередь задач авторов через FastAPI dependency injection

    Returns:
        Optional[AuthorCeleryTaskQueue]: Очередь задач или None
    """
    try:
        celery_app = await get_celery_app()
        if celery_app:
            return AuthorCeleryTaskQueue(celery_app)
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize author task queue: {e}")
        return None


async def get_author_service_dependency(
    repository: AuthorRepository = Depends(get_author_repository_dependency),
    cache: Optional[AuthorRedisCache] = Depends(get_author_cache_dependency),
    task_queue: Optional[AuthorCeleryTaskQueue] = Depends(get_author_task_queue_dependency),
) -> AuthorService:
    """
    Получить сервис авторов через FastAPI dependency injection

    Args:
        repository: Репозиторий авторов из FastAPI dependency
        cache: Кэш авторов из FastAPI dependency
        task_queue: Очередь задач из FastAPI dependency

    Returns:
        AuthorService: Сервис авторов
    """
    return AuthorService(repository, cache, task_queue)
