"""
Константы модуля Comments

Содержит все константы используемые в модуле комментариев
"""

# Статусы комментариев
COMMENT_STATUS_VIEWED = "viewed"
COMMENT_STATUS_PROCESSED = "processed"
COMMENT_STATUS_ARCHIVED = "archived"
COMMENT_STATUS_NEW = "new"

# Действия массовых операций
BULK_ACTION_VIEW = "view"
BULK_ACTION_PROCESS = "process"
BULK_ACTION_ARCHIVE = "archive"
BULK_ACTION_UNARCHIVE = "unarchive"

# Допустимые действия
ALLOWED_BULK_ACTIONS = [
    BULK_ACTION_VIEW,
    BULK_ACTION_PROCESS,
    BULK_ACTION_ARCHIVE,
    BULK_ACTION_UNARCHIVE,
]

# Поля для сортировки
SORT_FIELD_DATE = "date"
SORT_FIELD_LIKES = "likes_count"
SORT_FIELD_AUTHOR = "author_name"
SORT_FIELD_CREATED = "created_at"

ALLOWED_SORT_FIELDS = [
    SORT_FIELD_DATE,
    SORT_FIELD_LIKES,
    SORT_FIELD_AUTHOR,
    SORT_FIELD_CREATED,
]

# Направления сортировки
SORT_ORDER_ASC = "asc"
SORT_ORDER_DESC = "desc"

ALLOWED_SORT_ORDERS = [SORT_ORDER_ASC, SORT_ORDER_DESC]

# Типы фильтров
FILTER_TYPE_GROUP = "group"
FILTER_TYPE_POST = "post"
FILTER_TYPE_AUTHOR = "author"
FILTER_TYPE_DATE_RANGE = "date_range"
FILTER_TYPE_STATUS = "status"

# Сообщения об ошибках
ERROR_COMMENT_NOT_FOUND = "Комментарий не найден"
ERROR_INVALID_COMMENT_ID = "Неверный ID комментария"
ERROR_INVALID_GROUP_ID = "Неверный ID группы"
ERROR_INVALID_POST_ID = "Неверный ID поста"
ERROR_INVALID_SEARCH_QUERY = "Неверный поисковый запрос"
ERROR_BULK_ACTION_FAILED = "Массовое действие не выполнено"
ERROR_COMMENT_ALREADY_EXISTS = "Комментарий уже существует"

# Сообщения об успехе
SUCCESS_COMMENT_CREATED = "Комментарий успешно создан"
SUCCESS_COMMENT_UPDATED = "Комментарий успешно обновлен"
SUCCESS_COMMENT_DELETED = "Комментарий успешно удален"
SUCCESS_COMMENT_MARKED_VIEWED = "Комментарий отмечен как просмотренный"
SUCCESS_BULK_OPERATION = "Массовое действие выполнено успешно"

# Названия полей для API
API_FIELD_ID = "id"
API_FIELD_VK_COMMENT_ID = "vk_comment_id"
API_FIELD_VK_POST_ID = "vk_post_id"
API_FIELD_VK_GROUP_ID = "vk_group_id"
API_FIELD_AUTHOR_ID = "author_id"
API_FIELD_AUTHOR_NAME = "author_name"
API_FIELD_TEXT = "text"
API_FIELD_LIKES_COUNT = "likes_count"
API_FIELD_DATE = "date"
API_FIELD_PROCESSED_AT = "processed_at"
API_FIELD_CREATED_AT = "created_at"
API_FIELD_UPDATED_AT = "updated_at"

# Обязательные поля для создания комментария
REQUIRED_CREATE_FIELDS = [
    API_FIELD_VK_COMMENT_ID,
    API_FIELD_VK_POST_ID,
    API_FIELD_VK_GROUP_ID,
    API_FIELD_AUTHOR_ID,
    API_FIELD_AUTHOR_NAME,
    API_FIELD_TEXT,
    API_FIELD_DATE,
]

# Допустимые поля для обновления
ALLOWED_UPDATE_FIELDS = [
    API_FIELD_LIKES_COUNT,
    API_FIELD_PROCESSED_AT,
]

# Максимальные значения
MAX_COMMENT_TEXT_LENGTH = 10000
MAX_AUTHOR_NAME_LENGTH = 255
MAX_VK_ID_LENGTH = 50
MAX_BULK_OPERATION_SIZE = 1000

# Настройки кеширования
CACHE_KEY_COMMENT = "comment:{id}"
CACHE_KEY_COMMENTS_GROUP = "comments:group:{group_id}:{page}:{size}"
CACHE_KEY_COMMENTS_POST = "comments:post:{post_id}:{page}:{size}"
CACHE_KEY_COMMENTS_SEARCH = "comments:search:{query}:{page}:{size}"
CACHE_KEY_STATS_GROUP = "stats:group:{group_id}"

# Таймауты
DATABASE_TIMEOUT = 30
SEARCH_TIMEOUT = 30
CACHE_TIMEOUT = 300


# Экспорт всех констант
__all__ = [
    # Статусы
    "COMMENT_STATUS_VIEWED",
    "COMMENT_STATUS_PROCESSED",
    "COMMENT_STATUS_ARCHIVED",
    "COMMENT_STATUS_NEW",
    # Действия
    "BULK_ACTION_VIEW",
    "BULK_ACTION_PROCESS",
    "BULK_ACTION_ARCHIVE",
    "BULK_ACTION_UNARCHIVE",
    "ALLOWED_BULK_ACTIONS",
    # Сортировка
    "SORT_FIELD_DATE",
    "SORT_FIELD_LIKES",
    "SORT_FIELD_AUTHOR",
    "SORT_FIELD_CREATED",
    "ALLOWED_SORT_FIELDS",
    "SORT_ORDER_ASC",
    "SORT_ORDER_DESC",
    "ALLOWED_SORT_ORDERS",
    # Фильтры
    "FILTER_TYPE_GROUP",
    "FILTER_TYPE_POST",
    "FILTER_TYPE_AUTHOR",
    "FILTER_TYPE_DATE_RANGE",
    "FILTER_TYPE_STATUS",
    # Сообщения об ошибках
    "ERROR_COMMENT_NOT_FOUND",
    "ERROR_INVALID_COMMENT_ID",
    "ERROR_INVALID_GROUP_ID",
    "ERROR_INVALID_POST_ID",
    "ERROR_INVALID_SEARCH_QUERY",
    "ERROR_BULK_ACTION_FAILED",
    "ERROR_COMMENT_ALREADY_EXISTS",
    # Сообщения об успехе
    "SUCCESS_COMMENT_CREATED",
    "SUCCESS_COMMENT_UPDATED",
    "SUCCESS_COMMENT_DELETED",
    "SUCCESS_COMMENT_MARKED_VIEWED",
    "SUCCESS_BULK_OPERATION",
    # API поля
    "API_FIELD_ID",
    "API_FIELD_VK_COMMENT_ID",
    "API_FIELD_VK_POST_ID",
    "API_FIELD_VK_GROUP_ID",
    "API_FIELD_AUTHOR_ID",
    "API_FIELD_AUTHOR_NAME",
    "API_FIELD_TEXT",
    "API_FIELD_LIKES_COUNT",
    "API_FIELD_DATE",
    "API_FIELD_PROCESSED_AT",
    "API_FIELD_CREATED_AT",
    "API_FIELD_UPDATED_AT",
    "REQUIRED_CREATE_FIELDS",
    "ALLOWED_UPDATE_FIELDS",
    # Максимальные значения
    "MAX_COMMENT_TEXT_LENGTH",
    "MAX_AUTHOR_NAME_LENGTH",
    "MAX_VK_ID_LENGTH",
    "MAX_BULK_OPERATION_SIZE",
    # Кеширование
    "CACHE_KEY_COMMENT",
    "CACHE_KEY_COMMENTS_GROUP",
    "CACHE_KEY_COMMENTS_POST",
    "CACHE_KEY_COMMENTS_SEARCH",
    "CACHE_KEY_STATS_GROUP",
    # Таймауты
    "DATABASE_TIMEOUT",
    "SEARCH_TIMEOUT",
    "CACHE_TIMEOUT",
]
