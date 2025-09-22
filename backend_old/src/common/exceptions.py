"""
Базовые исключения
"""

from typing import Optional


class APIException(Exception):
    """Базовое API исключение"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(APIException):
    """Ошибка валидации"""
    def __init__(self, message: str):
        super().__init__(message, 400)


class NotFoundError(APIException):
    """Ресурс не найден"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)
