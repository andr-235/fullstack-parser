"""
Улучшенные схемы ошибок для API v1
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class APIError(HTTPException):
    """Базовый класс для API ошибок"""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
    ):
        self.error_code = error_code
        self.details = details or {}
        self.field = field

        super().__init__(status_code=status_code, detail=message)


class ValidationError(APIError):
    """Ошибка валидации"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details,
            field=field,
        )


class NotFoundError(APIError):
    """Ресурс не найден"""

    def __init__(self, resource: str, resource_id: Optional[Any] = None):
        message = f"{resource} not found"
        if resource_id is not None:
            message += f" with id {resource_id}"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
            details={"resource": resource, "resource_id": resource_id},
        )


class RateLimitError(APIError):
    """Превышен лимит запросов"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Try again later.",
            details={"retry_after": retry_after},
        )
