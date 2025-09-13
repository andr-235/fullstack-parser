"""
Константы модуля Health
"""

# Статусы здоровья
HEALTHY = "healthy"
DEGRADED = "degraded"
UNHEALTHY = "unhealthy"
UNKNOWN = "unknown"
READY = "ready"
NOT_READY = "not_ready"
ALIVE = "alive"
DEAD = "dead"
WARNING = "warning"
CRITICAL = "critical"

# Компоненты системы
DATABASE = "database"
MEMORY = "memory"
DISK = "disk"
CPU = "cpu"
PROCESS = "process"

# Пороги для метрик
MEMORY_CRITICAL = 90.0  # %
MEMORY_WARNING = 80.0   # %
DISK_CRITICAL = 95.0    # %
DISK_WARNING = 85.0     # %
CPU_CRITICAL = 95.0     # %
CPU_WARNING = 80.0      # %

# Временные интервалы
CHECK_TIMEOUT = 10  # seconds
CACHE_TTL = 60      # seconds

# Максимальные значения
MAX_HISTORY = 100
MAX_RESPONSE_TIME_MS = 5000  # 5 seconds

# Коды ошибок
ERROR_TIMEOUT = "TIMEOUT"
ERROR_CONNECTION_FAILED = "CONNECTION_FAILED"
ERROR_SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

# Сообщения
SUCCESS_CHECK_PASSED = "Health check passed"
ERROR_CHECK_FAILED = "Health check failed"

# Ключи кеша
CACHE_STATUS = "health:status"
CACHE_COMPONENT = "health:component:{component}"
CACHE_HISTORY = "health:history"

# TTL кеша
STATUS_TTL = 30
COMPONENT_TTL = 60
METRICS_TTL = 300

# Метрики
METRIC_CHECKS_TOTAL = "health.checks.total"
METRIC_CHECKS_SUCCESSFUL = "health.checks.successful"
METRIC_CHECKS_FAILED = "health.checks.failed"
METRIC_RESPONSE_TIME = "health.response_time"
METRIC_UPTIME = "health.system.uptime"

# События
EVENT_STATUS_CHANGED = "health.status.changed"
EVENT_COMPONENT_FAILED = "health.component.failed"
EVENT_COMPONENT_RECOVERED = "health.component.recovered"

# Уровни логирования
LOG_HEALTHY = "INFO"
LOG_DEGRADED = "WARNING"
LOG_UNHEALTHY = "ERROR"
LOG_CRITICAL = "CRITICAL"

# Форматы экспорта
EXPORT_JSON = "json"
EXPORT_PROMETHEUS = "prometheus"

# Настройки повторных попыток
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2.0
RETRY_MAX_DELAY = 30.0

# Kubernetes пути
K8S_READINESS_PATH = "/health/ready"
K8S_LIVENESS_PATH = "/health/live"

# Prometheus настройки
PROMETHEUS_METRICS_PATH = "/metrics"
PROMETHEUS_PREFIX = "vk_comments_parser"


__all__ = [
    # Статусы
    "HEALTHY", "DEGRADED", "UNHEALTHY", "UNKNOWN",
    "READY", "NOT_READY", "ALIVE", "DEAD",
    "WARNING", "CRITICAL",
    # Компоненты
    "DATABASE", "MEMORY", "DISK", "CPU", "PROCESS",
    # Пороги
    "MEMORY_CRITICAL", "MEMORY_WARNING",
    "DISK_CRITICAL", "DISK_WARNING",
    "CPU_CRITICAL", "CPU_WARNING",
    # Интервалы
    "CHECK_TIMEOUT", "CACHE_TTL",
    # Максимальные значения
    "MAX_HISTORY", "MAX_RESPONSE_TIME_MS",
    # Ошибки
    "ERROR_TIMEOUT", "ERROR_CONNECTION_FAILED", "ERROR_SERVICE_UNAVAILABLE",
    # Сообщения
    "SUCCESS_CHECK_PASSED", "ERROR_CHECK_FAILED",
    # Кеш
    "CACHE_STATUS", "CACHE_COMPONENT", "CACHE_HISTORY",
    "STATUS_TTL", "COMPONENT_TTL", "METRICS_TTL",
    # Метрики
    "METRIC_CHECKS_TOTAL", "METRIC_CHECKS_SUCCESSFUL", "METRIC_CHECKS_FAILED",
    "METRIC_RESPONSE_TIME", "METRIC_UPTIME",
    # События
    "EVENT_STATUS_CHANGED", "EVENT_COMPONENT_FAILED", "EVENT_COMPONENT_RECOVERED",
    # Логирование
    "LOG_HEALTHY", "LOG_DEGRADED", "LOG_UNHEALTHY", "LOG_CRITICAL",
    # Экспорт
    "EXPORT_JSON", "EXPORT_PROMETHEUS",
    # Повторные попытки
    "RETRY_MAX_ATTEMPTS", "RETRY_BACKOFF_FACTOR", "RETRY_MAX_DELAY",
    # Kubernetes
    "K8S_READINESS_PATH", "K8S_LIVENESS_PATH",
    # Prometheus
    "PROMETHEUS_METRICS_PATH", "PROMETHEUS_PREFIX",
]
