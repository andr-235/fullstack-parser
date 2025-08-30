"""
Конфигурация модуля Keywords

Содержит настройки специфичные для модуля управления ключевыми словами
"""

from typing import Optional, List

from ..config import settings


class KeywordsConfig:
    """Конфигурация для модуля ключевых слов"""

    # Настройки ключевых слов
    MAX_KEYWORD_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_CATEGORY_LENGTH = 100
    DEFAULT_PRIORITY = 5
    MIN_PRIORITY = 1
    MAX_PRIORITY = 10

    # Настройки пагинации
    DEFAULT_LIMIT = 50
    MAX_LIMIT = 100
    MIN_LIMIT = 1

    # Настройки массовых операций
    MAX_KEYWORDS_PER_REQUEST = 100
    MAX_BULK_ACTIONS = 100

    # Настройки поиска
    SEARCH_TIMEOUT_SECONDS = 5.0
    MAX_SEARCH_RESULTS = 200

    # Настройки экспорта/импорта
    ALLOWED_EXPORT_FORMATS = ["json", "csv", "txt"]
    MAX_EXPORT_SIZE = 1000
    IMPORT_BATCH_SIZE = 50

    # Настройки кеширования
    CACHE_KEYWORD_TTL = 3600  # 1 час
    CACHE_SEARCH_TTL = 1800  # 30 минут
    CACHE_STATS_TTL = 300  # 5 минут

    # Настройки категорий
    DEFAULT_CATEGORY = "general"
    MAX_CATEGORIES_PER_KEYWORD = 1
    CATEGORY_CACHE_TTL = 1800  # 30 минут

    # Настройки валидации
    VALIDATE_KEYWORDS_ON_CREATE = True
    VALIDATE_KEYWORDS_ON_UPDATE = True
    SKIP_DUPLICATE_VALIDATION = False

    # Настройки статистики
    STATS_UPDATE_INTERVAL = 300  # 5 минут
    STATS_RETENTION_DAYS = 30
    ENABLE_ADVANCED_STATS = True

    # Настройки производительности
    ENABLE_CACHING = True
    ENABLE_SEARCH_INDEX = False  # Для будущих улучшений
    BATCH_PROCESSING_ENABLED = True

    # Настройки логирования
    LOG_KEYWORD_OPERATIONS = True
    LOG_BULK_OPERATIONS = True
    LOG_SEARCH_QUERIES = False  # Может быть много логов

    @classmethod
    def get_keyword_limits(cls) -> dict:
        """Получить лимиты для ключевых слов"""
        return {
            "max_length": cls.MAX_KEYWORD_LENGTH,
            "max_description_length": cls.MAX_DESCRIPTION_LENGTH,
            "max_category_length": cls.MAX_CATEGORY_LENGTH,
            "min_priority": cls.MIN_PRIORITY,
            "max_priority": cls.MAX_PRIORITY,
        }

    @classmethod
    def get_pagination_config(cls) -> dict:
        """Получить конфигурацию пагинации"""
        return {
            "default_limit": cls.DEFAULT_LIMIT,
            "max_limit": cls.MAX_LIMIT,
            "min_limit": cls.MIN_LIMIT,
        }

    @classmethod
    def get_bulk_config(cls) -> dict:
        """Получить конфигурацию массовых операций"""
        return {
            "max_keywords_per_request": cls.MAX_KEYWORDS_PER_REQUEST,
            "max_bulk_actions": cls.MAX_BULK_ACTIONS,
            "import_batch_size": cls.IMPORT_BATCH_SIZE,
        }

    @classmethod
    def get_search_config(cls) -> dict:
        """Получить конфигурацию поиска"""
        return {
            "timeout_seconds": cls.SEARCH_TIMEOUT_SECONDS,
            "max_results": cls.MAX_SEARCH_RESULTS,
            "enable_index": cls.ENABLE_SEARCH_INDEX,
        }

    @classmethod
    def get_export_config(cls) -> dict:
        """Получить конфигурацию экспорта"""
        return {
            "allowed_formats": cls.ALLOWED_EXPORT_FORMATS,
            "max_export_size": cls.MAX_EXPORT_SIZE,
        }

    @classmethod
    def get_cache_config(cls) -> dict:
        """Получить конфигурацию кеширования"""
        return {
            "keyword_ttl": cls.CACHE_KEYWORD_TTL,
            "search_ttl": cls.CACHE_SEARCH_TTL,
            "stats_ttl": cls.CACHE_STATS_TTL,
            "category_ttl": cls.CATEGORY_CACHE_TTL,
            "enabled": cls.ENABLE_CACHING,
        }

    @classmethod
    def get_validation_config(cls) -> dict:
        """Получить конфигурацию валидации"""
        return {
            "validate_on_create": cls.VALIDATE_KEYWORDS_ON_CREATE,
            "validate_on_update": cls.VALIDATE_KEYWORDS_ON_UPDATE,
            "skip_duplicate_validation": cls.SKIP_DUPLICATE_VALIDATION,
        }

    @classmethod
    def get_logging_config(cls) -> dict:
        """Получить конфигурацию логирования"""
        return {
            "log_operations": cls.LOG_KEYWORD_OPERATIONS,
            "log_bulk_operations": cls.LOG_BULK_OPERATIONS,
            "log_search_queries": cls.LOG_SEARCH_QUERIES,
        }

    @classmethod
    def validate_keyword_length(cls, word: str) -> bool:
        """Проверить длину ключевого слова"""
        return len(word) <= cls.MAX_KEYWORD_LENGTH

    @classmethod
    def validate_description_length(cls, description: str) -> bool:
        """Проверить длину описания"""
        return len(description) <= cls.MAX_DESCRIPTION_LENGTH

    @classmethod
    def validate_category_length(cls, category: str) -> bool:
        """Проверить длину категории"""
        return len(category) <= cls.MAX_CATEGORY_LENGTH

    @classmethod
    def validate_priority(cls, priority: int) -> bool:
        """Проверить приоритет"""
        return cls.MIN_PRIORITY <= priority <= cls.MAX_PRIORITY

    @classmethod
    def validate_bulk_size(cls, size: int) -> bool:
        """Проверить размер пакета"""
        return 1 <= size <= cls.MAX_KEYWORDS_PER_REQUEST

    @classmethod
    def is_export_format_allowed(cls, format_type: str) -> bool:
        """Проверить допустимость формата экспорта"""
        return format_type in cls.ALLOWED_EXPORT_FORMATS

    @classmethod
    def get_default_category(cls) -> str:
        """Получить категорию по умолчанию"""
        return cls.DEFAULT_CATEGORY

    @classmethod
    def should_log_operation(cls, operation: str) -> bool:
        """Определить, нужно ли логировать операцию"""
        if not cls.LOG_KEYWORD_OPERATIONS:
            return False

        if operation.startswith("bulk") and not cls.LOG_BULK_OPERATIONS:
            return False

        if operation == "search" and not cls.LOG_SEARCH_QUERIES:
            return False

        return True


# Экземпляр конфигурации
keywords_config = KeywordsConfig()


# Экспорт
__all__ = [
    "KeywordsConfig",
    "keywords_config",
]
