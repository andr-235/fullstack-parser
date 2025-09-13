"""
Роутер для модуля Health
"""

from typing import Optional

from fastapi import APIRouter, Depends

from health.dependencies import get_health_service
from health.schemas import HealthCheckResult, HealthMetrics, HealthResponse
from health.service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="Basic Health Check")
async def basic_health_check(
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Базовая проверка здоровья системы"""
    health_status = await health_service.perform_basic_health_check()
    return HealthResponse(
        status=health_status.status,
        service=health_status.service_name,
        version=health_status.version,
        components=health_status.components,
        timestamp=health_status.timestamp.isoformat(),
        uptime_seconds=health_status.uptime_seconds,
    )


@router.get("/detailed", response_model=HealthResponse, summary="Detailed Health Check")
async def detailed_health_check(
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Детальная проверка здоровья системы"""
    health_status = await health_service.perform_detailed_health_check()
    return HealthResponse(
        status=health_status.status,
        service=health_status.service_name,
        version=health_status.version,
        components=health_status.components,
        timestamp=health_status.timestamp.isoformat(),
        uptime_seconds=health_status.uptime_seconds,
    )


@router.get("/ready", response_model=HealthResponse, summary="Readiness Check")
async def readiness_check(
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Проверка готовности системы"""
    health_status = await health_service.perform_readiness_check()
    return HealthResponse(
        status=health_status.status,
        service=health_status.service_name,
        version=health_status.version,
        components=health_status.components,
        timestamp=health_status.timestamp.isoformat(),
        uptime_seconds=health_status.uptime_seconds,
    )


@router.get("/live", response_model=HealthResponse, summary="Liveness Check")
async def liveness_check(
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Проверка живости процесса"""
    health_status = await health_service.perform_liveness_check()
    return HealthResponse(
        status=health_status.status,
        service=health_status.service_name,
        version=health_status.version,
        components=health_status.components,
        timestamp=health_status.timestamp.isoformat(),
        uptime_seconds=health_status.uptime_seconds,
    )


@router.get("/component/{component}", response_model=HealthCheckResult, summary="Component Health Check")
async def check_component(
    component: str,
    health_service: HealthService = Depends(get_health_service),
) -> HealthCheckResult:
    """Проверить здоровье конкретного компонента"""
    result = await health_service.check_component_health(component)
    return HealthCheckResult(
        component=result.component,
        status=result.status,
        response_time_ms=result.response_time_ms,
        error_message=result.error_message,
        details=result.details,
        checked_at=result.checked_at.isoformat(),
    )


@router.get("/history", summary="Health History")
async def get_health_history(
    component: Optional[str] = None,
    limit: int = 50,
    health_service: HealthService = Depends(get_health_service),
):
    """Получить историю проверок здоровья"""
    history = await health_service.get_health_history(component, limit)
    return {"history": history, "total": len(history)}


@router.get("/metrics", response_model=HealthMetrics, summary="Health Metrics")
async def get_health_metrics(
    health_service: HealthService = Depends(get_health_service),
) -> HealthMetrics:
    """Получить метрики здоровья"""
    metrics = await health_service.get_health_metrics()
    return HealthMetrics(**metrics)


@router.delete("/cache", summary="Clear Health Cache")
async def clear_health_cache(
    health_service: HealthService = Depends(get_health_service),
):
    """Очистить кеш здоровья"""
    success = await health_service.clear_health_cache()
    return {"success": success, "message": "Cache cleared" if success else "Failed to clear cache"}
