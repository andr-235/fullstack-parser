"""
Health check endpoints for monitoring system status.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from structlog import get_logger

from app.core.database import get_db
from app.core.cache import CacheService
from app.core.exceptions import ServiceUnavailableError
from redis.asyncio import Redis
from app.core.config import settings

logger = get_logger()

router = APIRouter()


async def get_redis_client() -> Redis:
    """Get Redis client for health checks."""
    return Redis.from_url(str(settings.redis.url), decode_responses=True)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Dict with health status
    """
    return {
        "status": "healthy",
        "service": "vk-comments-parser",
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health_check(
    db=Depends(get_db), redis_client: Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Detailed health check with database and cache status.

    Returns:
        Dict with detailed health status
    """
    health_status = {
        "status": "healthy",
        "service": "vk-comments-parser",
        "version": "1.0.0",
        "components": {"database": "unknown", "cache": "unknown"},
    }

    # Check database
    try:
        # Simple query to check database connectivity
        await db.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
        logger.debug("Database health check passed")
    except Exception as e:
        health_status["components"]["database"] = "unhealthy"
        health_status["database_error"] = str(e)
        logger.error("Database health check failed", error=str(e))

    # Check cache
    try:
        await redis_client.ping()
        health_status["components"]["cache"] = "healthy"
        logger.debug("Cache health check passed")
    except Exception as e:
        health_status["components"]["cache"] = "unhealthy"
        health_status["cache_error"] = str(e)
        logger.error("Cache health check failed", error=str(e))

    # Determine overall status
    if any(
        status == "unhealthy"
        for status in health_status["components"].values()
    ):
        health_status["status"] = "degraded"

    return health_status


@router.get("/health/ready")
async def readiness_check(
    db=Depends(get_db), redis_client: Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/container orchestration.

    Returns:
        Dict with readiness status
    """
    try:
        # Check database
        await db.execute("SELECT 1")

        # Check cache
        await redis_client.ping()

        return {"status": "ready", "service": "vk-comments-parser"}

    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise ServiceUnavailableError(f"Service not ready: {str(e)}")


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes/container orchestration.

    Returns:
        Dict with liveness status
    """
    return {"status": "alive", "service": "vk-comments-parser"}
