"""
Конфигурация модуля Groups

Содержит настройки специфичные для модуля групп VK
"""

from typing import Optional

from ..config import settings


class GroupsConfig:
    """Конфигурация для модуля групп"""

    # Настройки пагинации
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    MIN_SEARCH_LENGTH = 2

    # Настройки поиска
    SEARCH_TIMEOUT = 30  # секунды

    # Настройки кеширования
    CACHE_GROUP_TTL = 300  # 5 минут
    CACHE_STATS_TTL = 60  # 1 минута
    CACHE_LIST_TTL = 180  # 3 минуты

    # Настройки массовых операций
    MAX_BULK_SIZE = 500

    # Настройки валидации
    MAX_GROUP_NAME_LENGTH = 255
    MAX_SCREEN_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 1000

    # Настройки мониторинга
    DEFAULT_MAX_POSTS_TO_CHECK = 100
    MIN_MAX_POSTS_TO_CHECK = 10
    MAX_MAX_POSTS_TO_CHECK = 1000

    # Настройки VK API
    VK_GROUP_INFO_CACHE_TTL = 3600  # 1 час

    @classmethod
    def get_page_size(cls, requested_size: Optional[int] = None) -> int:
        """Получить размер страницы с валидацией"""
        if requested_size is None:
            return cls.DEFAULT_PAGE_SIZE

        return max(cls.DEFAULT_PAGE_SIZE, min(requested_size, cls.MAX_PAGE_SIZE))

    @classmethod
    def validate_search_query(cls, query: str) -> bool:
        """Валидировать поисковый запрос"""
        return len(query.strip()) >= cls.MIN_SEARCH_LENGTH

    @classmethod
    def validate_group_name(cls, name: str) -> bool:
        """Валидировать название группы"""
        return 1 <= len(name.strip()) <= cls.MAX_GROUP_NAME_LENGTH

    @classmethod
    def validate_screen_name(cls, screen_name: str) -> bool:
        """Валидировать screen_name группы"""
        return 1 <= len(screen_name.strip()) <= cls.MAX_SCREEN_NAME_LENGTH

    @classmethod
    def validate_description(cls, description: Optional[str]) -> bool:
        """Валидировать описание группы"""
        if description is None:
            return True
        return len(description.strip()) <= cls.MAX_DESCRIPTION_LENGTH

    @classmethod
    def validate_max_posts_to_check(cls, max_posts: int) -> bool:
        """Валидировать максимальное количество постов для проверки"""
        return cls.MIN_MAX_POSTS_TO_CHECK <= max_posts <= cls.MAX_MAX_POSTS_TO_CHECK

    @classmethod
    def get_cache_settings(cls) -> dict:
        """Получить настройки кеширования"""
        return {
            "enabled": settings.cache_enabled,
            "group_ttl": cls.CACHE_GROUP_TTL,
            "stats_ttl": cls.CACHE_STATS_TTL,
            "list_ttl": cls.CACHE_LIST_TTL,
        }

    @classmethod
    def get_monitoring_settings(cls) -> dict:
        """Получить настройки мониторинга"""
        return {
            "default_max_posts": cls.DEFAULT_MAX_POSTS_TO_CHECK,
            "min_max_posts": cls.MIN_MAX_POSTS_TO_CHECK,
            "max_max_posts": cls.MAX_MAX_POSTS_TO_CHECK,
        }


# Экземпляр конфигурации
groups_config = GroupsConfig()


# Экспорт
__all__ = [
    "GroupsConfig",
    "groups_config",
]
