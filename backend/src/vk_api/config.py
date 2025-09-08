"""
Конфигурация и константы модуля VK API

Объединенный файл конфигурации по паттернам FastAPI лучших практик
"""

from typing import Optional, List
from pydantic import BaseModel, Field

from ..config import settings


class VKAPIConnectionConfig(BaseModel):
    """Конфигурация подключения к VK API"""

    timeout: float = Field(default=30.0, gt=0, description="Таймаут запросов")
    connection_timeout: float = Field(
        default=10.0, gt=0, description="Таймаут подключения"
    )
    max_connections: int = Field(
        default=100, gt=0, description="Максимум соединений"
    )
    max_keepalive: int = Field(
        default=10, gt=0, description="Максимум keep-alive соединений"
    )


class VKAPIRateLimitConfig(BaseModel):
    """Конфигурация rate limiting"""

    max_requests_per_second: int = Field(
        default=3, gt=0, description="Максимум запросов в секунду"
    )
    window_seconds: float = Field(
        default=1.0, gt=0, description="Окно времени в секундах"
    )


class VKAPIRequestLimits(BaseModel):
    """Лимиты запросов VK API"""

    max_posts_per_request: int = Field(
        default=100, gt=0, description="Максимум постов за запрос"
    )
    max_comments_per_request: int = Field(
        default=100, gt=0, description="Максимум комментариев за запрос"
    )
    max_groups_per_request: int = Field(
        default=10000, gt=0, description="Максимум групп за запрос"
    )
    max_users_per_request: int = Field(
        default=1000, gt=0, description="Максимум пользователей за запрос"
    )
    max_group_members_per_request: int = Field(
        default=1000, gt=0, description="Максимум участников группы за запрос"
    )


class VKAPICacheConfig(BaseModel):
    """Конфигурация кеширования"""

    enabled: bool = Field(default=True, description="Включено ли кеширование")
    group_posts_ttl: int = Field(
        default=300, gt=0, description="TTL кеша постов группы (сек)"
    )
    post_comments_ttl: int = Field(
        default=600, gt=0, description="TTL кеша комментариев (сек)"
    )
    group_info_ttl: int = Field(
        default=3600, gt=0, description="TTL кеша информации о группе (сек)"
    )
    user_info_ttl: int = Field(
        default=1800,
        gt=0,
        description="TTL кеша информации о пользователе (сек)",
    )
    search_ttl: int = Field(
        default=1800, gt=0, description="TTL кеша поиска (сек)"
    )
    group_members_ttl: int = Field(
        default=1800, gt=0, description="TTL кеша участников группы (сек)"
    )


class VKAPIRetryConfig(BaseModel):
    """Конфигурация повторов"""

    enabled: bool = Field(default=True, description="Включены ли повторы")
    max_attempts: int = Field(default=3, gt=0, description="Максимум попыток")
    backoff_factor: float = Field(
        default=2.0, gt=0, description="Коэффициент отката"
    )
    max_delay: float = Field(
        default=60.0, gt=0, description="Максимальная задержка"
    )


class VKAPIProxyConfig(BaseModel):
    """Конфигурация прокси"""

    enabled: bool = Field(default=False, description="Включены ли прокси")
    proxy_list: List[str] = Field(
        default_factory=list, description="Список прокси"
    )
    rotation_enabled: bool = Field(
        default=False, description="Включена ли ротация прокси"
    )


class VKAPILoggingConfig(BaseModel):
    """Конфигурация логирования"""

    log_requests: bool = Field(default=True, description="Логировать запросы")
    log_errors: bool = Field(default=True, description="Логировать ошибки")
    log_rate_limits: bool = Field(
        default=True, description="Логировать rate limits"
    )


class VKAPIMonitoringConfig(BaseModel):
    """Конфигурация мониторинга"""

    metrics_enabled: bool = Field(
        default=True, description="Включены ли метрики"
    )
    health_checks_enabled: bool = Field(
        default=True, description="Включены ли проверки здоровья"
    )
    health_check_interval: int = Field(
        default=60, description="Интервал проверок здоровья"
    )


class VKAPICleanupConfig(BaseModel):
    """Конфигурация очистки кеша"""

    enabled: bool = Field(default=True, description="Включена ли очистка")
    interval: int = Field(default=3600, description="Интервал очистки (сек)")
    max_entries: int = Field(default=10000, description="Максимум записей")
    cleanup_ratio: float = Field(
        default=0.8, description="Коэффициент очистки"
    )


class VKAPIConfig(BaseModel):
    """Основная конфигурация VK API"""

    # Основные настройки
    api_version: str = Field(default="5.199", description="Версия VK API")
    base_url: str = Field(
        default="https://api.vk.com/method/", description="Базовый URL API"
    )
    access_token: Optional[str] = Field(
        default_factory=lambda: getattr(settings, "vk_access_token", None),
        description="Токен доступа",
        repr=False,  # Don't include token in string representation
    )

    # Поля запросов
    group_fields: str = Field(
        default="id,name,screen_name,description,members_count,photo_200,is_closed,type",
        description="Поля для запросов групп",
    )
    user_fields: str = Field(
        default="id,first_name,last_name,photo_100,sex,city,country",
        description="Поля для запросов пользователей",
    )
    group_members_fields: str = Field(
        default="id,first_name,last_name,photo_100,sex,city,country,deactivated",
        description="Поля для запросов участников группы",
    )

    # Настройки для тестирования
    test_mode_enabled: bool = Field(
        default=False, description="Тестовый режим"
    )
    mock_responses_enabled: bool = Field(
        default=False, description="Мок-ответы"
    )

    # Настройки для обработки больших объемов данных
    batch_size_group_posts: int = Field(
        default=50, description="Размер батча постов групп"
    )
    batch_size_group_comments: int = Field(
        default=25, description="Размер батча комментариев"
    )
    batch_size_user_info: int = Field(
        default=100, description="Размер батча информации о пользователях"
    )

    # Вложенные конфигурации
    connection: VKAPIConnectionConfig = Field(
        default_factory=VKAPIConnectionConfig
    )
    rate_limit: VKAPIRateLimitConfig = Field(
        default_factory=VKAPIRateLimitConfig
    )
    limits: VKAPIRequestLimits = Field(default_factory=VKAPIRequestLimits)
    cache: VKAPICacheConfig = Field(default_factory=VKAPICacheConfig)
    retry: VKAPIRetryConfig = Field(default_factory=VKAPIRetryConfig)
    proxy: VKAPIProxyConfig = Field(default_factory=VKAPIProxyConfig)
    logging: VKAPILoggingConfig = Field(default_factory=VKAPILoggingConfig)
    monitoring: VKAPIMonitoringConfig = Field(
        default_factory=VKAPIMonitoringConfig
    )
    cleanup: VKAPICleanupConfig = Field(default_factory=VKAPICleanupConfig)

    @property
    def is_token_configured(self) -> bool:
        """Проверить, настроен ли токен доступа"""
        return (
            self.access_token is not None and self.access_token.strip() != ""
        )

    def validate_token(self, token: str) -> bool:
        """Проверить валидность токена"""
        if not token or not isinstance(token, str):
            return False
        return len(token.strip()) > 10  # Минимальная длина токена

    def get_request_fields(self, object_type: str) -> str:
        """Получить поля для запроса в зависимости от типа объекта"""
        if object_type == "group":
            return self.group_fields
        elif object_type == "user":
            return self.user_fields
        return ""

    def should_log_request(self, method: str) -> bool:
        """Определить, нужно ли логировать запрос"""
        if not self.logging.log_requests:
            return False
        return True

    def should_log_error(self, error_code: int) -> bool:
        """Определить, нужно ли логировать ошибку"""
        if not self.logging.log_errors:
            return False

        # Важные ошибки всегда логируем
        critical_errors = [
            5,
            6,
            7,
            203,
        ]  # access denied, invalid request, etc.
        return error_code in critical_errors


# Дополнительные константы (временно, пока не перенесены в конфигурацию)
VK_OBJECT_TYPE_POST = "post"
VK_OBJECT_TYPE_COMMENT = "comment"
VK_OBJECT_TYPE_GROUP = "group"
VK_OBJECT_TYPE_USER = "user"
VK_OBJECT_TYPE_WALL = "wall"
VK_SORT_ASC = "asc"
VK_SORT_DESC = "desc"
VK_GROUP_TYPE_GROUP = "group"
VK_GROUP_TYPE_PAGE = "page"
VK_GROUP_TYPE_EVENT = "event"
VK_GROUP_STATUS_OPEN = "open"
VK_GROUP_STATUS_CLOSED = "closed"
VK_GROUP_STATUS_PRIVATE = "private"
VK_METHOD_WALL_GET = "wall.get"
VK_METHOD_WALL_GET_COMMENTS = "wall.getComments"
VK_METHOD_GROUPS_GET_BY_ID = "groups.getById"
VK_METHOD_GROUPS_SEARCH = "groups.search"
VK_METHOD_USERS_GET = "users.get"
VK_METHOD_GROUPS_GET_MEMBERS = "groups.getMembers"
VK_ERROR_ACCESS_DENIED = 15
VK_ERROR_INVALID_REQUEST = 100
VK_ERROR_TOO_MANY_REQUESTS = 6
VK_ERROR_AUTH_FAILED = 5
VK_ERROR_PERMISSION_DENIED = 7
VK_ERROR_GROUP_ACCESS_DENIED = 203
VK_ERROR_POST_NOT_FOUND = 100
VK_ERROR_USER_NOT_FOUND = 113
REGEX_VK_GROUP_ID = r"^(-?\d+)$"
REGEX_VK_USER_ID = r"^(\d+)$"
REGEX_VK_POST_ID = r"^(\d+)$"
USER_AGENTS = [
    "VK Comments Parser/1.0",
    "VK Data Collector/1.0",
    "VK API Client/1.0",
]

# Экземпляр конфигурации
vk_api_config = VKAPIConfig()


# Экспорт
__all__ = [
    "VKAPIConfig",
    "VKAPIConnectionConfig",
    "VKAPIRateLimitConfig",
    "VKAPIRequestLimits",
    "VKAPICacheConfig",
    "VKAPIRetryConfig",
    "VKAPIProxyConfig",
    "VKAPILoggingConfig",
    "VKAPIMonitoringConfig",
    "VKAPICleanupConfig",
    "vk_api_config",
]
