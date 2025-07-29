"""
Custom exceptions for VK Comments Parser backend.
Provides centralized error handling with structured logging support.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}


class VKAPIError(BaseAPIException):
    """Exception for VK API related errors."""

    def __init__(
        self,
        detail: str,
        vk_error_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"VK API Error: {detail}",
            error_code="VK_API_ERROR",
            context=context,
        )
        self.vk_error_code = vk_error_code


class DatabaseError(BaseAPIException):
    """Exception for database related errors."""

    def __init__(
        self,
        detail: str,
        db_error: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Error: {detail}",
            error_code="DATABASE_ERROR",
            context=context,
        )
        self.db_error = db_error


class CacheError(BaseAPIException):
    """Exception for Redis cache related errors."""

    def __init__(
        self,
        detail: str,
        cache_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache Error: {detail}",
            error_code="CACHE_ERROR",
            context=context,
        )
        self.cache_key = cache_key


class ValidationError(BaseAPIException):
    """Exception for data validation errors."""

    def __init__(
        self,
        detail: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation Error: {detail}",
            error_code="VALIDATION_ERROR",
            context=context,
        )
        self.field = field
        self.value = value


class RateLimitError(BaseAPIException):
    """Exception for rate limiting errors."""

    def __init__(
        self,
        detail: str,
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate Limit Error: {detail}",
            error_code="RATE_LIMIT_ERROR",
            context=context,
        )
        self.retry_after = retry_after


class ServiceUnavailableError(BaseAPIException):
    """Exception for service unavailable errors."""

    def __init__(
        self,
        detail: str,
        service: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service Unavailable: {detail}",
            error_code="SERVICE_UNAVAILABLE",
            context=context,
        )
        self.service = service
