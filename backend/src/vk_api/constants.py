"""
Константы модуля VK API

Содержит все константы используемые в модуле работы с VK API
"""

# VK API лимиты
VK_API_MAX_REQUESTS_PER_SECOND = 3
VK_API_MAX_POSTS_PER_REQUEST = 100
VK_API_MAX_COMMENTS_PER_REQUEST = 100
VK_API_MAX_GROUPS_PER_REQUEST = 1000
VK_API_MAX_USERS_PER_REQUEST = 1000

# Таймауты
VK_API_REQUEST_TIMEOUT = 30.0
VK_API_CONNECTION_TIMEOUT = 10.0

# Rate limiting
RATE_LIMIT_WINDOW_SECONDS = 1.0
RATE_LIMIT_MAX_REQUESTS = 3

# Коды ошибок VK API
VK_ERROR_ACCESS_DENIED = 5
VK_ERROR_INVALID_REQUEST = 6
VK_ERROR_TOO_MANY_REQUESTS = 6
VK_ERROR_AUTH_FAILED = 5
VK_ERROR_PERMISSION_DENIED = 7
VK_ERROR_GROUP_ACCESS_DENIED = 203
VK_ERROR_POST_NOT_FOUND = 100
VK_ERROR_USER_NOT_FOUND = 113

# Типы объектов VK
VK_OBJECT_TYPE_POST = "post"
VK_OBJECT_TYPE_COMMENT = "comment"
VK_OBJECT_TYPE_GROUP = "group"
VK_OBJECT_TYPE_USER = "user"
VK_OBJECT_TYPE_WALL = "wall"

# Сортировка комментариев
VK_SORT_ASC = "asc"
VK_SORT_DESC = "desc"

# Типы поиска групп
VK_GROUP_TYPE_GROUP = "group"
VK_GROUP_TYPE_PAGE = "page"
VK_GROUP_TYPE_EVENT = "event"

# Статусы групп
VK_GROUP_STATUS_OPEN = "open"
VK_GROUP_STATUS_CLOSED = "closed"
VK_GROUP_STATUS_PRIVATE = "private"

# Методы VK API
VK_METHOD_WALL_GET = "wall.get"
VK_METHOD_WALL_GET_COMMENTS = "wall.getComments"
VK_METHOD_GROUPS_GET_BY_ID = "groups.getById"
VK_METHOD_GROUPS_SEARCH = "groups.search"
VK_METHOD_USERS_GET = "users.get"
VK_METHOD_GROUPS_GET_MEMBERS = "groups.getMembers"

# Параметры полей для запросов
VK_FIELDS_GROUP = (
    "id,name,screen_name,description,members_count,photo_200,is_closed,type"
)
VK_FIELDS_USER = "id,first_name,last_name,photo_100,sex,city,country"

# Ключи кеша
CACHE_KEY_GROUP_POSTS = "vk:group:{group_id}:posts:{count}:{offset}"
CACHE_KEY_POST_COMMENTS = "vk:post:{post_id}:comments:{count}:{offset}:{sort}"
CACHE_KEY_GROUP_INFO = "vk:group:{group_id}:info"
CACHE_KEY_USER_INFO = "vk:user:{user_id}:info"
CACHE_KEY_GROUP_SEARCH = "vk:search:groups:{query}:{count}:{offset}"

# TTL кеша
CACHE_GROUP_POSTS_TTL = 300  # 5 минут
CACHE_POST_COMMENTS_TTL = 600  # 10 минут
CACHE_GROUP_INFO_TTL = 3600  # 1 час
CACHE_USER_INFO_TTL = 1800  # 30 минут
CACHE_SEARCH_TTL = 1800  # 30 минут

# Сообщения об ошибках
ERROR_VK_API_REQUEST_FAILED = "VK API request failed"
ERROR_VK_API_RATE_LIMIT = "VK API rate limit exceeded"
ERROR_VK_API_AUTH = "VK API authentication failed"
ERROR_VK_API_INVALID_TOKEN = "Invalid VK API token"
ERROR_VK_API_ACCESS_DENIED = "VK API access denied"
ERROR_VK_API_INVALID_PARAMS = "Invalid VK API parameters"
ERROR_VK_API_TIMEOUT = "VK API request timeout"
ERROR_VK_API_NETWORK = "VK API network error"

# Сообщения об успехе
SUCCESS_VK_API_CONNECTED = "VK API connected successfully"
SUCCESS_VK_API_TOKEN_VALID = "VK API token is valid"
SUCCESS_VK_API_REQUEST_COMPLETED = "VK API request completed"

# Регулярные выражения
REGEX_VK_GROUP_ID = r"^(-?\d+)$"
REGEX_VK_USER_ID = r"^(\d+)$"
REGEX_VK_POST_ID = r"^(\d+)$"

# Настройки логирования
LOG_VK_API_REQUEST = "VK API Request: {method} - {params}"
LOG_VK_API_RESPONSE = "VK API Response: {method} - {response_time:.2f}s"
LOG_VK_API_ERROR = "VK API Error: {method} - {error_code}: {error_msg}"
LOG_VK_API_RATE_LIMIT = "VK API Rate Limit: waiting {wait_time:.2f}s"

# Метрики
METRIC_VK_API_REQUESTS = "vk_api.requests.total"
METRIC_VK_API_ERRORS = "vk_api.errors.total"
METRIC_VK_API_RATE_LIMITS = "vk_api.rate_limits.total"
METRIC_VK_API_RESPONSE_TIME = "vk_api.response_time"
METRIC_VK_API_REQUESTS_PER_SECOND = "vk_api.requests_per_second"

# Настройки повторов
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2.0
RETRY_MAX_DELAY = 60.0

# Настройки подключения
HTTP_MAX_CONNECTIONS = 100
HTTP_MAX_KEEPALIVE = 10
HTTP_TIMEOUT = 30.0

# Настройки прокси (если нужны)
PROXY_ENABLED = False
PROXY_LIST = []
PROXY_ROTATION_ENABLED = False

# Настройки для тестирования
TEST_MODE_ENABLED = False
TEST_MOCK_RESPONSES = {}

# Настройки версий API
VK_API_VERSION = "5.199"
VK_API_BASE_URL = "https://api.vk.com/method/"

# Настройки пользовательских агентов
USER_AGENTS = [
    "VK Comments Parser/1.0",
    "VK Data Collector/1.0",
    "VK API Client/1.0",
]

# Настройки для обработки больших объемов данных
BATCH_SIZE_GROUP_POSTS = 50
BATCH_SIZE_GROUP_COMMENTS = 25
BATCH_SIZE_USER_INFO = 100

# Настройки для обработки ошибок
ERROR_RETRY_DELAY = 1.0
ERROR_RETRY_MAX_DELAY = 60.0
ERROR_RETRY_BACKOFF = 2.0

# Настройки для мониторинга
HEALTH_CHECK_INTERVAL = 60  # секунд
HEALTH_CHECK_TIMEOUT = 5.0
HEALTH_CHECK_MAX_FAILURES = 3

# Настройки для очистки кеша
CACHE_CLEANUP_INTERVAL = 3600  # 1 час
CACHE_MAX_ENTRIES = 10000
CACHE_CLEANUP_RATIO = 0.8  # удалять 80% устаревших записей


# Экспорт всех констант
__all__ = [
    # VK API лимиты
    "VK_API_MAX_REQUESTS_PER_SECOND",
    "VK_API_MAX_POSTS_PER_REQUEST",
    "VK_API_MAX_COMMENTS_PER_REQUEST",
    "VK_API_MAX_GROUPS_PER_REQUEST",
    "VK_API_MAX_USERS_PER_REQUEST",
    # Таймауты
    "VK_API_REQUEST_TIMEOUT",
    "VK_API_CONNECTION_TIMEOUT",
    # Rate limiting
    "RATE_LIMIT_WINDOW_SECONDS",
    "RATE_LIMIT_MAX_REQUESTS",
    # Коды ошибок VK API
    "VK_ERROR_ACCESS_DENIED",
    "VK_ERROR_INVALID_REQUEST",
    "VK_ERROR_TOO_MANY_REQUESTS",
    "VK_ERROR_AUTH_FAILED",
    "VK_ERROR_PERMISSION_DENIED",
    "VK_ERROR_GROUP_ACCESS_DENIED",
    "VK_ERROR_POST_NOT_FOUND",
    "VK_ERROR_USER_NOT_FOUND",
    # Типы объектов VK
    "VK_OBJECT_TYPE_POST",
    "VK_OBJECT_TYPE_COMMENT",
    "VK_OBJECT_TYPE_GROUP",
    "VK_OBJECT_TYPE_USER",
    "VK_OBJECT_TYPE_WALL",
    # Сортировка комментариев
    "VK_SORT_ASC",
    "VK_SORT_DESC",
    # Типы поиска групп
    "VK_GROUP_TYPE_GROUP",
    "VK_GROUP_TYPE_PAGE",
    "VK_GROUP_TYPE_EVENT",
    # Статусы групп
    "VK_GROUP_STATUS_OPEN",
    "VK_GROUP_STATUS_CLOSED",
    "VK_GROUP_STATUS_PRIVATE",
    # Методы VK API
    "VK_METHOD_WALL_GET",
    "VK_METHOD_WALL_GET_COMMENTS",
    "VK_METHOD_GROUPS_GET_BY_ID",
    "VK_METHOD_GROUPS_SEARCH",
    "VK_METHOD_USERS_GET",
    "VK_METHOD_GROUPS_GET_MEMBERS",
    # Параметры полей для запросов
    "VK_FIELDS_GROUP",
    "VK_FIELDS_USER",
    # Ключи кеша
    "CACHE_KEY_GROUP_POSTS",
    "CACHE_KEY_POST_COMMENTS",
    "CACHE_KEY_GROUP_INFO",
    "CACHE_KEY_USER_INFO",
    "CACHE_KEY_GROUP_SEARCH",
    # TTL кеша
    "CACHE_GROUP_POSTS_TTL",
    "CACHE_POST_COMMENTS_TTL",
    "CACHE_GROUP_INFO_TTL",
    "CACHE_USER_INFO_TTL",
    "CACHE_SEARCH_TTL",
    # Сообщения об ошибках
    "ERROR_VK_API_REQUEST_FAILED",
    "ERROR_VK_API_RATE_LIMIT",
    "ERROR_VK_API_AUTH",
    "ERROR_VK_API_INVALID_TOKEN",
    "ERROR_VK_API_ACCESS_DENIED",
    "ERROR_VK_API_INVALID_PARAMS",
    "ERROR_VK_API_TIMEOUT",
    "ERROR_VK_API_NETWORK",
    # Сообщения об успехе
    "SUCCESS_VK_API_CONNECTED",
    "SUCCESS_VK_API_TOKEN_VALID",
    "SUCCESS_VK_API_REQUEST_COMPLETED",
    # Регулярные выражения
    "REGEX_VK_GROUP_ID",
    "REGEX_VK_USER_ID",
    "REGEX_VK_POST_ID",
    # Логирование
    "LOG_VK_API_REQUEST",
    "LOG_VK_API_RESPONSE",
    "LOG_VK_API_ERROR",
    "LOG_VK_API_RATE_LIMIT",
    # Метрики
    "METRIC_VK_API_REQUESTS",
    "METRIC_VK_API_ERRORS",
    "METRIC_VK_API_RATE_LIMITS",
    "METRIC_VK_API_RESPONSE_TIME",
    "METRIC_VK_API_REQUESTS_PER_SECOND",
    # Настройки повторов
    "RETRY_MAX_ATTEMPTS",
    "RETRY_BACKOFF_FACTOR",
    "RETRY_MAX_DELAY",
    # Настройки подключения
    "HTTP_MAX_CONNECTIONS",
    "HTTP_MAX_KEEPALIVE",
    "HTTP_TIMEOUT",
    # Настройки прокси
    "PROXY_ENABLED",
    "PROXY_LIST",
    "PROXY_ROTATION_ENABLED",
    # Настройки для тестирования
    "TEST_MODE_ENABLED",
    "TEST_MOCK_RESPONSES",
    # Настройки версий API
    "VK_API_VERSION",
    "VK_API_BASE_URL",
    # Настройки пользовательских агентов
    "USER_AGENTS",
    # Настройки для обработки больших объемов данных
    "BATCH_SIZE_GROUP_POSTS",
    "BATCH_SIZE_GROUP_COMMENTS",
    "BATCH_SIZE_USER_INFO",
    # Настройки для обработки ошибок
    "ERROR_RETRY_DELAY",
    "ERROR_RETRY_MAX_DELAY",
    "ERROR_RETRY_BACKOFF",
    # Настройки для мониторинга
    "HEALTH_CHECK_INTERVAL",
    "HEALTH_CHECK_TIMEOUT",
    "HEALTH_CHECK_MAX_FAILURES",
    # Настройки для очистки кеша
    "CACHE_CLEANUP_INTERVAL",
    "CACHE_MAX_ENTRIES",
    "CACHE_CLEANUP_RATIO",
]
