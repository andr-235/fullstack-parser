import logging

import redis.asyncio as aioredis
from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthCheck
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=HealthCheck,
    summary="Проверка состояния сервиса",
    tags=["Health"],
)
async def health_check(
    db: AsyncSession = Depends(get_db),
):
    """
    Проверяет доступность сервиса и его зависимостей
    (например, базы данных и Redis).
    """
    health_status = HealthCheck(status="ok", services={})

    # Проверка базы данных
    try:
        await db.execute(text("SELECT 1"))
        health_status.services["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status.services["database"] = "error"
        health_status.status = "error"

    # Проверка Redis
    try:
        logger.info(f"Attempting Redis connection to: {settings.redis_url}")
        redis = await aioredis.from_url(str(settings.redis_url))
        await redis.ping()
        health_status.services["redis"] = "ok"
        await redis.aclose()
        logger.info("Redis health check successful")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status.services["redis"] = "error"
        health_status.status = "error"

    return health_status
