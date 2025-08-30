"""
Исключения модуля Health

Содержит специфические исключения для модуля проверки здоровья системы
"""

from ..exceptions import APIException


class HealthError(APIException):
    """Общая ошибка модуля Health"""

    def __init__(
        self,
        message: str,
        error_code: str = "HEALTH_ERROR",
        details: dict = None,
    ):
        super().__init__(
            status_code=500,
            detail=message,
            error_code=error_code,
            extra_data=details or {},
        )


class HealthCheckFailedError(APIException):
    """Ошибка выполнения проверки здоровья"""

    def __init__(
        self,
        component: str,
        message: str = "Health check failed",
        details: dict = None,
    ):
        extra_data = {"component": component}
        if details:
            extra_data.update(details)

        super().__init__(
            status_code=503,
            detail=f"{message}: {component}",
            error_code="HEALTH_CHECK_FAILED",
            extra_data=extra_data,
        )


class HealthComponentNotFoundError(APIException):
    """Компонент здоровья не найден"""

    def __init__(self, component: str):
        super().__init__(
            status_code=404,
            detail=f"Health component not found: {component}",
            error_code="HEALTH_COMPONENT_NOT_FOUND",
            extra_data={"component": component},
        )


class HealthCheckTimeoutError(APIException):
    """Превышено время ожидания проверки здоровья"""

    def __init__(self, component: str, timeout: float):
        super().__init__(
            status_code=504,
            detail=f"Health check timeout for {component}: {timeout}s",
            error_code="HEALTH_CHECK_TIMEOUT",
            extra_data={"component": component, "timeout": timeout},
        )


class HealthConfigurationError(APIException):
    """Ошибка конфигурации проверки здоровья"""

    def __init__(self, message: str, config_key: str = None):
        extra_data = {"message": message}
        if config_key:
            extra_data["config_key"] = config_key

        super().__init__(
            status_code=500,
            detail=message,
            error_code="HEALTH_CONFIGURATION_ERROR",
            extra_data=extra_data,
        )


class HealthServiceUnavailableError(APIException):
    """Сервис здоровья недоступен"""

    def __init__(
        self, service: str, message: str = "Health service unavailable"
    ):
        super().__init__(
            status_code=503,
            detail=f"{message}: {service}",
            error_code="HEALTH_SERVICE_UNAVAILABLE",
            extra_data={"service": service, "message": message},
        )


class HealthMetricsUnavailableError(APIException):
    """Метрики здоровья недоступны"""

    def __init__(
        self, metric: str, message: str = "Health metrics unavailable"
    ):
        super().__init__(
            status_code=503,
            detail=f"{message}: {metric}",
            error_code="HEALTH_METRICS_UNAVAILABLE",
            extra_data={"metric": metric, "message": message},
        )


class HealthCacheError(APIException):
    """Ошибка кеширования здоровья"""

    def __init__(self, operation: str, message: str = "Health cache error"):
        super().__init__(
            status_code=500,
            detail=f"{message}: {operation}",
            error_code="HEALTH_CACHE_ERROR",
            extra_data={"operation": operation, "message": message},
        )


class HealthDatabaseError(APIException):
    """Ошибка проверки базы данных"""

    def __init__(
        self,
        message: str = "Database health check failed",
        details: dict = None,
    ):
        super().__init__(
            status_code=503,
            detail=message,
            error_code="HEALTH_DATABASE_ERROR",
            extra_data=details or {},
        )


class HealthRedisError(APIException):
    """Ошибка проверки Redis"""

    def __init__(
        self, message: str = "Redis health check failed", details: dict = None
    ):
        super().__init__(
            status_code=503,
            detail=message,
            error_code="HEALTH_REDIS_ERROR",
            extra_data=details or {},
        )


class HealthVKAPIError(APIException):
    """Ошибка проверки VK API"""

    def __init__(
        self, message: str = "VK API health check failed", details: dict = None
    ):
        super().__init__(
            status_code=503,
            detail=message,
            error_code="HEALTH_VK_API_ERROR",
            extra_data=details or {},
        )


class HealthSystemResourceError(APIException):
    """Ошибка проверки системных ресурсов"""

    def __init__(self, resource: str, current_value: float, threshold: float):
        super().__init__(
            status_code=503,
            detail=f"System resource {resource} exceeded threshold: {current_value:.1f} > {threshold:.1f}",
            error_code="HEALTH_SYSTEM_RESOURCE_ERROR",
            extra_data={
                "resource": resource,
                "current_value": current_value,
                "threshold": threshold,
            },
        )


class HealthReadinessError(APIException):
    """Ошибка проверки готовности"""

    def __init__(
        self, message: str = "Service is not ready", details: dict = None
    ):
        super().__init__(
            status_code=503,
            detail=message,
            error_code="HEALTH_READINESS_ERROR",
            extra_data=details or {},
        )


class HealthLivenessError(APIException):
    """Ошибка проверки живости"""

    def __init__(
        self, message: str = "Service is not alive", details: dict = None
    ):
        super().__init__(
            status_code=503,
            detail=message,
            error_code="HEALTH_LIVENESS_ERROR",
            extra_data=details or {},
        )


class HealthExportError(APIException):
    """Ошибка экспорта данных здоровья"""

    def __init__(
        self, format: str, message: str = "Health data export failed"
    ):
        super().__init__(
            status_code=500,
            detail=f"{message}: {format}",
            error_code="HEALTH_EXPORT_ERROR",
            extra_data={"format": format, "message": message},
        )


class HealthImportError(APIException):
    """Ошибка импорта данных здоровья"""

    def __init__(
        self, source: str, message: str = "Health data import failed"
    ):
        super().__init__(
            status_code=400,
            detail=f"{message}: {source}",
            error_code="HEALTH_IMPORT_ERROR",
            extra_data={"source": source, "message": message},
        )


class HealthNotificationError(APIException):
    """Ошибка отправки уведомления о здоровье"""

    def __init__(
        self, channel: str, message: str = "Health notification failed"
    ):
        super().__init__(
            status_code=500,
            detail=f"{message}: {channel}",
            error_code="HEALTH_NOTIFICATION_ERROR",
            extra_data={"channel": channel, "message": message},
        )


class HealthRetryExhaustedError(APIException):
    """Исчерпаны попытки повтора проверки здоровья"""

    def __init__(self, component: str, max_attempts: int):
        super().__init__(
            status_code=503,
            detail=f"Health check retry exhausted for {component} after {max_attempts} attempts",
            error_code="HEALTH_RETRY_EXHAUSTED",
            extra_data={"component": component, "max_attempts": max_attempts},
        )


class HealthInvalidStatusError(APIException):
    """Неверный статус здоровья"""

    def __init__(self, status: str, valid_statuses: list):
        super().__init__(
            status_code=400,
            detail=f"Invalid health status: {status}. Valid: {', '.join(valid_statuses)}",
            error_code="HEALTH_INVALID_STATUS",
            extra_data={"status": status, "valid_statuses": valid_statuses},
        )


class HealthComponentDisabledError(APIException):
    """Компонент проверки здоровья отключен"""

    def __init__(self, component: str):
        super().__init__(
            status_code=503,
            detail=f"Health component disabled: {component}",
            error_code="HEALTH_COMPONENT_DISABLED",
            extra_data={"component": component},
        )


class HealthDependencyError(APIException):
    """Ошибка проверки зависимостей здоровья"""

    def __init__(
        self, dependency: str, message: str = "Health dependency check failed"
    ):
        super().__init__(
            status_code=503,
            detail=f"{message}: {dependency}",
            error_code="HEALTH_DEPENDENCY_ERROR",
            extra_data={"dependency": dependency, "message": message},
        )


# Экспорт всех исключений
__all__ = [
    "HealthError",
    "HealthCheckFailedError",
    "HealthComponentNotFoundError",
    "HealthCheckTimeoutError",
    "HealthConfigurationError",
    "HealthServiceUnavailableError",
    "HealthMetricsUnavailableError",
    "HealthCacheError",
    "HealthDatabaseError",
    "HealthRedisError",
    "HealthVKAPIError",
    "HealthSystemResourceError",
    "HealthReadinessError",
    "HealthLivenessError",
    "HealthExportError",
    "HealthImportError",
    "HealthNotificationError",
    "HealthRetryExhaustedError",
    "HealthInvalidStatusError",
    "HealthComponentDisabledError",
    "HealthDependencyError",
]
