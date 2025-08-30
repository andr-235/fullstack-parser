"""
Переделанный роутер health с новой архитектурой (DDD + Middleware)
"""

from typing import Dict, Any
from fastapi import APIRouter, Request, Depends
from ..application.health_service import HealthApplicationService
from ..handlers.common import create_success_response, create_error_response
from ..dependencies import CommonDB


router = APIRouter(prefix="/health", tags=["Health"])


# Dependency для Health Service
def get_health_service() -> HealthApplicationService:
    """Получить экземпляр Health Service"""
    return HealthApplicationService()


@router.get(
    "",
    summary="Basic Health Check",
    description="Базовая проверка состояния сервиса с новой архитектурой",
)
async def basic_health_check(
    request: Request,
    health_service: HealthApplicationService = Depends(get_health_service),
) -> Dict[str, Any]:
    """Базовая проверка здоровья системы"""
    try:
        health_status = await health_service.perform_basic_health_check()
        return await create_success_response(request, health_status.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "HEALTH_CHECK_FAILED",
            f"Failed to perform health check: {str(e)}",
        )


@router.get(
    "/detailed",
    summary="Detailed Health Check",
    description="Детальная проверка состояния с проверкой всех компонентов",
)
async def detailed_health_check(
    request: Request,
    health_service: HealthApplicationService = Depends(get_health_service),
) -> Dict[str, Any]:
    """Детальная проверка здоровья системы"""
    try:
        health_status = await health_service.perform_detailed_health_check()
        return await create_success_response(request, health_status.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "DETAILED_HEALTH_CHECK_FAILED",
            f"Failed to perform detailed health check: {str(e)}",
        )


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Проверка готовности для Kubernetes/контейнерной оркестрации",
)
async def readiness_check(
    request: Request,
    health_service: HealthApplicationService = Depends(get_health_service),
) -> Dict[str, Any]:
    """Проверка готовности системы"""
    try:
        health_status = await health_service.perform_readiness_check()
        return await create_success_response(request, health_status.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            503,
            "READINESS_CHECK_FAILED",
            f"Service is not ready: {str(e)}",
        )


@router.get(
    "/live",
    summary="Liveness Check",
    description="Проверка живости процесса для Kubernetes",
)
async def liveness_check(
    request: Request,
    health_service: HealthApplicationService = Depends(get_health_service),
) -> Dict[str, Any]:
    """Проверка живости процесса"""
    try:
        health_status = await health_service.perform_liveness_check()
        return await create_success_response(request, health_status.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            503,
            "LIVENESS_CHECK_FAILED",
            f"Process is not alive: {str(e)}",
        )


@router.get(
    "/status",
    summary="System Status Overview",
    description="Общая информация о статусе системы",
)
async def system_status(
    request: Request,
    health_service: HealthApplicationService = Depends(get_health_service),
) -> Dict[str, Any]:
    """Получить общую информацию о статусе системы"""
    try:
        # Выполняем детальную проверку
        health_status = await health_service.perform_detailed_health_check()

        # Добавляем дополнительную информацию
        status_info = {
            **health_status.to_dict(),
            "architecture": "DDD + Middleware (v1.6.0)",
            "features": [
                "Domain-Driven Design",
                "Application Services",
                "Rate Limiting",
                "Request Logging",
                "Standardized Responses",
            ],
        }

        return await create_success_response(request, status_info)
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "STATUS_CHECK_FAILED",
            f"Failed to get system status: {str(e)}",
        )
