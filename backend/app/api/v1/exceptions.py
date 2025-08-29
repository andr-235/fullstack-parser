"""
Общие исключения для API v1 с DDD архитектурой

Этот модуль содержит кастомные исключения, используемые
в различных API эндпоинтах. Интегрирован с новой системой
обработки ошибок и handlers.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status, Request


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
    Создает стандартизированный ответ об ошибке (устаревший метод).

    Args:
        error: Исключение API

    Returns:
        Dict[str, Any]: Стандартизированный ответ об ошибке

    Note:
        Этот метод устарел. Используйте create_error_response из handlers.common
        для полной интеграции с DDD архитектурой.
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


async def create_standard_error_response(
    request: Request, error: APIException, field: Optional[str] = None
) -> Dict[str, Any]:
    """
    Создает стандартизированный ответ об ошибке с DDD архитектурой.

    Args:
        request: FastAPI Request объект
        error: Исключение API
        field: Поле, вызвавшее ошибку (опционально)

    Returns:
        Dict[str, Any]: Стандартизированный ответ об ошибке

    Note:
        Использует новую систему handlers для полной интеграции с DDD архитектурой.
    """
    from .handlers.common import (
        create_error_response as create_handler_error_response,
    )

    details = error.extra_data or {}
    if field:
        details["field"] = field

    return await create_handler_error_response(
        request,
        error.status_code,
        error.error_code or "UNKNOWN_ERROR",
        error.detail,
        details,
    )


def handle_api_exception(error: APIException) -> Dict[str, Any]:
    """
    Обрабатывает API исключение и возвращает стандартизированный ответ.

    Args:
        error: Исключение API

    Returns:
        Dict[str, Any]: Стандартизированный ответ об ошибке

    Note:
        Утилитная функция для быстрой обработки исключений.
        Для полной интеграции с DDD архитектурой используйте create_standard_error_response.
    """
    return create_error_response(error)
