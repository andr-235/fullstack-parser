"""
Переделанный роутер settings с новой архитектурой (DDD + Middleware)
"""

from typing import Dict, Any
from fastapi import APIRouter, Request, Depends
from .service import SettingsService
from ..handlers import create_success_response, create_error_response


router = APIRouter(prefix="/settings", tags=["Settings"])


# Dependency для Settings Service
def get_settings_service() -> SettingsService:
    """Получить экземпляр Settings Service"""
    return SettingsService()


@router.get(
    "",
    summary="Get Current Settings",
    description="Получить текущие настройки приложения",
)
async def get_settings(
    request: Request,
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Получить текущие настройки системы"""
    try:
        settings = await settings_service.get_current_settings()
        return await create_success_response(request, settings)
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SETTINGS_LOAD_FAILED",
            f"Failed to load settings: {str(e)}",
        )


@router.put(
    "",
    summary="Update Settings",
    description="Обновить настройки приложения",
)
async def update_settings(
    request: Request,
    updates: Dict[str, Any],
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Обновить настройки системы"""
    try:
        updated_settings = await settings_service.update_settings(updates)
        return await create_success_response(
            request,
            updated_settings,
            None,  # pagination
            {"message": "Настройки успешно обновлены"},  # meta
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SETTINGS_UPDATE_FAILED",
            f"Failed to update settings: {str(e)}",
        )


@router.post(
    "/reset",
    summary="Reset Settings to Defaults",
    description="Сбросить настройки к значениям по умолчанию",
)
async def reset_settings(
    request: Request,
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Сбросить настройки к значениям по умолчанию"""
    try:
        default_settings = await settings_service.reset_to_defaults()
        return await create_success_response(
            request,
            default_settings,
            None,  # pagination
            {"message": "Настройки сброшены к значениям по умолчанию"},  # meta
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SETTINGS_RESET_FAILED",
            f"Failed to reset settings: {str(e)}",
        )


@router.get(
    "/section/{section_name}",
    summary="Get Settings Section",
    description="Получить секцию настроек по имени",
)
async def get_settings_section(
    request: Request,
    section_name: str,
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Получить секцию настроек"""
    try:
        section = await settings_service.get_section(section_name)
        if not section:
            return await create_error_response(
                request,
                404,
                "SECTION_NOT_FOUND",
                f"Settings section '{section_name}' not found",
            )

        return await create_success_response(
            request,
            {
                "name": section.name,
                "values": section.values,
                "description": section.description,
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SECTION_LOAD_FAILED",
            f"Failed to load settings section: {str(e)}",
        )


@router.put(
    "/section/{section_name}",
    summary="Update Settings Section",
    description="Обновить секцию настроек",
)
async def update_settings_section(
    request: Request,
    section_name: str,
    values: Dict[str, Any],
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Обновить секцию настроек"""
    try:
        updated_settings = await settings_service.update_section(
            section_name, values
        )
        return await create_success_response(
            request,
            updated_settings,
            None,  # pagination
            {"message": f"Секция '{section_name}' успешно обновлена"},  # meta
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SECTION_UPDATE_FAILED",
            f"Failed to update settings section: {str(e)}",
        )


@router.get(
    "/value/{section_name}/{key}",
    summary="Get Setting Value",
    description="Получить значение настройки",
)
async def get_setting_value(
    request: Request,
    section_name: str,
    key: str,
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Получить значение настройки"""
    try:
        value = await settings_service.get_setting_value(section_name, key)
        if value is None:
            return await create_error_response(
                request,
                404,
                "SETTING_NOT_FOUND",
                f"Setting '{section_name}.{key}' not found",
            )

        return await create_success_response(
            request, {"section": section_name, "key": key, "value": value}
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SETTING_LOAD_FAILED",
            f"Failed to load setting value: {str(e)}",
        )


@router.put(
    "/value/{section_name}/{key}",
    summary="Set Setting Value",
    description="Установить значение настройки",
)
async def set_setting_value(
    request: Request,
    section_name: str,
    key: str,
    value: Any,
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Установить значение настройки"""
    try:
        updated_settings = await settings_service.set_setting_value(
            section_name, key, value
        )
        return await create_success_response(
            request,
            updated_settings,
            None,  # pagination
            {
                "message": f"Настройка '{section_name}.{key}' успешно установлена"
            },  # meta
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SETTING_UPDATE_FAILED",
            f"Failed to update setting value: {str(e)}",
        )


@router.get(
    "/health",
    summary="Settings Health Check",
    description="Проверить состояние настроек",
)
async def get_settings_health(
    request: Request,
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Проверить состояние настроек"""
    try:
        health_status = await settings_service.get_health_status()
        return await create_success_response(request, health_status)
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "HEALTH_CHECK_FAILED",
            f"Failed to check settings health: {str(e)}",
        )


@router.post(
    "/validate",
    summary="Validate Settings",
    description="Валидировать настройки системы",
)
async def validate_settings(
    request: Request,
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Валидировать настройки системы"""
    try:
        validation_result = await settings_service.validate_settings()
        return await create_success_response(request, validation_result)
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "VALIDATION_FAILED",
            f"Failed to validate settings: {str(e)}",
        )
