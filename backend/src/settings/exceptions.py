"""
Исключения модуля Settings

Содержит специфические исключения для модуля управления настройками
"""

from ..exceptions import APIError as APIException


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
            error_code=error_code,
            message=message,
            details=details or {},
        )


class SettingsSectionNotFoundError(APIException):
    """Секция настроек не найдена"""

    def __init__(self, section_name: str):
        super().__init__(
            status_code=404,
            error_code="SETTINGS_SECTION_NOT_FOUND",
            message=f"Settings section '{section_name}' not found",
            details={"section_name": section_name},
        )


class SettingsKeyNotFoundError(APIException):
    """Ключ настройки не найден"""

    def __init__(self, section_name: str, key: str):
        super().__init__(
            status_code=404,
            error_code="SETTINGS_KEY_NOT_FOUND",
            message=f"Settings key '{section_name}.{key}' not found",
            details={"section_name": section_name, "key": key},
        )


class SettingsValidationError(APIException):
    """Ошибка валидации настроек"""

    def __init__(self, message: str, validation_errors: dict = None):
        details = {"message": message}
        if validation_errors:
            details["validation_errors"] = validation_errors

        super().__init__(
            status_code=400,
            error_code="SETTINGS_VALIDATION_ERROR",
            message=message,
            details=details,
        )


class SettingsUpdateError(APIException):
    """Ошибка обновления настроек"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=500,
            error_code="SETTINGS_UPDATE_ERROR",
            message=message,
            details=details or {},
        )


class SettingsAccessDeniedError(APIException):
    """Отказано в доступе к настройкам"""

    def __init__(
        self, message: str = "Access denied to settings", details: dict = None
    ):
        super().__init__(
            status_code=403,
            error_code="SETTINGS_ACCESS_DENIED",
            message=message,
            details=details or {},
        )


class SettingsReadonlyError(APIException):
    """Попытка изменения настройки только для чтения"""

    def __init__(self, section_name: str, key: str = None):
        message = f"Settings section '{section_name}' is read-only"
        if key:
            message = f"Settings key '{section_name}.{key}' is read-only"

        details = {"section_name": section_name}
        if key:
            details["key"] = key

        super().__init__(
            status_code=403,
            error_code="SETTINGS_READONLY_ERROR",
            message=message,
            details=details,
        )


class SettingsCriticalSectionError(APIException):
    """Попытка изменения критической секции без админ прав"""

    def __init__(self, section_name: str):
        super().__init__(
            status_code=403,
            error_code="SETTINGS_CRITICAL_SECTION_ERROR",
            message=f"Settings section '{section_name}' is critical and requires admin privileges",
            details={"section_name": section_name},
        )


class SettingsImportError(APIException):
    """Ошибка импорта настроек"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=400,
            message=message,
            error_code="SETTINGS_IMPORT_ERROR",
            details=details or {},
        )


class SettingsExportError(APIException):
    """Ошибка экспорта настроек"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=500,
            message=message,
            error_code="SETTINGS_EXPORT_ERROR",
            details=details or {},
        )


class SettingsCacheError(APIException):
    """Ошибка кеширования настроек"""

    def __init__(self, message: str, operation: str = None):
        details = {"message": message}
        if operation:
            details["operation"] = operation

        super().__init__(
            status_code=500,
            message=f"Settings cache error: {message}",
            error_code="SETTINGS_CACHE_ERROR",
            details=details,
        )


class SettingsSizeLimitError(APIException):
    """Превышен лимит размера настроек"""

    def __init__(self, current_size: int, max_size: int):
        super().__init__(
            status_code=413,
            message=f"Settings size limit exceeded: {current_size} > {max_size}",
            error_code="SETTINGS_SIZE_LIMIT_ERROR",
            details={"current_size": current_size, "max_size": max_size},
        )


class SettingsSectionLimitError(APIException):
    """Превышен лимит количества секций"""

    def __init__(self, current_count: int, max_count: int):
        super().__init__(
            status_code=413,
            message=f"Settings sections limit exceeded: {current_count} > {max_count}",
            error_code="SETTINGS_SECTION_LIMIT_ERROR",
            details={
                "current_count": current_count,
                "max_count": max_count,
            },
        )


class SettingsValueLimitError(APIException):
    """Превышен лимит количества значений в секции"""

    def __init__(self, section_name: str, current_count: int, max_count: int):
        super().__init__(
            status_code=413,
            message=f"Settings values limit exceeded in section '{section_name}': {current_count} > {max_count}",
            error_code="SETTINGS_VALUE_LIMIT_ERROR",
            details={
                "section_name": section_name,
                "current_count": current_count,
                "max_count": max_count,
            },
        )


class SettingsAuditError(APIException):
    """Ошибка аудита настроек"""

    def __init__(self, message: str, operation: str = None):
        details = {"message": message}
        if operation:
            details["operation"] = operation

        super().__init__(
            status_code=500,
            message=f"Settings audit error: {message}",
            error_code="SETTINGS_AUDIT_ERROR",
            details=details,
        )


class SettingsMetricsError(APIException):
    """Ошибка метрик настроек"""

    def __init__(self, message: str, metric: str = None):
        details = {"message": message}
        if metric:
            details["metric"] = metric

        super().__init__(
            status_code=500,
            message=f"Settings metrics error: {message}",
            error_code="SETTINGS_METRICS_ERROR",
            details=details,
        )


class SettingsBackupError(APIException):
    """Ошибка резервного копирования настроек"""

    def __init__(self, message: str, operation: str = None):
        details = {"message": message}
        if operation:
            details["operation"] = operation

        super().__init__(
            status_code=500,
            message=f"Settings backup error: {message}",
            error_code="SETTINGS_BACKUP_ERROR",
            details=details,
        )


class SettingsRestoreError(APIException):
    """Ошибка восстановления настроек"""

    def __init__(self, message: str, backup_id: str = None):
        details = {"message": message}
        if backup_id:
            details["backup_id"] = backup_id

        super().__init__(
            status_code=500,
            message=f"Settings restore error: {message}",
            error_code="SETTINGS_RESTORE_ERROR",
            details=details,
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
