"""
Исключения модуля Settings

Содержит специфические исключения для модуля управления настройками
"""

from ..exceptions import APIException


class SettingsError(APIException):
    """Общая ошибка модуля Settings"""

    def __init__(
        self,
        message: str,
        error_code: str = "SETTINGS_ERROR",
        details: dict = None,
    ):
        super().__init__(
            status_code=500,
            detail=message,
            error_code=error_code,
            extra_data=details or {},
        )


class SettingsSectionNotFoundError(APIException):
    """Секция настроек не найдена"""

    def __init__(self, section_name: str):
        super().__init__(
            status_code=404,
            detail=f"Settings section '{section_name}' not found",
            error_code="SETTINGS_SECTION_NOT_FOUND",
            extra_data={"section_name": section_name},
        )


class SettingsKeyNotFoundError(APIException):
    """Ключ настройки не найден"""

    def __init__(self, section_name: str, key: str):
        super().__init__(
            status_code=404,
            detail=f"Settings key '{section_name}.{key}' not found",
            error_code="SETTINGS_KEY_NOT_FOUND",
            extra_data={"section_name": section_name, "key": key},
        )


class SettingsValidationError(APIException):
    """Ошибка валидации настроек"""

    def __init__(self, message: str, validation_errors: dict = None):
        extra_data = {"message": message}
        if validation_errors:
            extra_data["validation_errors"] = validation_errors

        super().__init__(
            status_code=400,
            detail=message,
            error_code="SETTINGS_VALIDATION_ERROR",
            extra_data=extra_data,
        )


class SettingsUpdateError(APIException):
    """Ошибка обновления настроек"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=500,
            detail=message,
            error_code="SETTINGS_UPDATE_ERROR",
            extra_data=details or {},
        )


class SettingsAccessDeniedError(APIException):
    """Отказано в доступе к настройкам"""

    def __init__(
        self, message: str = "Access denied to settings", details: dict = None
    ):
        super().__init__(
            status_code=403,
            detail=message,
            error_code="SETTINGS_ACCESS_DENIED",
            extra_data=details or {},
        )


class SettingsReadonlyError(APIException):
    """Попытка изменения настройки только для чтения"""

    def __init__(self, section_name: str, key: str = None):
        message = f"Settings section '{section_name}' is read-only"
        if key:
            message = f"Settings key '{section_name}.{key}' is read-only"

        extra_data = {"section_name": section_name}
        if key:
            extra_data["key"] = key

        super().__init__(
            status_code=403,
            detail=message,
            error_code="SETTINGS_READONLY_ERROR",
            extra_data=extra_data,
        )


class SettingsCriticalSectionError(APIException):
    """Попытка изменения критической секции без админ прав"""

    def __init__(self, section_name: str):
        super().__init__(
            status_code=403,
            detail=f"Settings section '{section_name}' is critical and requires admin privileges",
            error_code="SETTINGS_CRITICAL_SECTION_ERROR",
            extra_data={"section_name": section_name},
        )


class SettingsImportError(APIException):
    """Ошибка импорта настроек"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=400,
            detail=message,
            error_code="SETTINGS_IMPORT_ERROR",
            extra_data=details or {},
        )


class SettingsExportError(APIException):
    """Ошибка экспорта настроек"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=500,
            detail=message,
            error_code="SETTINGS_EXPORT_ERROR",
            extra_data=details or {},
        )


class SettingsCacheError(APIException):
    """Ошибка кеширования настроек"""

    def __init__(self, message: str, operation: str = None):
        extra_data = {"message": message}
        if operation:
            extra_data["operation"] = operation

        super().__init__(
            status_code=500,
            detail=f"Settings cache error: {message}",
            error_code="SETTINGS_CACHE_ERROR",
            extra_data=extra_data,
        )


class SettingsSizeLimitError(APIException):
    """Превышен лимит размера настроек"""

    def __init__(self, current_size: int, max_size: int):
        super().__init__(
            status_code=413,
            detail=f"Settings size limit exceeded: {current_size} > {max_size}",
            error_code="SETTINGS_SIZE_LIMIT_ERROR",
            extra_data={"current_size": current_size, "max_size": max_size},
        )


class SettingsSectionLimitError(APIException):
    """Превышен лимит количества секций"""

    def __init__(self, current_count: int, max_count: int):
        super().__init__(
            status_code=413,
            detail=f"Settings sections limit exceeded: {current_count} > {max_count}",
            error_code="SETTINGS_SECTION_LIMIT_ERROR",
            extra_data={
                "current_count": current_count,
                "max_count": max_count,
            },
        )


class SettingsValueLimitError(APIException):
    """Превышен лимит количества значений в секции"""

    def __init__(self, section_name: str, current_count: int, max_count: int):
        super().__init__(
            status_code=413,
            detail=f"Settings values limit exceeded in section '{section_name}': {current_count} > {max_count}",
            error_code="SETTINGS_VALUE_LIMIT_ERROR",
            extra_data={
                "section_name": section_name,
                "current_count": current_count,
                "max_count": max_count,
            },
        )


class SettingsAuditError(APIException):
    """Ошибка аудита настроек"""

    def __init__(self, message: str, operation: str = None):
        extra_data = {"message": message}
        if operation:
            extra_data["operation"] = operation

        super().__init__(
            status_code=500,
            detail=f"Settings audit error: {message}",
            error_code="SETTINGS_AUDIT_ERROR",
            extra_data=extra_data,
        )


class SettingsMetricsError(APIException):
    """Ошибка метрик настроек"""

    def __init__(self, message: str, metric: str = None):
        extra_data = {"message": message}
        if metric:
            extra_data["metric"] = metric

        super().__init__(
            status_code=500,
            detail=f"Settings metrics error: {message}",
            error_code="SETTINGS_METRICS_ERROR",
            extra_data=extra_data,
        )


class SettingsBackupError(APIException):
    """Ошибка резервного копирования настроек"""

    def __init__(self, message: str, operation: str = None):
        extra_data = {"message": message}
        if operation:
            extra_data["operation"] = operation

        super().__init__(
            status_code=500,
            detail=f"Settings backup error: {message}",
            error_code="SETTINGS_BACKUP_ERROR",
            extra_data=extra_data,
        )


class SettingsRestoreError(APIException):
    """Ошибка восстановления настроек"""

    def __init__(self, message: str, backup_id: str = None):
        extra_data = {"message": message}
        if backup_id:
            extra_data["backup_id"] = backup_id

        super().__init__(
            status_code=500,
            detail=f"Settings restore error: {message}",
            error_code="SETTINGS_RESTORE_ERROR",
            extra_data=extra_data,
        )


# Экспорт всех исключений
__all__ = [
    "SettingsError",
    "SettingsSectionNotFoundError",
    "SettingsKeyNotFoundError",
    "SettingsValidationError",
    "SettingsUpdateError",
    "SettingsAccessDeniedError",
    "SettingsReadonlyError",
    "SettingsCriticalSectionError",
    "SettingsImportError",
    "SettingsExportError",
    "SettingsCacheError",
    "SettingsSizeLimitError",
    "SettingsSectionLimitError",
    "SettingsValueLimitError",
    "SettingsAuditError",
    "SettingsMetricsError",
    "SettingsBackupError",
    "SettingsRestoreError",
]
