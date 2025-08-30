"""
Конфигурация модуля Comments

Содержит настройки специфичные для модуля комментариев
"""

from typing import Optional

from ..config import settings


class CommentsConfig:
    """Конфигурация для модуля комментариев"""

    # Настройки пагинации
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    MIN_SEARCH_LENGTH = 2

    # Настройки поиска
    SEARCH_TIMEOUT = 30  # секунды

    # Настройки кеширования
    CACHE_COMMENT_TTL = 300  # 5 минут
    CACHE_STATS_TTL = 60  # 1 минута

    # Настройки массовых операций
    MAX_BULK_SIZE = 1000

    # Настройки валидации
    MAX_COMMENT_LENGTH = 10000
    MAX_AUTHOR_NAME_LENGTH = 255

    @classmethod
    def get_page_size(cls, requested_size: Optional[int] = None) -> int:
        """Получить размер страницы с валидацией"""
        if requested_size is None:
            return cls.DEFAULT_PAGE_SIZE

        return max(
            cls.DEFAULT_PAGE_SIZE, min(requested_size, cls.MAX_PAGE_SIZE)
        )

    @classmethod
    def validate_search_query(cls, query: str) -> bool:
        """Валидировать поисковый запрос"""
        return len(query.strip()) >= cls.MIN_SEARCH_LENGTH

    @classmethod
    def get_cache_settings(cls) -> dict:
        """Получить настройки кеширования"""
        return {
            "enabled": settings.cache_enabled,
            "comment_ttl": cls.CACHE_COMMENT_TTL,
            "stats_ttl": cls.CACHE_STATS_TTL,
        }


# Экземпляр конфигурации
comments_config = CommentsConfig()


# Экспорт
__all__ = [
    "CommentsConfig",
    "comments_config",
]
