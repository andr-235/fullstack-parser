"""
Константы модуля Parser

Содержит все константы используемые в модуле парсера
"""

# Статусы задач
TASK_STATUS_PENDING = "pending"
TASK_STATUS_RUNNING = "running"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"
TASK_STATUS_STOPPED = "stopped"

# Допустимые статусы задач
ALLOWED_TASK_STATUSES = [
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_STOPPED,
]

# Приоритеты задач
TASK_PRIORITY_LOW = "low"
TASK_PRIORITY_NORMAL = "normal"
TASK_PRIORITY_HIGH = "high"

# Допустимые приоритеты
ALLOWED_TASK_PRIORITIES = [
    TASK_PRIORITY_LOW,
    TASK_PRIORITY_NORMAL,
    TASK_PRIORITY_HIGH,
]

# Типы операций парсинга
PARSE_OPERATION_POSTS = "posts"
PARSE_OPERATION_COMMENTS = "comments"
PARSE_OPERATION_GROUP_INFO = "group_info"
PARSE_OPERATION_USER_INFO = "user_info"

# Допустимые операции
ALLOWED_PARSE_OPERATIONS = [
    PARSE_OPERATION_POSTS,
    PARSE_OPERATION_COMMENTS,
    PARSE_OPERATION_GROUP_INFO,
    PARSE_OPERATION_USER_INFO,
]

# Источники данных
DATA_SOURCE_VK_API = "vk_api"
DATA_SOURCE_CACHE = "cache"
DATA_SOURCE_DATABASE = "database"

# Типы ошибок
ERROR_TYPE_VK_API = "vk_api_error"
ERROR_TYPE_NETWORK = "network_error"
ERROR_TYPE_VALIDATION = "validation_error"
ERROR_TYPE_TIMEOUT = "timeout_error"
ERROR_TYPE_RATE_LIMIT = "rate_limit_error"
ERROR_TYPE_UNKNOWN = "unknown_error"

# Сообщения об ошибках
ERROR_TASK_NOT_FOUND = "Задача не найдена"
ERROR_INVALID_TASK_ID = "Неверный ID задачи"
ERROR_INVALID_GROUP_ID = "Неверный ID группы VK"
ERROR_INVALID_POST_ID = "Неверный ID поста"
ERROR_INVALID_PRIORITY = "Неверный приоритет задачи"
ERROR_INVALID_STATUS = "Неверный статус задачи"
ERROR_TOO_MANY_GROUPS = "Слишком много групп в запросе"
ERROR_PARSING_FAILED = "Парсинг завершен с ошибками"
ERROR_VK_API_UNAVAILABLE = "VK API недоступен"
ERROR_RATE_LIMIT_EXCEEDED = "Превышен лимит запросов к VK API"

# Сообщения об успехе
SUCCESS_PARSING_STARTED = "Парсинг успешно запущен"
SUCCESS_PARSING_COMPLETED = "Парсинг успешно завершен"
SUCCESS_TASK_STOPPED = "Задача успешно остановлена"
SUCCESS_DATA_SAVED = "Данные успешно сохранены"

# Названия полей для API
API_FIELD_TASK_ID = "task_id"
API_FIELD_STATUS = "status"
API_FIELD_GROUP_IDS = "group_ids"
API_FIELD_MAX_POSTS = "max_posts"
API_FIELD_MAX_COMMENTS = "max_comments_per_post"
API_FIELD_FORCE_REPARSE = "force_reparse"
API_FIELD_PRIORITY = "priority"
API_FIELD_PROGRESS = "progress"
API_FIELD_POSTS_FOUND = "posts_found"
API_FIELD_COMMENTS_FOUND = "comments_found"
API_FIELD_ERRORS = "errors"
API_FIELD_CREATED_AT = "created_at"
API_FIELD_STARTED_AT = "started_at"
API_FIELD_COMPLETED_AT = "completed_at"
API_FIELD_DURATION = "duration"

# Максимальные значения
MAX_GROUP_IDS_PER_REQUEST = 100
MAX_POSTS_PER_GROUP = 1000
MAX_COMMENTS_PER_POST = 1000
MAX_TASK_TIMEOUT = 3600  # 1 час
MAX_REQUEST_TIMEOUT = 30
MAX_CONNECTION_TIMEOUT = 10

# Настройки кеширования
CACHE_KEY_TASK = "parser:task:{task_id}"
CACHE_KEY_GROUP_DATA = "parser:group:{group_id}:{data_type}"
CACHE_KEY_VK_API_RESPONSE = "parser:vk_api:{method}:{params_hash}"
CACHE_KEY_STATS = "parser:stats"

# Таймауты кеша
CACHE_TASK_TTL = 3600  # 1 час
CACHE_GROUP_DATA_TTL = 1800  # 30 минут
CACHE_VK_API_TTL = 300  # 5 минут
CACHE_STATS_TTL = 60  # 1 минута

# Настройки очередей
QUEUE_MAX_SIZE = 1000
QUEUE_PRIORITY_WEIGHTS = {
    TASK_PRIORITY_LOW: 1,
    TASK_PRIORITY_NORMAL: 2,
    TASK_PRIORITY_HIGH: 3,
}

# Настройки повторных попыток
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5
RETRY_BACKOFF_FACTOR = 2

# VK API константы
VK_API_BASE_URL = "https://api.vk.com/method"
VK_API_VERSION = "5.199"
VK_API_MAX_REQUESTS_PER_SECOND = 3
VK_API_POSTS_FIELDS = "id,text,date,likes,reposts,comments"
VK_API_COMMENTS_FIELDS = "id,text,date,likes,thread"
VK_API_GROUP_FIELDS = (
    "id,name,screen_name,description,members_count,photo_200,is_closed"
)
VK_API_USER_FIELDS = "id,first_name,last_name,screen_name,photo_100"

# Настройки логирования
LOG_REQUEST_FORMAT = "VK API Request: {method} - {url}"
LOG_RESPONSE_FORMAT = "VK API Response: {method} - Status: {status}"
LOG_ERROR_FORMAT = "VK API Error: {method} - {error}"
LOG_PARSING_FORMAT = "Parsing: Group {group_id} - {posts_found} posts, {comments_found} comments"

# Метрики и статистика
METRIC_TASKS_CREATED = "parser.tasks.created"
METRIC_TASKS_COMPLETED = "parser.tasks.completed"
METRIC_TASKS_FAILED = "parser.tasks.failed"
METRIC_POSTS_FOUND = "parser.posts.found"
METRIC_COMMENTS_FOUND = "parser.comments.found"
METRIC_API_REQUESTS = "parser.api.requests"
METRIC_API_ERRORS = "parser.api.errors"

# Временные интервалы (в секундах)
INTERVAL_HEALTH_CHECK = 60
INTERVAL_STATS_UPDATE = 300
INTERVAL_CACHE_CLEANUP = 3600

# Размеры батчей
BATCH_SIZE_POSTS = 100
BATCH_SIZE_COMMENTS = 100
BATCH_SIZE_SAVE = 50


# Экспорт всех констант
__all__ = [
    # Статусы задач
    "TASK_STATUS_PENDING",
    "TASK_STATUS_RUNNING",
    "TASK_STATUS_COMPLETED",
    "TASK_STATUS_FAILED",
    "TASK_STATUS_STOPPED",
    "ALLOWED_TASK_STATUSES",
    # Приоритеты
    "TASK_PRIORITY_LOW",
    "TASK_PRIORITY_NORMAL",
    "TASK_PRIORITY_HIGH",
    "ALLOWED_TASK_PRIORITIES",
    # Операции
    "PARSE_OPERATION_POSTS",
    "PARSE_OPERATION_COMMENTS",
    "PARSE_OPERATION_GROUP_INFO",
    "PARSE_OPERATION_USER_INFO",
    "ALLOWED_PARSE_OPERATIONS",
    # Источники данных
    "DATA_SOURCE_VK_API",
    "DATA_SOURCE_CACHE",
    "DATA_SOURCE_DATABASE",
    # Типы ошибок
    "ERROR_TYPE_VK_API",
    "ERROR_TYPE_NETWORK",
    "ERROR_TYPE_VALIDATION",
    "ERROR_TYPE_TIMEOUT",
    "ERROR_TYPE_RATE_LIMIT",
    "ERROR_TYPE_UNKNOWN",
    # Сообщения об ошибках
    "ERROR_TASK_NOT_FOUND",
    "ERROR_INVALID_TASK_ID",
    "ERROR_INVALID_GROUP_ID",
    "ERROR_INVALID_POST_ID",
    "ERROR_INVALID_PRIORITY",
    "ERROR_INVALID_STATUS",
    "ERROR_TOO_MANY_GROUPS",
    "ERROR_PARSING_FAILED",
    "ERROR_VK_API_UNAVAILABLE",
    "ERROR_RATE_LIMIT_EXCEEDED",
    # Сообщения об успехе
    "SUCCESS_PARSING_STARTED",
    "SUCCESS_PARSING_COMPLETED",
    "SUCCESS_TASK_STOPPED",
    "SUCCESS_DATA_SAVED",
    # API поля
    "API_FIELD_TASK_ID",
    "API_FIELD_STATUS",
    "API_FIELD_GROUP_IDS",
    "API_FIELD_MAX_POSTS",
    "API_FIELD_MAX_COMMENTS",
    "API_FIELD_FORCE_REPARSE",
    "API_FIELD_PRIORITY",
    "API_FIELD_PROGRESS",
    "API_FIELD_POSTS_FOUND",
    "API_FIELD_COMMENTS_FOUND",
    "API_FIELD_ERRORS",
    "API_FIELD_CREATED_AT",
    "API_FIELD_STARTED_AT",
    "API_FIELD_COMPLETED_AT",
    "API_FIELD_DURATION",
    # Максимальные значения
    "MAX_GROUP_IDS_PER_REQUEST",
    "MAX_POSTS_PER_GROUP",
    "MAX_COMMENTS_PER_POST",
    "MAX_TASK_TIMEOUT",
    "MAX_REQUEST_TIMEOUT",
    "MAX_CONNECTION_TIMEOUT",
    # Кеширование
    "CACHE_KEY_TASK",
    "CACHE_KEY_GROUP_DATA",
    "CACHE_KEY_VK_API_RESPONSE",
    "CACHE_KEY_STATS",
    "CACHE_TASK_TTL",
    "CACHE_GROUP_DATA_TTL",
    "CACHE_VK_API_TTL",
    "CACHE_STATS_TTL",
    # Очереди
    "QUEUE_MAX_SIZE",
    "QUEUE_PRIORITY_WEIGHTS",
    # Повторные попытки
    "MAX_RETRY_ATTEMPTS",
    "RETRY_DELAY_SECONDS",
    "RETRY_BACKOFF_FACTOR",
    # VK API
    "VK_API_BASE_URL",
    "VK_API_VERSION",
    "VK_API_MAX_REQUESTS_PER_SECOND",
    "VK_API_POSTS_FIELDS",
    "VK_API_COMMENTS_FIELDS",
    "VK_API_GROUP_FIELDS",
    "VK_API_USER_FIELDS",
    # Логирование
    "LOG_REQUEST_FORMAT",
    "LOG_RESPONSE_FORMAT",
    "LOG_ERROR_FORMAT",
    "LOG_PARSING_FORMAT",
    # Метрики
    "METRIC_TASKS_CREATED",
    "METRIC_TASKS_COMPLETED",
    "METRIC_TASKS_FAILED",
    "METRIC_POSTS_FOUND",
    "METRIC_COMMENTS_FOUND",
    "METRIC_API_REQUESTS",
    "METRIC_API_ERRORS",
    # Интервалы
    "INTERVAL_HEALTH_CHECK",
    "INTERVAL_STATS_UPDATE",
    "INTERVAL_CACHE_CLEANUP",
    # Батчи
    "BATCH_SIZE_POSTS",
    "BATCH_SIZE_COMMENTS",
    "BATCH_SIZE_SAVE",
]
