"""
Исключения модуля Settings - упрощенная версия
"""

from common.exceptions import (
    APIException,
    NotFoundException,
    ValidationException,
)


class SettingsError(APIException):
    """Общая ошибка модуля Settings"""
    pass


class SettingsNotFoundError(NotFoundException):
    """Настройка не найдена"""
    pass


class SettingsValidationError(ValidationException):
    """Ошибка валидации настроек"""
    pass


__all__ = [
    "SettingsError",
    "SettingsNotFoundError",
    "SettingsValidationError",
]
