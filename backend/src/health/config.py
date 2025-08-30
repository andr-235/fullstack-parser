"""
Конфигурация модуля Health

Содержит настройки специфичные для модуля проверки здоровья системы
"""

from typing import Optional, Dict, Any, List

from ..config import settings


class HealthConfig:
    """Конфигурация для модуля Health"""

    # Основные настройки модуля
    ENABLED = True
    CACHE_ENABLED = True
    METRICS_ENABLED = True
    NOTIFICATIONS_ENABLED = False

    # Настройки проверок здоровья
    CHECK_INTERVAL = 30  # seconds
    CHECK_TIMEOUT = 10  # seconds
    CACHE_TTL = 60  # seconds
    HISTORY_RETENTION = 3600  # seconds

    # Настройки компонентов
    COMPONENTS_TO_CHECK = [
        "database",
        "redis",
        "vk_api",
        "memory",
        "disk",
        "cpu",
        "process",
    ]

    # Критические компоненты (без которых система не готова)
    CRITICAL_COMPONENTS = ["database", "process"]

    # Опциональные компоненты
    OPTIONAL_COMPONENTS = ["redis", "vk_api", "cache"]

    # Пороги для метрик
    MEMORY_CRITICAL_THRESHOLD = 90.0
    MEMORY_WARNING_THRESHOLD = 80.0
    DISK_CRITICAL_THRESHOLD = 95.0
    DISK_WARNING_THRESHOLD = 85.0
    CPU_CRITICAL_THRESHOLD = 95.0
    CPU_WARNING_THRESHOLD = 80.0
    RESPONSE_TIME_CRITICAL_MS = 5000
    RESPONSE_TIME_WARNING_MS = 1000

    # Настройки повторных попыток
    RETRY_ENABLED = True
    RETRY_MAX_ATTEMPTS = 3
    RETRY_BACKOFF_FACTOR = 2.0
    RETRY_MAX_DELAY = 30.0

    # Настройки кеширования
    CACHE_PREFIX = "health"
    CACHE_STATUS_TTL = 30
    CACHE_COMPONENT_TTL = 60
    CACHE_METRICS_TTL = 300

    # Настройки метрик
    METRICS_PREFIX = "health"
    METRICS_UPDATE_INTERVAL = 60

    # Настройки логирования
    LOG_LEVEL = "INFO"
    LOG_HEALTHY_EVENTS = False  # Не логировать успешные проверки
    LOG_DEGRADED_EVENTS = True
    LOG_UNHEALTHY_EVENTS = True

    # Настройки экспорта
    EXPORT_FORMATS = ["json", "prometheus"]
    EXPORT_INCLUDE_HISTORY = True
    EXPORT_MAX_HISTORY_ITEMS = 100

    # Настройки уведомлений
    NOTIFICATION_ON_FAILURE = True
    NOTIFICATION_ON_RECOVERY = True
    NOTIFICATION_CHANNELS = ["log"]
    NOTIFICATION_THROTTLE_SECONDS = 300  # 5 минут между уведомлениями

    # Настройки для Kubernetes
    K8S_MODE_ENABLED = False
    READINESS_CHECK_STRICT = True  # Строгая проверка готовности
    LIVENESS_CHECK_STRICT = False  # Мягкая проверка живости

    # Настройки для Prometheus
    PROMETHEUS_ENABLED = False
    PROMETHEUS_METRICS_PREFIX = "vk_comments_parser"

    # Настройки зависимостей
    DEPENDENCY_CHECKS_ENABLED = True
    DEPENDENCY_TIMEOUT = 5.0

    # Настройки базы данных
    DATABASE_CHECK_ENABLED = True
    DATABASE_CHECK_QUERY = "SELECT 1"
    DATABASE_CHECK_TIMEOUT = 5.0

    # Настройки Redis
    REDIS_CHECK_ENABLED = False
    REDIS_CHECK_KEY = "health:check"
    REDIS_CHECK_TIMEOUT = 2.0

    # Настройки VK API
    VK_API_CHECK_ENABLED = False
    VK_API_CHECK_ENDPOINT = "/api/v1/vk-api/health"
    VK_API_CHECK_TIMEOUT = 10.0

    # Настройки системы
    SYSTEM_CHECK_ENABLED = True
    SYSTEM_MEMORY_CHECK_ENABLED = True
    SYSTEM_DISK_CHECK_ENABLED = True
    SYSTEM_CPU_CHECK_ENABLED = True
    SYSTEM_NETWORK_CHECK_ENABLED = False

    @classmethod
    def get_check_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию проверок здоровья"""
        return {
            "interval": cls.CHECK_INTERVAL,
            "timeout": cls.CHECK_TIMEOUT,
            "components": cls.COMPONENTS_TO_CHECK,
            "critical_components": cls.CRITICAL_COMPONENTS,
            "optional_components": cls.OPTIONAL_COMPONENTS,
        }

    @classmethod
    def get_thresholds_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию порогов"""
        return {
            "memory_critical": cls.MEMORY_CRITICAL_THRESHOLD,
            "memory_warning": cls.MEMORY_WARNING_THRESHOLD,
            "disk_critical": cls.DISK_CRITICAL_THRESHOLD,
            "disk_warning": cls.DISK_WARNING_THRESHOLD,
            "cpu_critical": cls.CPU_CRITICAL_THRESHOLD,
            "cpu_warning": cls.CPU_WARNING_THRESHOLD,
            "response_time_critical_ms": cls.RESPONSE_TIME_CRITICAL_MS,
            "response_time_warning_ms": cls.RESPONSE_TIME_WARNING_MS,
        }

    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию кеширования"""
        return {
            "enabled": cls.CACHE_ENABLED,
            "prefix": cls.CACHE_PREFIX,
            "status_ttl": cls.CACHE_STATUS_TTL,
            "component_ttl": cls.CACHE_COMPONENT_TTL,
            "metrics_ttl": cls.CACHE_METRICS_TTL,
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
    def get_notification_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию уведомлений"""
        return {
            "enabled": cls.NOTIFICATIONS_ENABLED,
            "on_failure": cls.NOTIFICATION_ON_FAILURE,
            "on_recovery": cls.NOTIFICATION_ON_RECOVERY,
            "channels": cls.NOTIFICATION_CHANNELS,
            "throttle_seconds": cls.NOTIFICATION_THROTTLE_SECONDS,
        }

    @classmethod
    def get_kubernetes_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию для Kubernetes"""
        return {
            "mode_enabled": cls.K8S_MODE_ENABLED,
            "readiness_strict": cls.READINESS_CHECK_STRICT,
            "liveness_strict": cls.LIVENESS_CHECK_STRICT,
        }

    @classmethod
    def get_prometheus_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию для Prometheus"""
        return {
            "enabled": cls.PROMETHEUS_ENABLED,
            "metrics_prefix": cls.PROMETHEUS_METRICS_PREFIX,
        }

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию проверки базы данных"""
        return {
            "enabled": cls.DATABASE_CHECK_ENABLED,
            "query": cls.DATABASE_CHECK_QUERY,
            "timeout": cls.DATABASE_CHECK_TIMEOUT,
        }

    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию проверки Redis"""
        return {
            "enabled": cls.REDIS_CHECK_ENABLED,
            "key": cls.REDIS_CHECK_KEY,
            "timeout": cls.REDIS_CHECK_TIMEOUT,
        }

    @classmethod
    def get_vk_api_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию проверки VK API"""
        return {
            "enabled": cls.VK_API_CHECK_ENABLED,
            "endpoint": cls.VK_API_CHECK_ENDPOINT,
            "timeout": cls.VK_API_CHECK_TIMEOUT,
        }

    @classmethod
    def get_system_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию системных проверок"""
        return {
            "enabled": cls.SYSTEM_CHECK_ENABLED,
            "memory_enabled": cls.SYSTEM_MEMORY_CHECK_ENABLED,
            "disk_enabled": cls.SYSTEM_DISK_CHECK_ENABLED,
            "cpu_enabled": cls.SYSTEM_CPU_CHECK_ENABLED,
            "network_enabled": cls.SYSTEM_NETWORK_CHECK_ENABLED,
        }

    @classmethod
    def is_component_required(cls, component: str) -> bool:
        """Проверить, является ли компонент обязательным"""
        return component in cls.CRITICAL_COMPONENTS

    @classmethod
    def is_component_optional(cls, component: str) -> bool:
        """Проверить, является ли компонент опциональным"""
        return component in cls.OPTIONAL_COMPONENTS

    @classmethod
    def get_all_components(cls) -> List[str]:
        """Получить список всех компонентов для проверки"""
        return cls.COMPONENTS_TO_CHECK.copy()

    @classmethod
    def should_notify_on_status_change(
        cls, old_status: str, new_status: str
    ) -> bool:
        """Определить, нужно ли отправлять уведомление при изменении статуса"""
        if not cls.NOTIFICATIONS_ENABLED:
            return False

        # Всегда уведомлять о переходе в нерабочее состояние
        if (
            new_status in ["unhealthy", "critical"]
            and cls.NOTIFICATION_ON_FAILURE
        ):
            return True

        # Уведомлять о восстановлении из нерабочего состояния
        if (
            old_status in ["unhealthy", "critical"]
            and new_status in ["healthy", "degraded"]
            and cls.NOTIFICATION_ON_RECOVERY
        ):
            return True

        return False


# Экземпляр конфигурации
health_config = HealthConfig()


# Экспорт
__all__ = [
    "HealthConfig",
    "health_config",
]
