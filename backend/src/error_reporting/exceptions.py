"""
Исключения модуля Error Reporting

Содержит специфические исключения для модуля отчетов об ошибках
"""

from ..exceptions import APIException


class ErrorReportingError(APIException):
    """Общая ошибка модуля Error Reporting"""

    def __init__(
        self,
        message: str,
        error_code: str = "ERROR_REPORTING_ERROR",
        details: dict = None,
    ):
        super().__init__(
            status_code=500,
            detail=message,
            error_code=error_code,
            extra_data=details or {},
        )


class ErrorReportNotFoundError(APIException):
    """Отчет об ошибке не найден"""

    def __init__(self, report_id: str):
        super().__init__(
            status_code=404,
            detail=f"Error report not found: {report_id}",
            error_code="ERROR_REPORT_NOT_FOUND",
            extra_data={"report_id": report_id},
        )


class ErrorReportValidationError(APIException):
    """Ошибка валидации отчета об ошибке"""

    def __init__(self, message: str, validation_errors: dict = None):
        extra_data = {"message": message}
        if validation_errors:
            extra_data["validation_errors"] = validation_errors

        super().__init__(
            status_code=400,
            detail=message,
            error_code="ERROR_REPORT_VALIDATION_ERROR",
            extra_data=extra_data,
        )


class ErrorReportAlreadyAcknowledgedError(APIException):
    """Отчет об ошибке уже подтвержден"""

    def __init__(self, report_id: str):
        super().__init__(
            status_code=409,
            detail=f"Error report already acknowledged: {report_id}",
            error_code="ERROR_REPORT_ALREADY_ACKNOWLEDGED",
            extra_data={"report_id": report_id},
        )


class ErrorReportAlreadyResolvedError(APIException):
    """Отчет об ошибке уже разрешен"""

    def __init__(self, report_id: str):
        super().__init__(
            status_code=409,
            detail=f"Error report already resolved: {report_id}",
            error_code="ERROR_REPORT_ALREADY_RESOLVED",
            extra_data={"report_id": report_id},
        )


class ErrorReportNotAcknowledgedError(APIException):
    """Отчет об ошибке не подтвержден"""

    def __init__(self, report_id: str):
        super().__init__(
            status_code=409,
            detail=f"Error report must be acknowledged before resolution: {report_id}",
            error_code="ERROR_REPORT_NOT_ACKNOWLEDGED",
            extra_data={"report_id": report_id},
        )


class ErrorReportAccessDeniedError(APIException):
    """Отказано в доступе к отчету об ошибке"""

    def __init__(
        self, report_id: str, message: str = "Access denied to error report"
    ):
        super().__init__(
            status_code=403,
            detail=f"{message}: {report_id}",
            error_code="ERROR_REPORT_ACCESS_DENIED",
            extra_data={"report_id": report_id},
        )


class ErrorReportLimitExceededError(APIException):
    """Превышен лимит отчетов об ошибках"""

    def __init__(self, current_count: int, max_count: int):
        super().__init__(
            status_code=429,
            detail=f"Error reports limit exceeded: {current_count} > {max_count}",
            error_code="ERROR_REPORT_LIMIT_EXCEEDED",
            extra_data={
                "current_count": current_count,
                "max_count": max_count,
            },
        )


class ErrorReportSizeLimitError(APIException):
    """Превышен лимит размера отчета об ошибке"""

    def __init__(self, field: str, current_size: int, max_size: int):
        super().__init__(
            status_code=413,
            detail=f"Error report {field} size limit exceeded: {current_size} > {max_size}",
            error_code="ERROR_REPORT_SIZE_LIMIT_ERROR",
            extra_data={
                "field": field,
                "current_size": current_size,
                "max_size": max_size,
            },
        )


class ErrorReportInvalidTypeError(APIException):
    """Неверный тип ошибки в отчете"""

    def __init__(self, error_type: str, valid_types: list):
        super().__init__(
            status_code=400,
            detail=f"Invalid error type: {error_type}. Valid: {', '.join(valid_types)}",
            error_code="ERROR_REPORT_INVALID_TYPE",
            extra_data={"error_type": error_type, "valid_types": valid_types},
        )


class ErrorReportInvalidSeverityError(APIException):
    """Неверный уровень серьезности ошибки"""

    def __init__(self, severity: str, valid_severities: list):
        super().__init__(
            status_code=400,
            detail=f"Invalid error severity: {severity}. Valid: {', '.join(valid_severities)}",
            error_code="ERROR_REPORT_INVALID_SEVERITY",
            extra_data={
                "severity": severity,
                "valid_severities": valid_severities,
            },
        )


class ErrorReportTimeoutError(APIException):
    """Превышено время ожидания обработки отчета об ошибке"""

    def __init__(self, report_id: str, timeout_type: str, timeout_hours: int):
        super().__init__(
            status_code=408,
            detail=f"Error report {timeout_type} timeout exceeded: {timeout_hours} hours for {report_id}",
            error_code="ERROR_REPORT_TIMEOUT_ERROR",
            extra_data={
                "report_id": report_id,
                "timeout_type": timeout_type,
                "timeout_hours": timeout_hours,
            },
        )


class ErrorReportExportError(APIException):
    """Ошибка экспорта отчетов об ошибках"""

    def __init__(
        self, format: str, message: str = "Error reports export failed"
    ):
        super().__init__(
            status_code=500,
            detail=f"{message}: {format}",
            error_code="ERROR_REPORT_EXPORT_ERROR",
            extra_data={"format": format, "message": message},
        )


class ErrorReportImportError(APIException):
    """Ошибка импорта отчетов об ошибках"""

    def __init__(
        self, source: str, message: str = "Error reports import failed"
    ):
        super().__init__(
            status_code=400,
            detail=f"{message}: {source}",
            error_code="ERROR_REPORT_IMPORT_ERROR",
            extra_data={"source": source, "message": message},
        )


class ErrorReportCleanupError(APIException):
    """Ошибка очистки отчетов об ошибках"""

    def __init__(
        self,
        message: str = "Error reports cleanup failed",
        details: dict = None,
    ):
        super().__init__(
            status_code=500,
            detail=message,
            error_code="ERROR_REPORT_CLEANUP_ERROR",
            extra_data=details or {},
        )


class ErrorReportCacheError(APIException):
    """Ошибка кеширования отчетов об ошибках"""

    def __init__(
        self, operation: str, message: str = "Error reports cache error"
    ):
        super().__init__(
            status_code=500,
            detail=f"{message}: {operation}",
            error_code="ERROR_REPORT_CACHE_ERROR",
            extra_data={"operation": operation, "message": message},
        )


class ErrorReportMetricsError(APIException):
    """Ошибка метрик отчетов об ошибках"""

    def __init__(
        self, metric: str, message: str = "Error reports metrics error"
    ):
        super().__init__(
            status_code=500,
            detail=f"{message}: {metric}",
            error_code="ERROR_REPORT_METRICS_ERROR",
            extra_data={"metric": metric, "message": message},
        )


class ErrorReportNotificationError(APIException):
    """Ошибка отправки уведомления об отчете об ошибке"""

    def __init__(
        self, channel: str, message: str = "Error report notification failed"
    ):
        super().__init__(
            status_code=500,
            detail=f"{message}: {channel}",
            error_code="ERROR_REPORT_NOTIFICATION_ERROR",
            extra_data={"channel": channel, "message": message},
        )


class ErrorReportAggregationError(APIException):
    """Ошибка агрегации отчетов об ошибках"""

    def __init__(
        self,
        message: str = "Error reports aggregation failed",
        details: dict = None,
    ):
        super().__init__(
            status_code=500,
            detail=message,
            error_code="ERROR_REPORT_AGGREGATION_ERROR",
            extra_data=details or {},
        )


class ErrorReportBulkOperationError(APIException):
    """Ошибка массовой операции с отчетами об ошибках"""

    def __init__(
        self,
        operation: str,
        message: str = "Bulk operation failed",
        results: dict = None,
    ):
        extra_data = {"operation": operation, "message": message}
        if results:
            extra_data["results"] = results

        super().__init__(
            status_code=500,
            detail=f"{message}: {operation}",
            error_code="ERROR_REPORT_BULK_OPERATION_ERROR",
            extra_data=extra_data,
        )


class ErrorReportConfigurationError(APIException):
    """Ошибка конфигурации модуля отчетов об ошибках"""

    def __init__(
        self,
        config_key: str,
        message: str = "Error reporting configuration error",
    ):
        super().__init__(
            status_code=500,
            detail=f"{message}: {config_key}",
            error_code="ERROR_REPORT_CONFIGURATION_ERROR",
            extra_data={"config_key": config_key, "message": message},
        )


class ErrorReportIntegrationError(APIException):
    """Ошибка интеграции с внешними сервисами"""

    def __init__(
        self, service: str, message: str = "Error reporting integration failed"
    ):
        super().__init__(
            status_code=502,
            detail=f"{message}: {service}",
            error_code="ERROR_REPORT_INTEGRATION_ERROR",
            extra_data={"service": service, "message": message},
        )


class ErrorReportSecurityError(APIException):
    """Ошибка безопасности в отчетах об ошибках"""

    def __init__(
        self,
        message: str = "Error reporting security error",
        details: dict = None,
    ):
        super().__init__(
            status_code=403,
            detail=message,
            error_code="ERROR_REPORT_SECURITY_ERROR",
            extra_data=details or {},
        )


# Экспорт всех исключений
__all__ = [
    "ErrorReportingError",
    "ErrorReportNotFoundError",
    "ErrorReportValidationError",
    "ErrorReportAlreadyAcknowledgedError",
    "ErrorReportAlreadyResolvedError",
    "ErrorReportNotAcknowledgedError",
    "ErrorReportAccessDeniedError",
    "ErrorReportLimitExceededError",
    "ErrorReportSizeLimitError",
    "ErrorReportInvalidTypeError",
    "ErrorReportInvalidSeverityError",
    "ErrorReportTimeoutError",
    "ErrorReportExportError",
    "ErrorReportImportError",
    "ErrorReportCleanupError",
    "ErrorReportCacheError",
    "ErrorReportMetricsError",
    "ErrorReportNotificationError",
    "ErrorReportAggregationError",
    "ErrorReportBulkOperationError",
    "ErrorReportConfigurationError",
    "ErrorReportIntegrationError",
    "ErrorReportSecurityError",
]
