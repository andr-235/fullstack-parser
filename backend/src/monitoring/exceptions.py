"""
Исключения модуля Monitoring

Содержит специфические исключения для модуля мониторинга групп
"""

from ..exceptions import APIException


class MonitoringNotFoundError(APIException):
    """Мониторинг не найден"""

    def __init__(self, monitoring_id: str):
        super().__init__(
            status_code=404,
            detail=f"Мониторинг с ID {monitoring_id} не найден",
            error_code="MONITORING_NOT_FOUND",
            extra_data={"monitoring_id": monitoring_id},
        )


class InvalidMonitoringDataError(APIException):
    """Неверные данные мониторинга"""

    def __init__(self, field: str, value: str = None):
        detail = f"Неверное значение поля '{field}'"
        if value:
            detail += f": {value}"

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="INVALID_MONITORING_DATA",
            extra_data={"field": field, "value": value},
        )


class MonitoringAlreadyExistsError(APIException):
    """Мониторинг уже существует"""

    def __init__(self, group_id: int):
        super().__init__(
            status_code=409,
            detail=f"Мониторинг для группы {group_id} уже существует",
            error_code="MONITORING_ALREADY_EXISTS",
            extra_data={"group_id": group_id},
        )


class MonitoringOperationError(APIException):
    """Ошибка операции с мониторингом"""

    def __init__(self, operation: str, monitoring_id: str, reason: str = None):
        detail = (
            f"Ошибка операции '{operation}' для мониторинга {monitoring_id}"
        )
        if reason:
            detail += f": {reason}"

        super().__init__(
            status_code=400,
            detail=detail,
            error_code="MONITORING_OPERATION_ERROR",
            extra_data={
                "operation": operation,
                "monitoring_id": monitoring_id,
                "reason": reason,
            },
        )


class MonitoringQueueFullError(APIException):
    """Очередь мониторинга переполнена"""

    def __init__(self, queue_size: int):
        super().__init__(
            status_code=503,
            detail="Очередь задач мониторинга переполнена",
            error_code="MONITORING_QUEUE_FULL",
            extra_data={"queue_size": queue_size},
        )


class MonitoringTimeoutError(APIException):
    """Превышено время выполнения мониторинга"""

    def __init__(self, monitoring_id: str, timeout: int):
        super().__init__(
            status_code=504,
            detail="Превышено время выполнения задачи мониторинга",
            error_code="MONITORING_TIMEOUT",
            extra_data={"monitoring_id": monitoring_id, "timeout": timeout},
        )


class MonitoringParsingError(APIException):
    """Ошибка парсинга в мониторинге"""

    def __init__(self, monitoring_id: str, group_id: int, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка парсинга группы {group_id} в мониторинге {monitoring_id}",
            error_code="MONITORING_PARSING_ERROR",
            extra_data={
                "monitoring_id": monitoring_id,
                "group_id": group_id,
                "error": error,
            },
        )


class MonitoringNotificationError(APIException):
    """Ошибка отправки уведомления"""

    def __init__(self, monitoring_id: str, channel: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка отправки уведомления через {channel}",
            error_code="MONITORING_NOTIFICATION_ERROR",
            extra_data={
                "monitoring_id": monitoring_id,
                "channel": channel,
                "error": error,
            },
        )


class MonitoringConfigError(APIException):
    """Ошибка конфигурации мониторинга"""

    def __init__(self, config_key: str, error: str):
        super().__init__(
            status_code=422,
            detail=f"Ошибка конфигурации мониторинга: {error}",
            error_code="MONITORING_CONFIG_ERROR",
            extra_data={"config_key": config_key, "error": error},
        )


class MonitoringBulkOperationError(APIException):
    """Ошибка массовой операции"""

    def __init__(self, operation: str, errors: list):
        super().__init__(
            status_code=400,
            detail=f"Ошибка массовой операции '{operation}'",
            error_code="MONITORING_BULK_OPERATION_ERROR",
            extra_data={"operation": operation, "errors": errors},
        )


class MonitoringHealthCheckError(APIException):
    """Ошибка проверки здоровья"""

    def __init__(self, component: str, error: str):
        super().__init__(
            status_code=503,
            detail=f"Ошибка проверки здоровья компонента '{component}': {error}",
            error_code="MONITORING_HEALTH_CHECK_ERROR",
            extra_data={"component": component, "error": error},
        )


class MonitoringResourceLimitError(APIException):
    """Превышен лимит ресурсов"""

    def __init__(self, resource: str, limit: int, current: int):
        super().__init__(
            status_code=507,
            detail=f"Превышен лимит ресурса '{resource}': {current}/{limit}",
            error_code="MONITORING_RESOURCE_LIMIT",
            extra_data={
                "resource": resource,
                "limit": limit,
                "current": current,
            },
        )


class MonitoringConcurrencyError(APIException):
    """Ошибка параллелизма"""

    def __init__(self, monitoring_id: str, reason: str):
        super().__init__(
            status_code=409,
            detail=f"Ошибка параллелизма для мониторинга {monitoring_id}: {reason}",
            error_code="MONITORING_CONCURRENCY_ERROR",
            extra_data={"monitoring_id": monitoring_id, "reason": reason},
        )


class MonitoringDataValidationError(APIException):
    """Ошибка валидации данных мониторинга"""

    def __init__(self, data_type: str, errors: list):
        super().__init__(
            status_code=422,
            detail=f"Ошибка валидации данных типа '{data_type}'",
            error_code="MONITORING_DATA_VALIDATION_ERROR",
            extra_data={"data_type": data_type, "validation_errors": errors},
        )


class MonitoringExternalServiceError(APIException):
    """Ошибка внешнего сервиса"""

    def __init__(self, service_name: str, error_message: str):
        super().__init__(
            status_code=502,
            detail=f"Ошибка внешнего сервиса '{service_name}': {error_message}",
            error_code="MONITORING_EXTERNAL_SERVICE_ERROR",
            extra_data={
                "service": service_name,
                "error_message": error_message,
            },
        )


class MonitoringSchedulerError(APIException):
    """Ошибка планировщика"""

    def __init__(self, monitoring_id: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка планировщика для мониторинга {monitoring_id}: {error}",
            error_code="MONITORING_SCHEDULER_ERROR",
            extra_data={"monitoring_id": monitoring_id, "error": error},
        )


class MonitoringResultStorageError(APIException):
    """Ошибка хранения результатов"""

    def __init__(self, monitoring_id: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка хранения результатов мониторинга {monitoring_id}: {error}",
            error_code="MONITORING_RESULT_STORAGE_ERROR",
            extra_data={"monitoring_id": monitoring_id, "error": error},
        )


# Экспорт всех исключений
__all__ = [
    "MonitoringNotFoundError",
    "InvalidMonitoringDataError",
    "MonitoringAlreadyExistsError",
    "MonitoringOperationError",
    "MonitoringQueueFullError",
    "MonitoringTimeoutError",
    "MonitoringParsingError",
    "MonitoringNotificationError",
    "MonitoringConfigError",
    "MonitoringBulkOperationError",
    "MonitoringHealthCheckError",
    "MonitoringResourceLimitError",
    "MonitoringConcurrencyError",
    "MonitoringDataValidationError",
    "MonitoringExternalServiceError",
    "MonitoringSchedulerError",
    "MonitoringResultStorageError",
]
