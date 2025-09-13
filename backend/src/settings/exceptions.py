"""
Исключения модуля Settings - упрощенная версия
"""

from common.exceptions import (
    APIException,
    NotFoundError,
    ValidationError,
)


class SettingsError(APIException):
    """Общая ошибка модуля Settings"""
    pass


class SettingsNotFoundError(NotFoundError):
    """Настройка не найдена"""
    pass


class SettingsValidationError(ValidationError):
    """Ошибка валидации настроек"""
    pass


__all__ = [
    "SettingsError",
    "SettingsNotFoundError",
    "SettingsValidationError",
]
