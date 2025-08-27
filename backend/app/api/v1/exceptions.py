"""
Общие исключения для API v1

Этот модуль содержит кастомные исключения, используемые
в различных API эндпоинтах.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Базовое исключение для API ошибок."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}


class ValidationError(APIException):
    """Ошибка валидации данных."""

    def __init__(
        self,
        detail: str,
        field: Optional[str] = None,
        error_code: str = "VALIDATION_ERROR",
    ):
        extra_data = {"field": field} if field else {}
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            extra_data=extra_data,
        )


class NotFoundError(APIException):
    """Ресурс не найден."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        error_code: str = "NOT_FOUND",
    ):
        detail = f"{resource_type} с ID {resource_id} не найден"
        extra_data = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
            extra_data=extra_data,
        )


class ConflictError(APIException):
    """Конфликт данных."""

    def __init__(self, detail: str, error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
        )


class UnauthorizedError(APIException):
    """Ошибка авторизации."""

    def __init__(
        self,
        detail: str = "Требуется авторизация",
        error_code: str = "UNAUTHORIZED",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
        )


class ForbiddenError(APIException):
    """Ошибка доступа."""

    def __init__(
        self, detail: str = "Доступ запрещен", error_code: str = "FORBIDDEN"
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
        )


class RateLimitError(APIException):
    """Превышен лимит запросов."""

    def __init__(
        self,
        detail: str = "Превышен лимит запросов",
        retry_after: Optional[int] = None,
        error_code: str = "RATE_LIMIT_EXCEEDED",
    ):
        extra_data = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code,
            extra_data=extra_data,
        )


class ServiceUnavailableError(APIException):
    """Сервис недоступен."""

    def __init__(
        self,
        detail: str = "Сервис временно недоступен",
        error_code: str = "SERVICE_UNAVAILABLE",
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code,
        )


def create_error_response(error: APIException) -> Dict[str, Any]:
    """
    Создает стандартизированный ответ об ошибке.

    Args:
        error: Исключение API

    Returns:
        Dict[str, Any]: Стандартизированный ответ об ошибке
    """
    response = {
        "error": {
            "code": error.error_code or "UNKNOWN_ERROR",
            "message": error.detail,
            "status_code": error.status_code,
        }
    }

    if error.extra_data:
        response["error"]["details"] = error.extra_data

    return response
