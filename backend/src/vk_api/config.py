"""
Конфигурация модуля VK API

Содержит настройки специфичные для модуля работы с VK API
"""

from typing import Optional, List

from ..config import settings


class VKAPIConfig:
    """Конфигурация для модуля VK API"""

    # Основные настройки VK API
    API_VERSION = "5.199"
    BASE_URL = "https://api.vk.com/method/"
    ACCESS_TOKEN = (
        settings.vk_access_token
        if hasattr(settings, "vk_access_token")
        else None
    )

    # Настройки подключения
    REQUEST_TIMEOUT = 30.0
    CONNECTION_TIMEOUT = 10.0
    MAX_CONNECTIONS = 100
    MAX_KEEPALIVE = 10

    # Rate limiting
    MAX_REQUESTS_PER_SECOND = 3
    RATE_LIMIT_WINDOW = 1.0

    # Лимиты запросов
    MAX_POSTS_PER_REQUEST = 100
    MAX_COMMENTS_PER_REQUEST = 100
    MAX_GROUPS_PER_REQUEST = 1000
    MAX_USERS_PER_REQUEST = 1000

    # Настройки кеширования
    CACHE_ENABLED = True
    CACHE_TTL_GROUP_POSTS = 300  # 5 минут
    CACHE_TTL_POST_COMMENTS = 600  # 10 минут
    CACHE_TTL_GROUP_INFO = 3600  # 1 час
    CACHE_TTL_USER_INFO = 1800  # 30 минут
    CACHE_TTL_SEARCH = 1800  # 30 минут

    # Настройки повторов
    RETRY_ENABLED = True
    RETRY_MAX_ATTEMPTS = 3
    RETRY_BACKOFF_FACTOR = 2.0
    RETRY_MAX_DELAY = 60.0

    # Настройки прокси
    PROXY_ENABLED = False
    PROXY_LIST: List[str] = []
    PROXY_ROTATION_ENABLED = False

    # Настройки логирования
    LOG_REQUESTS = True
    LOG_ERRORS = True
    LOG_RATE_LIMITS = True

    # Настройки мониторинга
    METRICS_ENABLED = True
    HEALTH_CHECKS_ENABLED = True
    HEALTH_CHECK_INTERVAL = 60

    # Настройки для тестирования
    TEST_MODE_ENABLED = False
    MOCK_RESPONSES_ENABLED = False

    # Поля для запросов
    GROUP_FIELDS = "id,name,screen_name,description,members_count,photo_200,is_closed,type"
    USER_FIELDS = "id,first_name,last_name,photo_100,sex,city,country"

    # Настройки для обработки больших объемов данных
    BATCH_SIZE_GROUP_POSTS = 50
    BATCH_SIZE_GROUP_COMMENTS = 25
    BATCH_SIZE_USER_INFO = 100

    # Настройки очистки кеша
    CACHE_CLEANUP_ENABLED = True
    CACHE_CLEANUP_INTERVAL = 3600  # 1 час
    CACHE_MAX_ENTRIES = 10000
    CACHE_CLEANUP_RATIO = 0.8

    @classmethod
    def get_api_config(cls) -> dict:
        """Получить конфигурацию API"""
        return {
            "version": cls.API_VERSION,
            "base_url": cls.BASE_URL,
            "access_token": cls.ACCESS_TOKEN,
            "timeout": cls.REQUEST_TIMEOUT,
        }

    @classmethod
    def get_connection_config(cls) -> dict:
        """Получить конфигурацию подключения"""
        return {
            "max_connections": cls.MAX_CONNECTIONS,
            "max_keepalive": cls.MAX_KEEPALIVE,
            "connection_timeout": cls.CONNECTION_TIMEOUT,
        }

    @classmethod
    def get_rate_limit_config(cls) -> dict:
        """Получить конфигурацию rate limiting"""
        return {
            "max_requests_per_second": cls.MAX_REQUESTS_PER_SECOND,
            "window_seconds": cls.RATE_LIMIT_WINDOW,
        }

    @classmethod
    def get_limits_config(cls) -> dict:
        """Получить конфигурацию лимитов"""
        return {
            "max_posts_per_request": cls.MAX_POSTS_PER_REQUEST,
            "max_comments_per_request": cls.MAX_COMMENTS_PER_REQUEST,
            "max_groups_per_request": cls.MAX_GROUPS_PER_REQUEST,
            "max_users_per_request": cls.MAX_USERS_PER_REQUEST,
        }

    @classmethod
    def get_cache_config(cls) -> dict:
        """Получить конфигурацию кеширования"""
        return {
            "enabled": cls.CACHE_ENABLED,
            "group_posts_ttl": cls.CACHE_TTL_GROUP_POSTS,
            "post_comments_ttl": cls.CACHE_TTL_POST_COMMENTS,
            "group_info_ttl": cls.CACHE_TTL_GROUP_INFO,
            "user_info_ttl": cls.CACHE_TTL_USER_INFO,
            "search_ttl": cls.CACHE_TTL_SEARCH,
        }

    @classmethod
    def get_retry_config(cls) -> dict:
        """Получить конфигурацию повторов"""
        return {
            "enabled": cls.RETRY_ENABLED,
            "max_attempts": cls.RETRY_MAX_ATTEMPTS,
            "backoff_factor": cls.RETRY_BACKOFF_FACTOR,
            "max_delay": cls.RETRY_MAX_DELAY,
        }

    @classmethod
    def get_proxy_config(cls) -> dict:
        """Получить конфигурацию прокси"""
        return {
            "enabled": cls.PROXY_ENABLED,
            "proxy_list": cls.PROXY_LIST,
            "rotation_enabled": cls.PROXY_ROTATION_ENABLED,
        }

    @classmethod
    def get_logging_config(cls) -> dict:
        """Получить конфигурацию логирования"""
        return {
            "log_requests": cls.LOG_REQUESTS,
            "log_errors": cls.LOG_ERRORS,
            "log_rate_limits": cls.LOG_RATE_LIMITS,
        }

    @classmethod
    def get_monitoring_config(cls) -> dict:
        """Получить конфигурацию мониторинга"""
        return {
            "metrics_enabled": cls.METRICS_ENABLED,
            "health_checks_enabled": cls.HEALTH_CHECKS_ENABLED,
            "health_check_interval": cls.HEALTH_CHECK_INTERVAL,
        }

    @classmethod
    def get_batch_config(cls) -> dict:
        """Получить конфигурацию пакетной обработки"""
        return {
            "group_posts_batch_size": cls.BATCH_SIZE_GROUP_POSTS,
            "group_comments_batch_size": cls.BATCH_SIZE_GROUP_COMMENTS,
            "user_info_batch_size": cls.BATCH_SIZE_USER_INFO,
        }

    @classmethod
    def get_cleanup_config(cls) -> dict:
        """Получить конфигурацию очистки"""
        return {
            "enabled": cls.CACHE_CLEANUP_ENABLED,
            "interval": cls.CACHE_CLEANUP_INTERVAL,
            "max_entries": cls.CACHE_MAX_ENTRIES,
            "cleanup_ratio": cls.CACHE_CLEANUP_RATIO,
        }

    @classmethod
    def is_token_configured(cls) -> bool:
        """Проверить, настроен ли токен доступа"""
        return cls.ACCESS_TOKEN is not None and cls.ACCESS_TOKEN.strip() != ""

    @classmethod
    def validate_token(cls, token: str) -> bool:
        """Проверить валидность токена"""
        if not token or not isinstance(token, str):
            return False
        return len(token.strip()) > 10  # Минимальная длина токена

    @classmethod
    def get_request_fields(cls, object_type: str) -> str:
        """Получить поля для запроса в зависимости от типа объекта"""
        if object_type == "group":
            return cls.GROUP_FIELDS
        elif object_type == "user":
            return cls.USER_FIELDS
        return ""

    @classmethod
    def should_log_request(cls, method: str) -> bool:
        """Определить, нужно ли логировать запрос"""
        if not cls.LOG_REQUESTS:
            return False

        # Можно добавить логику для определенных методов
        return True

    @classmethod
    def should_log_error(cls, error_code: int) -> bool:
        """Определить, нужно ли логировать ошибку"""
        if not cls.LOG_ERRORS:
            return False

        # Важные ошибки всегда логируем
        critical_errors = [
            5,
            6,
            7,
            203,
        ]  # access denied, invalid request, etc.
        return error_code in critical_errors


# Экземпляр конфигурации
vk_api_config = VKAPIConfig()


# Экспорт
__all__ = [
    "VKAPIConfig",
    "vk_api_config",
]
