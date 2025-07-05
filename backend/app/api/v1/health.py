from datetime import datetime

import redis.asyncio as aioredis
from app.core.config import settings
from app.core.database import get_async_session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/health", summary="Проверка состояния сервиса", tags=["Health"])
async def health_check(
    db: AsyncSession = Depends(get_async_session),
):
    """
    Комплексная проверка состояния сервиса и его зависимостей.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    # 1. Проверка базы данных
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"

    # 2. Проверка Redis
    redis_client = None
    try:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    finally:
        if redis_client:
            await redis_client.close()

    # 3. Дополнительные проверки (можно добавить в будущем)
    # Например, проверка доступности внешнего API (VK API)
    # try:
    #     ...
    #     health_status["services"]["vk_api"] = "healthy"
    # except Exception:
    #     health_status["services"]["vk_api"] = "unhealthy"
    #     health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
