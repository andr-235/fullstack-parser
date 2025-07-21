"""
API для управления настройками приложения
"""

from typing import Any, Dict

import structlog
from fastapi import APIRouter, HTTPException, status

from app.schemas.settings import SettingsResponse, SettingsUpdateRequest
from app.services.settings_service import get_settings_service

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    """Получить текущие настройки приложения"""
    try:
        settings_service = get_settings_service()
        current_settings = await settings_service.get_current_settings()

        logger.info("settings_loaded", user_id="system")
        return SettingsResponse(settings=current_settings)

    except Exception as e:
        logger.error("settings_load_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка загрузки настроек: {str(e)}",
        )


@router.put("/", response_model=SettingsResponse)
async def update_settings(request: SettingsUpdateRequest) -> SettingsResponse:
    """Обновить настройки приложения"""
    try:
        settings_service = get_settings_service()
        updated_settings = await settings_service.update_settings(request)

        logger.info(
            "settings_updated",
            user_id="system",
            sections=list(request.dict(exclude_none=True).keys()),
        )
        return SettingsResponse(
            settings=updated_settings, message="Настройки успешно обновлены"
        )

    except ValueError as e:
        logger.warning("settings_validation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации настроек: {str(e)}",
        )
    except Exception as e:
        logger.error("settings_update_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обновления настроек: {str(e)}",
        )


@router.post("/reset", response_model=SettingsResponse)
async def reset_settings() -> SettingsResponse:
    """Сбросить настройки к значениям по умолчанию"""
    try:
        settings_service = get_settings_service()
        default_settings = await settings_service.reset_to_defaults()

        logger.info("settings_reset", user_id="system")
        return SettingsResponse(
            settings=default_settings,
            message="Настройки сброшены к значениям по умолчанию",
        )

    except Exception as e:
        logger.error("settings_reset_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сброса настроек: {str(e)}",
        )


@router.get("/health", response_model=Dict[str, Any])
async def get_settings_health() -> Dict[str, Any]:
    """Проверить состояние настроек"""
    try:
        settings_service = get_settings_service()
        health_status = await settings_service.get_health_status()

        return {
            "status": "healthy",
            "settings_valid": health_status["valid"],
            "database_connected": health_status["database_connected"],
            "redis_connected": health_status["redis_connected"],
            "vk_api_accessible": health_status["vk_api_accessible"],
            "last_check": health_status["last_check"],
        }

    except Exception as e:
        logger.error("settings_health_check_error", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "settings_valid": False,
            "database_connected": False,
            "redis_connected": False,
            "vk_api_accessible": False,
        }
