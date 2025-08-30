"""
Исключения модуля VK API

Содержит специфические исключения для модуля работы с VK API
"""

from typing import Optional, Dict, Any

from ..exceptions import APIError


class VKAPIError(APIError):
    """Общая ошибка VK API"""

    def __init__(
        self,
        message: str,
        error_code: Optional[int] = None,
        method: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        detail = f"VK API Error: {message}"
        details_dict: Dict[str, Any] = {"message": message}

        if error_code is not None:
            details_dict["vk_error_code"] = error_code
        if method:
            details_dict["method"] = method
        if details:
            details_dict["details"] = details

        super().__init__(
            status_code=502,
            error_code="VK_API_ERROR",
            message=detail,
            details=details_dict,
        )


class VKAPIRateLimitError(APIError):
    """Ошибка превышения лимита запросов VK API"""

    def __init__(
        self, wait_time: Optional[float] = None, method: Optional[str] = None
    ):
        detail = "VK API rate limit exceeded"
        details_dict: Dict[str, Any] = {"error_type": "rate_limit"}

        if wait_time is not None:
            detail += f". Wait {wait_time:.2f} seconds"
            details_dict["wait_time_seconds"] = wait_time
        if method:
            details_dict["method"] = method

        super().__init__(
            status_code=429,
            error_code="VK_API_RATE_LIMIT",
            message=detail,
            details=details_dict,
        )


class VKAPIAuthError(APIError):
    """Ошибка аутентификации VK API"""

    def __init__(self, message: str = "VK API authentication failed"):
        super().__init__(
            status_code=401,
            error_code="VK_API_AUTH_ERROR",
            message=message,
            details={"message": message},
        )


class VKAPIAccessDeniedError(APIError):
    """Ошибка доступа к ресурсу VK API"""

    def __init__(self, resource: str, reason: Optional[str] = None):
        detail = f"VK API access denied to resource: {resource}"
        details_dict = {"resource": resource}

        if reason:
            detail += f" ({reason})"
            details_dict["reason"] = reason

        super().__init__(
            status_code=403,
            error_code="VK_API_ACCESS_DENIED",
            message=detail,
            details=details_dict,
        )


class VKAPIInvalidTokenError(APIError):
    """Неверный токен доступа VK API"""

    def __init__(self, message: str = "Invalid VK API access token"):
        super().__init__(
            status_code=401,
            error_code="VK_API_INVALID_TOKEN",
            message=message,
            details={"message": message},
        )


class VKAPIInvalidParamsError(APIError):
    """Неверные параметры запроса VK API"""

    def __init__(
        self,
        params: Optional[dict] = None,
        message: str = "Invalid VK API parameters",
    ):
        detail = message
        details_dict: Dict[str, Any] = {"message": message}

        if params:
            details_dict["params"] = params

        super().__init__(
            status_code=400,
            error_code="VK_API_INVALID_PARAMS",
            message=detail,
            details=details_dict,
        )


class VKAPITimeoutError(APIError):
    """Превышено время ожидания ответа VK API"""

    def __init__(
        self, timeout: Optional[float] = None, method: Optional[str] = None
    ):
        detail = "VK API request timeout"
        details_dict: Dict[str, Any] = {}

        if timeout is not None:
            detail += f" ({timeout:.2f}s)"
            details_dict["timeout"] = timeout
        if method:
            details_dict["method"] = method

        super().__init__(
            status_code=408,
            error_code="VK_API_TIMEOUT",
            message=detail,
            details=details_dict,
        )


class VKAPINetworkError(APIError):
    """Ошибка сети при работе с VK API"""

    def __init__(
        self,
        message: str = "VK API network error",
        details: Optional[dict] = None,
    ):
        details_dict: Dict[str, Any] = {"message": message}
        if details:
            details_dict["details"] = details

        super().__init__(
            status_code=502,
            error_code="VK_API_NETWORK_ERROR",
            message=message,
            details=details_dict,
        )


class VKAPIResourceNotFoundError(APIError):
    """Ресурс не найден в VK API"""

    def __init__(self, resource_type: str, resource_id: str):
        detail = f"VK API resource not found: {resource_type} {resource_id}"
        extra_data = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }

        super().__init__(
            status_code=404,
            error_code="VK_API_RESOURCE_NOT_FOUND",
            message=detail,
            details=extra_data,
        )


class VKAPIInvalidResponseError(APIError):
    """Неверный формат ответа VK API"""

    def __init__(
        self,
        response: Optional[str] = None,
        message: str = "Invalid VK API response format",
    ):
        extra_data = {"message": message}
        if response:
            # Сохраняем только первые 500 символов ответа
            extra_data["response_preview"] = (
                response[:500] + "..." if len(response) > 500 else response
            )

        super().__init__(
            status_code=502,
            error_code="VK_API_INVALID_RESPONSE",
            message=message,
            details=extra_data,
        )


class VKAPIGroupAccessError(APIError):
    """Ошибка доступа к группе VK"""

    def __init__(
        self, group_id: int, reason: str = "Access denied to VK group"
    ):
        detail = f"{reason}: group {group_id}"
        extra_data = {"group_id": group_id, "reason": reason}

        super().__init__(
            status_code=403,
            error_code="VK_API_GROUP_ACCESS_ERROR",
            message=detail,
            details=extra_data,
        )


class VKAPIPostNotFoundError(APIError):
    """Пост не найден в VK API"""

    def __init__(self, post_id: int, group_id: Optional[int] = None):
        detail = f"VK post not found: {post_id}"
        extra_data = {"post_id": post_id}

        if group_id:
            detail += f" in group {group_id}"
            extra_data["group_id"] = group_id

        super().__init__(
            status_code=404,
            error_code="VK_API_POST_NOT_FOUND",
            message=detail,
            details=extra_data,
        )


class VKAPIUserNotFoundError(APIError):
    """Пользователь не найден в VK API"""

    def __init__(self, user_id: int):
        super().__init__(
            status_code=404,
            error_code="VK_API_USER_NOT_FOUND",
            message=f"VK user not found: {user_id}",
            details={"user_id": user_id},
        )


class VKAPIRetryExhaustedError(APIError):
    """Исчерпаны попытки повтора запроса к VK API"""

    def __init__(self, max_attempts: int, method: Optional[str] = None):
        detail = f"VK API retry exhausted after {max_attempts} attempts"
        extra_data: Dict[str, Any] = {"max_attempts": max_attempts}

        if method:
            detail += f" for method {method}"
            extra_data["method"] = method

        super().__init__(
            status_code=502,
            error_code="VK_API_RETRY_EXHAUSTED",
            message=detail,
            details=extra_data,
        )


class VKAPIConfigurationError(APIError):
    """Ошибка конфигурации VK API"""

    def __init__(
        self, config_key: str, message: str = "VK API configuration error"
    ):
        detail = f"{message}: {config_key}"
        extra_data = {"config_key": config_key, "message": message}

        super().__init__(
            status_code=500,
            error_code="VK_API_CONFIGURATION_ERROR",
            message=detail,
            details=extra_data,
        )


class VKAPICacheError(APIError):
    """Ошибка кеширования VK API"""

    def __init__(self, operation: str, message: str = "VK API cache error"):
        extra_data = {"operation": operation, "message": message}

        super().__init__(
            status_code=500,
            error_code="VK_API_CACHE_ERROR",
            message=f"{message}: {operation}",
            details=extra_data,
        )


class VKAPIMetricsError(APIError):
    """Ошибка метрик VK API"""

    def __init__(self, metric: str, message: str = "VK API metrics error"):
        extra_data = {"metric": metric, "message": message}

        super().__init__(
            status_code=500,
            error_code="VK_API_METRICS_ERROR",
            message=f"{message}: {metric}",
            details=extra_data,
        )


class VKAPIHealthCheckError(APIError):
    """Ошибка проверки здоровья VK API"""

    def __init__(
        self, component: str, message: str = "VK API health check failed"
    ):
        extra_data = {"component": component, "message": message}

        super().__init__(
            status_code=503,
            error_code="VK_API_HEALTH_CHECK_ERROR",
            message=f"{message}: {component}",
            details=extra_data,
        )


class VKAPIBulkOperationError(APIError):
    """Ошибка массовой операции"""

    def __init__(
        self,
        message: str,
        total_requested: int,
        total_succeeded: int,
        failed_items: Optional[list] = None,
        operation: Optional[str] = None,
    ):
        detail = f"Bulk operation failed: {message}"
        extra_data = {
            "error_type": "bulk_operation_error",
            "total_requested": total_requested,
            "total_succeeded": total_succeeded,
            "total_failed": total_requested - total_succeeded,
            "success_rate": (
                round(total_succeeded / total_requested * 100, 2)
                if total_requested > 0
                else 0
            ),
        }

        if failed_items:
            extra_data["failed_items"] = failed_items[
                :10
            ]  # Ограничим до 10 элементов для читаемости
        if operation:
            extra_data["operation"] = operation

        super().__init__(
            status_code=502,
            error_code="VK_API_BULK_OPERATION_ERROR",
            message=detail,
            details=extra_data,
        )


class VKAPIConcurrentRequestError(APIError):
    """Ошибка одновременных запросов"""

    def __init__(self, concurrent_requests: int, max_allowed: int):
        detail = f"Too many concurrent requests: {concurrent_requests}/{max_allowed}"
        extra_data = {
            "error_type": "concurrent_request_error",
            "concurrent_requests": concurrent_requests,
            "max_allowed": max_allowed,
            "suggestion": "Reduce concurrency or increase limits",
        }

        super().__init__(
            status_code=429,
            error_code="VK_API_CONCURRENT_REQUEST_ERROR",
            message=detail,
            details=extra_data,
        )


class VKAPICircuitBreakerOpenError(APIError):
    """Ошибка открытого circuit breaker"""

    def __init__(
        self, service: str, failure_count: int, recovery_timeout: float
    ):
        detail = f"Circuit breaker is open for {service}"
        extra_data: Dict[str, Any] = {
            "error_type": "circuit_breaker_open",
            "service": service,
            "failure_count": failure_count,
            "recovery_timeout_seconds": recovery_timeout,
            "retry_after": int(recovery_timeout),
        }

        super().__init__(
            status_code=503,
            error_code="VK_API_CIRCUIT_BREAKER_OPEN",
            message=detail,
            details=extra_data,
        )


# Экспорт всех исключений
__all__ = [
    "VKAPIError",
    "VKAPIRateLimitError",
    "VKAPIAuthError",
    "VKAPIAccessDeniedError",
    "VKAPIInvalidTokenError",
    "VKAPIInvalidParamsError",
    "VKAPITimeoutError",
    "VKAPINetworkError",
    "VKAPIResourceNotFoundError",
    "VKAPIInvalidResponseError",
    "VKAPIGroupAccessError",
    "VKAPIPostNotFoundError",
    "VKAPIUserNotFoundError",
    "VKAPIRetryExhaustedError",
    "VKAPIConfigurationError",
    "VKAPICacheError",
    "VKAPIMetricsError",
    "VKAPIHealthCheckError",
    "VKAPIBulkOperationError",
    "VKAPIConcurrentRequestError",
    "VKAPICircuitBreakerOpenError",
]
