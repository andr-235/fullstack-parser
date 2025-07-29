"""
Centralized error handlers for VK Comments Parser backend.
Provides structured logging and unified error responses.
"""

import traceback

from fastapi import Request, status
from fastapi.responses import JSONResponse
from structlog import get_logger

from .exceptions import (
    BaseAPIException,
    CacheError,
    DatabaseError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
    VKAPIError,
)

logger = get_logger()


async def base_exception_handler(
    request: Request, exc: BaseAPIException
) -> JSONResponse:
    """Handle custom API exceptions with structured logging."""

    # Prepare error context
    error_context = {
        "path": request.url.path,
        "method": request.method,
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "context": exc.context,
    }

    # Add specific context based on exception type
    if isinstance(exc, VKAPIError):
        error_context["vk_error_code"] = exc.vk_error_code
    elif isinstance(exc, DatabaseError):
        error_context["db_error"] = exc.db_error
    elif isinstance(exc, CacheError):
        error_context["cache_key"] = exc.cache_key
    elif isinstance(exc, ValidationError):
        error_context["field"] = exc.field
        error_context["value"] = exc.value
    elif isinstance(exc, RateLimitError):
        error_context["retry_after"] = exc.retry_after
    elif isinstance(exc, ServiceUnavailableError):
        error_context["service"] = exc.service

    # Log error with structured context
    logger.error(
        "API Error occurred", error_detail=exc.detail, **error_context
    )

    # Prepare response
    response_data = {
        "error": {
            "code": exc.error_code,
            "message": exc.detail,
            "status_code": exc.status_code,
        }
    }

    # Add retry information for rate limit errors
    if isinstance(exc, RateLimitError) and exc.retry_after:
        response_data["error"]["retry_after"] = exc.retry_after

    return JSONResponse(status_code=exc.status_code, content=response_data)


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle validation errors with detailed field information."""

    error_context = {
        "path": request.url.path,
        "method": request.method,
        "field": exc.field,
        "value": exc.value,
        "context": exc.context,
    }

    logger.warning(
        "Validation error occurred", error_detail=exc.detail, **error_context
    )

    response_data = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": exc.detail,
            "status_code": status.HTTP_400_BAD_REQUEST,
            "field": exc.field,
            "value": exc.value,
        }
    }

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=response_data
    )


async def vk_api_exception_handler(
    request: Request, exc: VKAPIError
) -> JSONResponse:
    """Handle VK API errors with retry information."""

    error_context = {
        "path": request.url.path,
        "method": request.method,
        "vk_error_code": exc.vk_error_code,
        "context": exc.context,
    }

    logger.error(
        "VK API error occurred", error_detail=exc.detail, **error_context
    )

    response_data = {
        "error": {
            "code": "VK_API_ERROR",
            "message": exc.detail,
            "status_code": status.HTTP_502_BAD_GATEWAY,
            "vk_error_code": exc.vk_error_code,
        }
    }

    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY, content=response_data
    )


async def database_exception_handler(
    request: Request, exc: DatabaseError
) -> JSONResponse:
    """Handle database errors with connection information."""

    error_context = {
        "path": request.url.path,
        "method": request.method,
        "db_error": exc.db_error,
        "context": exc.context,
    }

    logger.error(
        "Database error occurred", error_detail=exc.detail, **error_context
    )

    response_data = {
        "error": {
            "code": "DATABASE_ERROR",
            "message": "Internal database error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data,
    )


async def cache_exception_handler(
    request: Request, exc: CacheError
) -> JSONResponse:
    """Handle cache errors with key information."""

    error_context = {
        "path": request.url.path,
        "method": request.method,
        "cache_key": exc.cache_key,
        "context": exc.context,
    }

    logger.warning(
        "Cache error occurred", error_detail=exc.detail, **error_context
    )

    response_data = {
        "error": {
            "code": "CACHE_ERROR",
            "message": "Cache operation failed",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data,
    )


async def rate_limit_exception_handler(
    request: Request, exc: RateLimitError
) -> JSONResponse:
    """Handle rate limit errors with retry information."""

    error_context = {
        "path": request.url.path,
        "method": request.method,
        "retry_after": exc.retry_after,
        "context": exc.context,
    }

    logger.warning(
        "Rate limit exceeded", error_detail=exc.detail, **error_context
    )

    response_data = {
        "error": {
            "code": "RATE_LIMIT_ERROR",
            "message": exc.detail,
            "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
        }
    }

    if exc.retry_after:
        response_data["error"]["retry_after"] = exc.retry_after

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS, content=response_data
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions with full traceback logging."""

    error_context = {
        "path": request.url.path,
        "method": request.method,
        "exception_type": type(exc).__name__,
        "traceback": traceback.format_exc(),
    }

    logger.error(
        "Unexpected error occurred", error_detail=str(exc), **error_context
    )

    response_data = {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data,
    )
