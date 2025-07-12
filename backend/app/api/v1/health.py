import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthCheck

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheck,
    summary="Проверка состояния сервиса",
    tags=["Health"],
)
async def health_check(
    db: AsyncSession = Depends(get_db),
):
    """
    Проверяет доступность сервиса и его зависимостей (например, базы данных и Redis).
    """
    health_status = HealthCheck(status="ok", services={})

    # Проверка базы данных
    try:
        await db.execute(text("SELECT 1"))
        health_status.services["database"] = "ok"
    except Exception:
        health_status.services["database"] = "error"
        health_status.status = "error"

    # Проверка Redis
    try:
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        health_status.services["redis"] = "ok"
        await redis.close()
    except Exception:
        health_status.services["redis"] = "error"
        health_status.status = "error"

    return health_status
