"""
Конфигурация модуля Error Reporting

Содержит настройки специфичные для модуля отчетов об ошибках
"""

from typing import Optional, Dict, Any, List

from ..config import settings


class ErrorReportingConfig:
    """Конфигурация для модуля Error Reporting"""

    # Основные настройки модуля
    ENABLED = True
    AUTO_CAPTURE_ENABLED = True
    CACHE_ENABLED = True
    METRICS_ENABLED = True
    NOTIFICATIONS_ENABLED = False

    # Настройки хранения
    MAX_REPORTS_TOTAL = 100000
    RETENTION_DAYS = 365
    CLEANUP_ENABLED = True
    CLEANUP_INTERVAL_HOURS = 24
    CLEANUP_BATCH_SIZE = 1000

    # Настройки производительности
    MAX_MESSAGE_LENGTH = 10000
    MAX_STACK_TRACE_LENGTH = 50000
    MAX_CONTEXT_SIZE = 50000
    MAX_RESOLUTION_NOTES_LENGTH = 10000

    # Настройки пагинации
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    MAX_PAGES = 1000

    # Настройки кеширования
    CACHE_PREFIX = "error_reporting"
    CACHE_REPORT_TTL = 300  # 5 минут
    CACHE_STATS_TTL = 1800  # 30 минут
    CACHE_LIST_TTL = 60  # 1 минута

    # Настройки таймаутов
    ACKNOWLEDGE_TIMEOUT_HOURS = 24
    RESOLVE_TIMEOUT_HOURS = 168  # 7 дней
    PROCESSING_TIMEOUT_SECONDS = 30

    # Настройки серьезности
    DEFAULT_SEVERITY = "medium"
    CRITICAL_SEVERITIES = ["high", "critical"]
    AUTO_ESCALATE_SEVERITIES = ["critical"]

    # Настройки типов ошибок
    TRACKED_ERROR_TYPES = [
        "database",
        "api",
        "network",
        "authentication",
        "authorization",
        "business_logic",
        "system",
    ]

    # Настройки агрегации
    AGGREGATION_ENABLED = True
    AGGREGATION_WINDOW_MINUTES = 5
    SIMILARITY_THRESHOLD = 0.8
    MAX_SIMILAR_REPORTS = 100

    # Настройки уведомлений
    NOTIFICATION_ON_CRITICAL = True
    NOTIFICATION_ON_TIMEOUT = True
    NOTIFICATION_CHANNELS = ["log"]
    NOTIFICATION_THROTTLE_MINUTES = 5

    # Настройки экспорта
    EXPORT_FORMATS = ["json", "csv", "xml"]
    EXPORT_MAX_RECORDS = 10000
    EXPORT_COMPRESSION = True
    EXPORT_INCLUDE_STACK_TRACES = True

    # Настройки логирования
    LOGGING_ENABLED = True
    LOG_LEVEL = "WARNING"
    LOG_STACK_TRACES = True
    LOG_CONTEXT = True

    # Настройки фильтрации
    FILTER_SENSITIVE_DATA = True
    SENSITIVE_KEYS = [
        "password",
        "token",
        "secret",
        "key",
        "authorization",
        "api_key",
        "access_token",
        "refresh_token",
    ]

    # Настройки интеграции
    SENTRY_ENABLED = False
    SENTRY_DSN = None
    SLACK_ENABLED = False
    SLACK_WEBHOOK_URL = None
    EMAIL_ENABLED = False
    EMAIL_RECIPIENTS = []

    # Настройки метрик
    METRICS_PREFIX = "error_reporting"
    METRICS_UPDATE_INTERVAL = 60

    # Настройки для разных сред
    PRODUCTION_MODE = False
    DEBUG_MODE = False

    @classmethod
    def get_storage_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию хранения"""
        return {
            "max_reports_total": cls.MAX_REPORTS_TOTAL,
            "retention_days": cls.RETENTION_DAYS,
            "cleanup_enabled": cls.CLEANUP_ENABLED,
            "cleanup_interval_hours": cls.CLEANUP_INTERVAL_HOURS,
            "cleanup_batch_size": cls.CLEANUP_BATCH_SIZE,
        }

    @classmethod
    def get_performance_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию производительности"""
        return {
            "max_message_length": cls.MAX_MESSAGE_LENGTH,
            "max_stack_trace_length": cls.MAX_STACK_TRACE_LENGTH,
            "max_context_size": cls.MAX_CONTEXT_SIZE,
            "max_resolution_notes_length": cls.MAX_RESOLUTION_NOTES_LENGTH,
            "processing_timeout_seconds": cls.PROCESSING_TIMEOUT_SECONDS,
        }

    @classmethod
    def get_pagination_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию пагинации"""
        return {
            "default_page_size": cls.DEFAULT_PAGE_SIZE,
            "max_page_size": cls.MAX_PAGE_SIZE,
            "max_pages": cls.MAX_PAGES,
        }

    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию кеширования"""
        return {
            "enabled": cls.CACHE_ENABLED,
            "prefix": cls.CACHE_PREFIX,
            "report_ttl": cls.CACHE_REPORT_TTL,
            "stats_ttl": cls.CACHE_STATS_TTL,
            "list_ttl": cls.CACHE_LIST_TTL,
        }

    @classmethod
    def get_timeout_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию таймаутов"""
        return {
            "acknowledge_timeout_hours": cls.ACKNOWLEDGE_TIMEOUT_HOURS,
            "resolve_timeout_hours": cls.RESOLVE_TIMEOUT_HOURS,
        }

    @classmethod
    def get_severity_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию серьезности"""
        return {
            "default_severity": cls.DEFAULT_SEVERITY,
            "critical_severities": cls.CRITICAL_SEVERITIES,
            "auto_escalate_severities": cls.AUTO_ESCALATE_SEVERITIES,
        }

    @classmethod
    def get_aggregation_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию агрегации"""
        return {
            "enabled": cls.AGGREGATION_ENABLED,
            "window_minutes": cls.AGGREGATION_WINDOW_MINUTES,
            "similarity_threshold": cls.SIMILARITY_THRESHOLD,
            "max_similar_reports": cls.MAX_SIMILAR_REPORTS,
        }

    @classmethod
    def get_notification_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию уведомлений"""
        return {
            "enabled": cls.NOTIFICATIONS_ENABLED,
            "on_critical": cls.NOTIFICATION_ON_CRITICAL,
            "on_timeout": cls.NOTIFICATION_ON_TIMEOUT,
            "channels": cls.NOTIFICATION_CHANNELS,
            "throttle_minutes": cls.NOTIFICATION_THROTTLE_MINUTES,
        }

    @classmethod
    def get_export_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию экспорта"""
        return {
            "formats": cls.EXPORT_FORMATS,
            "max_records": cls.EXPORT_MAX_RECORDS,
            "compression": cls.EXPORT_COMPRESSION,
            "include_stack_traces": cls.EXPORT_INCLUDE_STACK_TRACES,
        }

    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию логирования"""
        return {
            "enabled": cls.LOGGING_ENABLED,
            "level": cls.LOG_LEVEL,
            "log_stack_traces": cls.LOG_STACK_TRACES,
            "log_context": cls.LOG_CONTEXT,
        }

    @classmethod
    def get_integration_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию интеграции"""
        return {
            "sentry_enabled": cls.SENTRY_ENABLED,
            "sentry_dsn": cls.SENTRY_DSN,
            "slack_enabled": cls.SLACK_ENABLED,
            "slack_webhook_url": cls.SLACK_WEBHOOK_URL,
            "email_enabled": cls.EMAIL_ENABLED,
            "email_recipients": cls.EMAIL_RECIPIENTS,
        }

    @classmethod
    def get_metrics_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию метрик"""
        return {
            "enabled": cls.METRICS_ENABLED,
            "prefix": cls.METRICS_PREFIX,
            "update_interval": cls.METRICS_UPDATE_INTERVAL,
        }

    @classmethod
    def is_critical_severity(cls, severity: str) -> bool:
        """Проверить, является ли серьезность критической"""
        return severity in cls.CRITICAL_SEVERITIES

    @classmethod
    def should_auto_escalate(cls, severity: str) -> bool:
        """Проверить, нужно ли автоматически эскалировать"""
        return severity in cls.AUTO_ESCALATE_SEVERITIES

    @classmethod
    def is_tracked_error_type(cls, error_type: str) -> bool:
        """Проверить, отслеживается ли тип ошибки"""
        return error_type in cls.TRACKED_ERROR_TYPES

    @classmethod
    def should_filter_sensitive_data(cls) -> bool:
        """Проверить, нужно ли фильтровать чувствительные данные"""
        return cls.FILTER_SENSITIVE_DATA

    @classmethod
    def get_sensitive_keys(cls) -> List[str]:
        """Получить список чувствительных ключей"""
        return cls.SENSITIVE_KEYS.copy()

    @classmethod
    def is_production_mode(cls) -> bool:
        """Проверить, включен ли режим продакшена"""
        return cls.PRODUCTION_MODE

    @classmethod
    def is_debug_mode(cls) -> bool:
        """Проверить, включен ли режим отладки"""
        return cls.DEBUG_MODE


# Экземпляр конфигурации
error_reporting_config = ErrorReportingConfig()


# Экспорт
__all__ = [
    "ErrorReportingConfig",
    "error_reporting_config",
]
