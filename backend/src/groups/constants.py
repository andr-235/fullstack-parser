"""
Константы модуля Groups

Содержит все константы используемые в модуле групп
"""

# Статусы групп
GROUP_STATUS_ACTIVE = "active"
GROUP_STATUS_INACTIVE = "inactive"
GROUP_STATUS_MONITORING = "monitoring"
GROUP_STATUS_ERROR = "error"

# Действия массовых операций
BULK_ACTION_ACTIVATE = "activate"
BULK_ACTION_DEACTIVATE = "deactivate"
BULK_ACTION_ENABLE_MONITORING = "enable_monitoring"
BULK_ACTION_DISABLE_MONITORING = "disable_monitoring"

# Допустимые действия
ALLOWED_BULK_ACTIONS = [
    BULK_ACTION_ACTIVATE,
    BULK_ACTION_DEACTIVATE,
    BULK_ACTION_ENABLE_MONITORING,
    BULK_ACTION_DISABLE_MONITORING,
]

# Поля для сортировки
SORT_FIELD_NAME = "name"
SORT_FIELD_CREATED = "created_at"
SORT_FIELD_MEMBERS = "members_count"
SORT_FIELD_ACTIVITY = "last_parsed_at"

ALLOWED_SORT_FIELDS = [
    SORT_FIELD_NAME,
    SORT_FIELD_CREATED,
    SORT_FIELD_MEMBERS,
    SORT_FIELD_ACTIVITY,
]

# Направления сортировки
SORT_ORDER_ASC = "asc"
SORT_ORDER_DESC = "desc"

ALLOWED_SORT_ORDERS = [SORT_ORDER_ASC, SORT_ORDER_DESC]

# Типы фильтров
FILTER_TYPE_ACTIVE = "active"
FILTER_TYPE_SEARCH = "search"
FILTER_TYPE_MEMBERS_RANGE = "members_range"
FILTER_TYPE_ACTIVITY = "activity"

# Сообщения об ошибках
ERROR_GROUP_NOT_FOUND = "Группа не найдена"
ERROR_INVALID_GROUP_ID = "Неверный ID группы"
ERROR_INVALID_VK_ID = "Неверный VK ID группы"
ERROR_INVALID_SCREEN_NAME = "Неверный screen_name группы"
ERROR_GROUP_ALREADY_EXISTS = "Группа уже существует"
ERROR_GROUP_NAME_TOO_LONG = "Название группы слишком длинное"
ERROR_SCREEN_NAME_TOO_LONG = "Screen name слишком длинный"
ERROR_DESCRIPTION_TOO_LONG = "Описание группы слишком длинное"
ERROR_BULK_ACTION_FAILED = "Массовое действие не выполнено"
ERROR_INVALID_MAX_POSTS = "Неверное значение max_posts_to_check"

# Сообщения об успехе
SUCCESS_GROUP_CREATED = "Группа успешно создана"
SUCCESS_GROUP_UPDATED = "Группа успешно обновлена"
SUCCESS_GROUP_DELETED = "Группа успешно удалена"
SUCCESS_GROUP_ACTIVATED = "Группа успешно активирована"
SUCCESS_GROUP_DEACTIVATED = "Группа успешно деактивирована"
SUCCESS_BULK_OPERATION = "Массовое действие выполнено успешно"

# Названия полей для API
API_FIELD_ID = "id"
API_FIELD_VK_ID = "vk_id"
API_FIELD_SCREEN_NAME = "screen_name"
API_FIELD_NAME = "name"
API_FIELD_DESCRIPTION = "description"
API_FIELD_IS_ACTIVE = "is_active"
API_FIELD_MAX_POSTS_TO_CHECK = "max_posts_to_check"
API_FIELD_MEMBERS_COUNT = "members_count"
API_FIELD_PHOTO_URL = "photo_url"
API_FIELD_IS_CLOSED = "is_closed"
API_FIELD_TOTAL_POSTS_PARSED = "total_posts_parsed"
API_FIELD_TOTAL_COMMENTS_FOUND = "total_comments_found"
API_FIELD_LAST_PARSED_AT = "last_parsed_at"
API_FIELD_CREATED_AT = "created_at"
API_FIELD_UPDATED_AT = "updated_at"

# Обязательные поля для создания группы
REQUIRED_CREATE_FIELDS = [
    API_FIELD_VK_ID,
    API_FIELD_SCREEN_NAME,
    API_FIELD_NAME,
]

# Допустимые поля для обновления
ALLOWED_UPDATE_FIELDS = [
    API_FIELD_NAME,
    API_FIELD_SCREEN_NAME,
    API_FIELD_DESCRIPTION,
    API_FIELD_IS_ACTIVE,
    API_FIELD_MAX_POSTS_TO_CHECK,
    API_FIELD_MEMBERS_COUNT,
    API_FIELD_PHOTO_URL,
    API_FIELD_IS_CLOSED,
]

# Максимальные значения
MAX_GROUP_NAME_LENGTH = 255
MAX_SCREEN_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 1000
MAX_VK_ID_VALUE = 999999999  # Максимальный ID в VK
MIN_VK_ID_VALUE = 1
MAX_BULK_OPERATION_SIZE = 500
MAX_MEMBERS_COUNT = 100000000  # 100 миллионов

# Настройки кеширования
CACHE_KEY_GROUP = "group:{id}"
CACHE_KEY_GROUP_VK = "group:vk:{vk_id}"
CACHE_KEY_GROUP_SCREEN = "group:screen:{screen_name}"
CACHE_KEY_GROUPS_LIST = "groups:list:{page}:{size}:{filters}"
CACHE_KEY_GROUPS_SEARCH = "groups:search:{query}:{page}:{size}"
CACHE_KEY_GROUP_STATS = "group:stats:{id}"
CACHE_KEY_GROUPS_STATS = "groups:stats:overview"

# Таймауты
DATABASE_TIMEOUT = 30
SEARCH_TIMEOUT = 30
VK_API_TIMEOUT = 30
CACHE_TIMEOUT = 300

# Настройки VK API
VK_API_BASE_URL = "https://api.vk.com/method"
VK_API_VERSION = "5.199"
VK_GROUP_INFO_FIELDS = "members_count,description,photo_200,is_closed"

# Настройки мониторинга
DEFAULT_MONITORING_INTERVAL_MINUTES = 60
MIN_MONITORING_INTERVAL_MINUTES = 15
MAX_MONITORING_INTERVAL_MINUTES = 1440  # 24 часа
DEFAULT_MAX_POSTS_TO_CHECK = 100
MIN_MAX_POSTS_TO_CHECK = 10
MAX_MAX_POSTS_TO_CHECK = 1000


# Экспорт всех констант
__all__ = [
    # Статусы
    "GROUP_STATUS_ACTIVE",
    "GROUP_STATUS_INACTIVE",
    "GROUP_STATUS_MONITORING",
    "GROUP_STATUS_ERROR",
    # Действия
    "BULK_ACTION_ACTIVATE",
    "BULK_ACTION_DEACTIVATE",
    "BULK_ACTION_ENABLE_MONITORING",
    "BULK_ACTION_DISABLE_MONITORING",
    "ALLOWED_BULK_ACTIONS",
    # Сортировка
    "SORT_FIELD_NAME",
    "SORT_FIELD_CREATED",
    "SORT_FIELD_MEMBERS",
    "SORT_FIELD_ACTIVITY",
    "ALLOWED_SORT_FIELDS",
    "SORT_ORDER_ASC",
    "SORT_ORDER_DESC",
    "ALLOWED_SORT_ORDERS",
    # Фильтры
    "FILTER_TYPE_ACTIVE",
    "FILTER_TYPE_SEARCH",
    "FILTER_TYPE_MEMBERS_RANGE",
    "FILTER_TYPE_ACTIVITY",
    # Сообщения об ошибках
    "ERROR_GROUP_NOT_FOUND",
    "ERROR_INVALID_GROUP_ID",
    "ERROR_INVALID_VK_ID",
    "ERROR_INVALID_SCREEN_NAME",
    "ERROR_GROUP_ALREADY_EXISTS",
    "ERROR_GROUP_NAME_TOO_LONG",
    "ERROR_SCREEN_NAME_TOO_LONG",
    "ERROR_DESCRIPTION_TOO_LONG",
    "ERROR_BULK_ACTION_FAILED",
    "ERROR_INVALID_MAX_POSTS",
    # Сообщения об успехе
    "SUCCESS_GROUP_CREATED",
    "SUCCESS_GROUP_UPDATED",
    "SUCCESS_GROUP_DELETED",
    "SUCCESS_GROUP_ACTIVATED",
    "SUCCESS_GROUP_DEACTIVATED",
    "SUCCESS_BULK_OPERATION",
    # API поля
    "API_FIELD_ID",
    "API_FIELD_VK_ID",
    "API_FIELD_SCREEN_NAME",
    "API_FIELD_NAME",
    "API_FIELD_DESCRIPTION",
    "API_FIELD_IS_ACTIVE",
    "API_FIELD_MAX_POSTS_TO_CHECK",
    "API_FIELD_MEMBERS_COUNT",
    "API_FIELD_PHOTO_URL",
    "API_FIELD_IS_CLOSED",
    "API_FIELD_TOTAL_POSTS_PARSED",
    "API_FIELD_TOTAL_COMMENTS_FOUND",
    "API_FIELD_LAST_PARSED_AT",
    "API_FIELD_CREATED_AT",
    "API_FIELD_UPDATED_AT",
    "REQUIRED_CREATE_FIELDS",
    "ALLOWED_UPDATE_FIELDS",
    # Максимальные значения
    "MAX_GROUP_NAME_LENGTH",
    "MAX_SCREEN_NAME_LENGTH",
    "MAX_DESCRIPTION_LENGTH",
    "MAX_VK_ID_VALUE",
    "MIN_VK_ID_VALUE",
    "MAX_BULK_OPERATION_SIZE",
    "MAX_MEMBERS_COUNT",
    # Кеширование
    "CACHE_KEY_GROUP",
    "CACHE_KEY_GROUP_VK",
    "CACHE_KEY_GROUP_SCREEN",
    "CACHE_KEY_GROUPS_LIST",
    "CACHE_KEY_GROUPS_SEARCH",
    "CACHE_KEY_GROUP_STATS",
    "CACHE_KEY_GROUPS_STATS",
    # Таймауты
    "DATABASE_TIMEOUT",
    "SEARCH_TIMEOUT",
    "VK_API_TIMEOUT",
    "CACHE_TIMEOUT",
    # VK API
    "VK_API_BASE_URL",
    "VK_API_VERSION",
    "VK_GROUP_INFO_FIELDS",
    # Мониторинг
    "DEFAULT_MONITORING_INTERVAL_MINUTES",
    "MIN_MONITORING_INTERVAL_MINUTES",
    "MAX_MONITORING_INTERVAL_MINUTES",
    "DEFAULT_MAX_POSTS_TO_CHECK",
    "MIN_MAX_POSTS_TO_CHECK",
    "MAX_MAX_POSTS_TO_CHECK",
]
