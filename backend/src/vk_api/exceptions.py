"""
Исключения модуля VK API

Содержит специфические исключения для модуля работы с VK API
"""

from ..exceptions import APIError


class VKAPIError(APIError):
    """Общая ошибка VK API"""

    def __init__(
        self,
        message: str,
        error_code: int = None,
        method: str = None,
        details: dict = None,
    ):
        detail = f"VK API Error: {message}"
        extra_data = {"message": message}

        if error_code is not None:
            extra_data["vk_error_code"] = error_code
        if method:
            extra_data["method"] = method
        if details:
            extra_data["details"] = details

        super().__init__(
            status_code=502,
            detail=detail,
            error_code="VK_API_ERROR",
            extra_data=extra_data,
        )


class VKAPIRateLimitError(APIError):
    """Ошибка превышения лимита запросов VK API"""

    def __init__(self, wait_time: float = None, method: str = None):
        detail = "VK API rate limit exceeded"
        extra_data = {}

        if wait_time is not None:
            detail += f". Wait {wait_time:.2f} seconds"
            extra_data["wait_time"] = wait_time
        if method:
            extra_data["method"] = method

        super().__init__(
            status_code=429,
            detail=detail,
            error_code="VK_API_RATE_LIMIT",
            extra_data=extra_data,
        )


class VKAPIAuthError(APIError):
    """Ошибка аутентификации VK API"""

    def __init__(self, message: str = "VK API authentication failed"):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="VK_API_AUTH_ERROR",
            extra_data={"message": message},
        )


class VKAPIAccessDeniedError(APIError):
    """Ошибка доступа к ресурсу VK API"""

    def __init__(self, resource: str, reason: str = None):
        detail = f"VK API access denied to resource: {resource}"
        extra_data = {"resource": resource}

        if reason:
            detail += f" ({reason})"
            extra_data["reason"] = reason

        super().__init__(
            status_code=403,
            detail=detail,
            error_code="VK_API_ACCESS_DENIED",
            extra_data=extra_data,
        )


class VKAPIInvalidTokenError(APIError):
    """Неверный токен доступа VK API"""

    def __init__(self, message: str = "Invalid VK API access token"):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="VK_API_INVALID_TOKEN",
            extra_data={"message": message},
        )


class VKAPIInvalidParamsError(APIError):
    """Неверные параметры запроса VK API"""

    def __init__(
        self, params: dict = None, message: str = "Invalid VK API parameters"
    ):
        detail = message
        extra_data = {"message": message}

        if params:
            extra_data["params"] = params

        super().__init__(
            status_code=400,
            detail=detail,
            error_code="VK_API_INVALID_PARAMS",
            extra_data=extra_data,
        )


class VKAPITimeoutError(APIError):
    """Превышено время ожидания ответа VK API"""

    def __init__(self, timeout: float = None, method: str = None):
        detail = "VK API request timeout"
        extra_data = {}

        if timeout is not None:
            detail += f" ({timeout:.2f}s)"
            extra_data["timeout"] = timeout
        if method:
            extra_data["method"] = method

        super().__init__(
            status_code=408,
            detail=detail,
            error_code="VK_API_TIMEOUT",
            extra_data=extra_data,
        )


class VKAPINetworkError(APIError):
    """Ошибка сети при работе с VK API"""

    def __init__(
        self, message: str = "VK API network error", details: dict = None
    ):
        extra_data = {"message": message}
        if details:
            extra_data["details"] = details

        super().__init__(
            status_code=502,
            detail=message,
            error_code="VK_API_NETWORK_ERROR",
            extra_data=extra_data,
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
            detail=detail,
            error_code="VK_API_RESOURCE_NOT_FOUND",
            extra_data=extra_data,
        )


class VKAPIInvalidResponseError(APIError):
    """Неверный формат ответа VK API"""

    def __init__(
        self,
        response: str = None,
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
            detail=message,
            error_code="VK_API_INVALID_RESPONSE",
            extra_data=extra_data,
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
            detail=detail,
            error_code="VK_API_GROUP_ACCESS_ERROR",
            extra_data=extra_data,
        )


class VKAPIPostNotFoundError(APIError):
    """Пост не найден в VK API"""

    def __init__(self, post_id: int, group_id: int = None):
        detail = f"VK post not found: {post_id}"
        extra_data = {"post_id": post_id}

        if group_id:
            detail += f" in group {group_id}"
            extra_data["group_id"] = group_id

        super().__init__(
            status_code=404,
            detail=detail,
            error_code="VK_API_POST_NOT_FOUND",
            extra_data=extra_data,
        )


class VKAPIUserNotFoundError(APIError):
    """Пользователь не найден в VK API"""

    def __init__(self, user_id: int):
        super().__init__(
            status_code=404,
            detail=f"VK user not found: {user_id}",
            error_code="VK_API_USER_NOT_FOUND",
            extra_data={"user_id": user_id},
        )


class VKAPIRetryExhaustedError(APIError):
    """Исчерпаны попытки повтора запроса к VK API"""

    def __init__(self, max_attempts: int, method: str = None):
        detail = f"VK API retry exhausted after {max_attempts} attempts"
        extra_data = {"max_attempts": max_attempts}

        if method:
            detail += f" for method {method}"
            extra_data["method"] = method

        super().__init__(
            status_code=502,
            detail=detail,
            error_code="VK_API_RETRY_EXHAUSTED",
            extra_data=extra_data,
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
            detail=detail,
            error_code="VK_API_CONFIGURATION_ERROR",
            extra_data=extra_data,
        )


class VKAPICacheError(APIError):
    """Ошибка кеширования VK API"""

    def __init__(self, operation: str, message: str = "VK API cache error"):
        extra_data = {"operation": operation, "message": message}

        super().__init__(
            status_code=500,
            detail=f"{message}: {operation}",
            error_code="VK_API_CACHE_ERROR",
            extra_data=extra_data,
        )


class VKAPIMetricsError(APIError):
    """Ошибка метрик VK API"""

    def __init__(self, metric: str, message: str = "VK API metrics error"):
        extra_data = {"metric": metric, "message": message}

        super().__init__(
            status_code=500,
            detail=f"{message}: {metric}",
            error_code="VK_API_METRICS_ERROR",
            extra_data=extra_data,
        )


class VKAPIHealthCheckError(APIError):
    """Ошибка проверки здоровья VK API"""

    def __init__(
        self, component: str, message: str = "VK API health check failed"
    ):
        extra_data = {"component": component, "message": message}

        super().__init__(
            status_code=503,
            detail=f"{message}: {component}",
            error_code="VK_API_HEALTH_CHECK_ERROR",
            extra_data=extra_data,
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
]
