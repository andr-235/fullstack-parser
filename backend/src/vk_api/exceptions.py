"""
Исключения модуля VK API

Содержит специфические исключения для модуля работы с VK API
"""

from typing import Optional, Dict, Any

from shared.presentation.exceptions import APIException as APIError


class VKAPIError(APIError):
    """Общая ошибка VK API"""

    def __init__(
        self,
        message: str,
        error_code: Optional[int] = None,
        method: Optional[str] = None,
        details: Optional[dict] = None,
        status_code: int = 502,
        api_error_code: str = "VK_API_ERROR",
    ):
        detail = f"VK API Error: {message}"
        details_dict: Dict[str, Any] = {"message": message}

        if error_code is not None:
            details_dict["vk_error_code"] = error_code
        if method is not None:
            details_dict["method"] = method
        if details:
            details_dict["details"] = (
                details.copy()
            )  # Копируем, чтобы избежать изменений
        else:
            details_dict["details"] = (
                {}
            )  # Создаем пустой словарь для совместимости с тестами

        # Добавляем error_type из details, если он есть
        if details and "error_type" in details:
            details_dict["error_type"] = details["error_type"]

        # Добавляем все остальные поля из details в details_dict
        if details:
            for key, value in details.items():
                if key not in details_dict:
                    details_dict[key] = value

        super().__init__(
            status_code=status_code,
            error_code=api_error_code,
            message=detail,
            details=details_dict,
        )


class VKAPIRateLimitError(VKAPIError):
    """Ошибка превышения лимита запросов VK API"""

    def __init__(
        self, wait_time: Optional[float] = None, method: Optional[str] = None
    ):
        detail = "VK API rate limit exceeded"
        details_dict: Dict[str, Any] = {"error_type": "rate_limit"}

        if wait_time is not None:
            try:
                wait_time_float = float(wait_time)
                detail += f". Wait {wait_time_float:.1f} seconds"
                details_dict["wait_time"] = wait_time_float
            except (ValueError, TypeError):
                detail += f". Wait {wait_time} seconds"
                details_dict["wait_time"] = wait_time
        if method:
            details_dict["method"] = method

        super().__init__(
            message=detail,
            details=details_dict,
            status_code=429,
            api_error_code="VK_API_RATE_LIMIT",
        )


class VKAPIAuthError(VKAPIError):
    """Ошибка аутентификации VK API"""

    def __init__(
        self,
        message: str = "VK API authentication failed",
        method: Optional[str] = None,
    ):
        # Убеждаемся, что в сообщении есть слово "authentication"
        if "authentication" not in message.lower():
            detail = f"VK API authentication failed: {message}"
        else:
            detail = message

        details_dict = {"message": message, "error_type": "auth"}
        if method:
            details_dict["method"] = method

        super().__init__(
            message=detail,
            details=details_dict,
            status_code=401,
            api_error_code="VK_API_AUTH",
        )


class VKAPIAccessDeniedError(VKAPIError):
    """Ошибка доступа к ресурсу VK API"""

    def __init__(
        self,
        resource: str,
        reason: Optional[str] = None,
        method: Optional[str] = None,
    ):
        detail = f"VK API access denied to resource: {resource}"
        details_dict = {"resource": resource, "error_type": "access_denied"}

        if reason:
            detail += f" ({reason})"
            details_dict["reason"] = reason
        if method:
            details_dict["method"] = method

        super().__init__(
            message=detail,
            details=details_dict,
            status_code=403,
            api_error_code="VK_API_ACCESS_DENIED",
        )


class VKAPIInvalidTokenError(VKAPIError):
    """Неверный токен доступа VK API"""

    def __init__(self, message: str = "Invalid VK API access token"):
        # Убеждаемся, что в сообщении есть слова "invalid token"
        if "invalid token" not in message.lower():
            detail = f"{message} (invalid token)"
        else:
            detail = message

        super().__init__(
            message=detail,
            details={"message": message, "error_type": "invalid_token"},
            status_code=401,
            api_error_code="VK_API_INVALID_TOKEN",
        )


class VKAPIInvalidParamsError(VKAPIError):
    """Неверные параметры запроса VK API"""

    def __init__(
        self,
        params: Optional[dict] = None,
        message: str = "Invalid VK API parameters",
        field: Optional[str] = None,
    ):
        # Убеждаемся, что в сообщении есть слова "invalid parameters"
        if "invalid parameters" not in message.lower():
            detail = f"{message} (invalid parameters)"
        else:
            detail = message

        details_dict: Dict[str, Any] = {
            "message": message,
            "error_type": "invalid_params",
        }

        if params:
            details_dict["params"] = params
        if field:
            details_dict["field"] = field

        super().__init__(
            message=detail,
            details=details_dict,
            status_code=400,
            api_error_code="VK_API_INVALID_PARAMS",
        )


class VKAPITimeoutError(VKAPIError):
    """Превышено время ожидания ответа VK API"""

    def __init__(
        self,
        message: str = "VK API request timeout",
        timeout: Optional[float] = None,
        method: Optional[str] = None,
    ):
        # Убеждаемся, что в сообщении есть слово "timeout"
        if "timeout" not in message.lower():
            detail = f"VK API request timeout: {message}"
        else:
            detail = message

        details_dict: Dict[str, Any] = {"error_type": "timeout"}

        if timeout is not None:
            try:
                timeout_float = float(timeout)
                detail += f" ({timeout_float:.2f}s)"
                details_dict["timeout"] = timeout_float
            except (ValueError, TypeError):
                detail += f" ({timeout})"
                details_dict["timeout"] = timeout
        if method:
            details_dict["method"] = method

        super().__init__(
            message=detail,
            details=details_dict,
            status_code=504,
            api_error_code="VK_API_TIMEOUT",
        )


class VKAPINetworkError(VKAPIError):
    """Ошибка сети при работе с VK API"""

    def __init__(
        self,
        message: str = "VK API network error",
        details: Optional[dict] = None,
    ):
        # Убеждаемся, что в сообщении есть слово "network"
        if "network" not in message.lower():
            detail = f"VK API network error: {message}"
        else:
            detail = message

        details_dict: Dict[str, Any] = {
            "message": message,
            "error_type": "network",
        }
        if details:
            details_dict["details"] = details

        super().__init__(
            message=detail,
            details=details_dict,
            status_code=502,
            api_error_code="VK_API_NETWORK",
        )


class VKAPIResourceNotFoundError(VKAPIError):
    """Ресурс не найден в VK API"""

    def __init__(self, resource_type: str, resource_id: str):
        detail = f"VK API resource not found: {resource_type} {resource_id}"
        extra_data = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }

        super().__init__(
            message=detail,
            details=extra_data,
            status_code=404,
            api_error_code="VK_API_RESOURCE_NOT_FOUND",
        )


class VKAPIInvalidResponseError(VKAPIError):
    """Неверный формат ответа VK API"""

    def __init__(
        self,
        message: str = "Invalid VK API response format",
        response: Optional[str] = None,
    ):
        # Убеждаемся, что в сообщении есть слова "invalid response"
        if "invalid response" not in message.lower():
            detail = f"{message} (invalid response)"
        else:
            detail = message

        extra_data = {"message": message, "error_type": "invalid_response"}
        if response:
            # Сохраняем только первые 500 символов ответа
            extra_data["response_preview"] = (
                response[:500] + "..." if len(response) > 500 else response
            )

        super().__init__(
            message=detail,
            details=extra_data,
            status_code=502,
            api_error_code="VK_API_INVALID_RESPONSE",
        )


class VKAPIGroupAccessError(VKAPIError):
    """Ошибка доступа к группе VK"""

    def __init__(
        self, group_id: int, reason: str = "Access denied to VK group"
    ):
        detail = f"{reason}: group {group_id}"
        extra_data = {"group_id": group_id, "reason": reason}

        super().__init__(
            message=detail,
            details=extra_data,
            status_code=403,
            api_error_code="VK_API_GROUP_ACCESS_ERROR",
        )


class VKAPIPostNotFoundError(VKAPIError):
    """Пост не найден в VK API"""

    def __init__(self, post_id: int, group_id: Optional[int] = None):
        detail = f"VK post not found: {post_id}"
        extra_data = {"post_id": post_id}

        if group_id:
            detail += f" in group {group_id}"
            extra_data["group_id"] = group_id

        super().__init__(
            message=detail,
            details=extra_data,
            status_code=404,
            api_error_code="VK_API_POST_NOT_FOUND",
        )


class VKAPIUserNotFoundError(VKAPIError):
    """Пользователь не найден в VK API"""

    def __init__(self, user_id: int):
        super().__init__(
            message=f"VK user not found: {user_id}",
            details={"user_id": user_id},
            status_code=404,
            api_error_code="VK_API_USER_NOT_FOUND",
        )


class VKAPIRetryExhaustedError(VKAPIError):
    """Исчерпаны попытки повтора запроса к VK API"""

    def __init__(self, max_attempts: int, method: Optional[str] = None):
        detail = f"VK API retry exhausted after {max_attempts} attempts"
        extra_data: Dict[str, Any] = {"max_attempts": max_attempts}

        if method:
            detail += f" for method {method}"
            extra_data["method"] = method

        super().__init__(
            message=detail,
            details=extra_data,
            status_code=502,
            api_error_code="VK_API_RETRY_EXHAUSTED",
        )


class VKAPIConfigurationError(VKAPIError):
    """Ошибка конфигурации VK API"""

    def __init__(
        self, config_key: str, message: str = "VK API configuration error"
    ):
        detail = f"{message}: {config_key}"
        extra_data = {"config_key": config_key, "message": message}

        super().__init__(
            message=detail,
            details=extra_data,
            status_code=500,
            api_error_code="VK_API_CONFIGURATION_ERROR",
        )


class VKAPICacheError(VKAPIError):
    """Ошибка кеширования VK API"""

    def __init__(self, operation: str, message: str = "VK API cache error"):
        extra_data = {"operation": operation, "message": message}

        super().__init__(
            message=f"{message}: {operation}",
            details=extra_data,
            status_code=500,
            api_error_code="VK_API_CACHE_ERROR",
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
