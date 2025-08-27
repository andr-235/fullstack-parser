"""
Health check endpoints for monitoring system status.

Этот модуль предоставляет эндпоинты для проверки состояния
системы, включая проверку базы данных и кеша.
"""

from typing import Any, Dict, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from structlog import get_logger

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ServiceUnavailableError

logger = get_logger()

router = APIRouter()


async def get_redis_client() -> Redis:
    """
    Получить Redis клиент для health checks.

    Returns:
        Redis: Redis клиент для проверки состояния кеша
    """
    return Redis.from_url(str(settings.redis.url), decode_responses=True)


@router.get(
    "/health",
    summary="Basic Health Check",
    description="Базовая проверка состояния сервиса",
    response_description="Статус здоровья сервиса",
)
async def health_check() -> Dict[str, Any]:
    """
    Базовая проверка состояния сервиса.

    Returns:
        Dict[str, Any]: Словарь с базовой информацией о состоянии сервиса
    """
    return {
        "status": "healthy",
        "service": "vk-comments-parser",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z",  # TODO: Добавить реальное время
    }


@router.get(
    "/health/",
    summary="Basic Health Check (with trailing slash)",
    description="Базовая проверка состояния сервиса с trailing slash",
    response_description="Статус здоровья сервиса",
)
async def health_check_trailing_slash() -> Dict[str, Any]:
    """
    Базовая проверка состояния сервиса с trailing slash.
    Алиас для основного health endpoint.

    Returns:
        Dict[str, Any]: Словарь с базовой информацией о состоянии сервиса
    """
    return {
        "status": "healthy",
        "service": "vk-comments-parser",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z",  # TODO: Добавить реальное время
    }


@router.get(
    "/health/detailed",
    summary="Detailed Health Check",
    description="Детальная проверка состояния с проверкой компонентов",
    response_description="Детальная информация о состоянии всех компонентов",
)
async def detailed_health_check(
    db=Depends(get_db), redis_client: Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Детальная проверка состояния с проверкой базы данных и кеша.

    Args:
        db: Сессия базы данных
        redis_client: Redis клиент для проверки кеша

    Returns:
        Dict[str, Any]: Словарь с детальной информацией о состоянии компонентов

    Raises:
        HTTPException: При критических ошибках компонентов
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "service": "vk-comments-parser",
        "version": "1.0.0",
        "components": {"database": "unknown", "cache": "unknown"},
        "timestamp": "2024-01-01T00:00:00Z",  # TODO: Добавить реальное время
    }

    # Проверка базы данных
    try:
        # Простой запрос для проверки подключения к БД
        await db.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
        logger.debug("Database health check passed")
    except Exception as e:
        health_status["components"]["database"] = "unhealthy"
        health_status["database_error"] = str(e)
        logger.error("Database health check failed", error=str(e))

    # Проверка кеша
    try:
        await redis_client.ping()
        health_status["components"]["cache"] = "healthy"
        logger.debug("Cache health check passed")
    except Exception as e:
        health_status["components"]["cache"] = "unhealthy"
        health_status["cache_error"] = str(e)
        logger.error("Cache health check failed", error=str(e))

    # Определение общего статуса
    unhealthy_components = [
        status
        for status in health_status["components"].values()
        if status == "unhealthy"
    ]

    if unhealthy_components:
        health_status["status"] = "degraded"
        if len(unhealthy_components) == len(health_status["components"]):
            health_status["status"] = "unhealthy"
            # Если все компоненты нездоровы, возвращаем ошибку
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="All system components are unhealthy",
            )

    return health_status


@router.get(
    "/health/ready",
    summary="Readiness Check",
    description="Проверка готовности для Kubernetes/контейнерной оркестрации",
    response_description="Статус готовности сервиса",
)
async def readiness_check(
    db=Depends(get_db), redis_client: Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Проверка готовности для Kubernetes/контейнерной оркестрации.

    Этот эндпоинт используется для проверки готовности сервиса
    к обработке запросов.

    Args:
        db: Сессия базы данных
        redis_client: Redis клиент для проверки кеша

    Returns:
        Dict[str, Any]: Словарь с информацией о готовности сервиса

    Raises:
        HTTPException: При неготовности сервиса
    """
    try:
        # Проверка базы данных
        await db.execute("SELECT 1")

        # Проверка кеша
        await redis_client.ping()

        return {
            "status": "ready",
            "service": "vk-comments-parser",
            "version": "1.0.0",
            "message": "Service is ready to handle requests",
            "timestamp": "2024-01-01T00:00:00Z",  # TODO: Добавить реальное время
        }

    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready to handle requests",
        )


@router.get(
    "/health/live",
    summary="Liveness Check",
    description="Проверка жизнеспособности процесса",
    response_description="Статус жизнеспособности процесса",
)
async def liveness_check() -> Dict[str, Any]:
    """
    Проверка жизнеспособности процесса.

    Этот эндпоинт используется для проверки того, что процесс
    все еще работает и не завис.

    Returns:
        Dict[str, Any]: Словарь с информацией о жизнеспособности процесса
    """
    return {
        "status": "alive",
        "service": "vk-comments-parser",
        "version": "1.0.0",
        "pid": "12345",  # TODO: Добавить реальный PID
        "timestamp": "2024-01-01T00:00:00Z",  # TODO: Добавить реальное время
    }
