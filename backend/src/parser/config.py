"""
Конфигурация модуля Parser

Содержит настройки специфичные для модуля парсера VK
"""

from typing import Optional

from ..config import settings


class ParserConfig:
    """Конфигурация для модуля парсера"""

    # Настройки VK API
    VK_API_BASE_URL = "https://api.vk.com/method"
    VK_API_VERSION = "5.199"
    VK_API_TIMEOUT = 30  # секунды

    # Rate limiting
    MAX_REQUESTS_PER_SECOND = 3
    MAX_POSTS_PER_REQUEST = 100
    MAX_COMMENTS_PER_REQUEST = 100
    MAX_GROUPS_PER_REQUEST = 10000  # Увеличен лимит для массового парсинга
    MAX_USERS_PER_REQUEST = 1000

    # Настройки парсинга
    DEFAULT_MAX_POSTS = 100
    DEFAULT_MAX_COMMENTS_PER_POST = 100
    DEFAULT_FORCE_REPARSE = False
    DEFAULT_PRIORITY = "normal"

    # Ограничения
    MAX_GROUP_IDS_PER_REQUEST = 10000  # Увеличен лимит для массового парсинга
    MAX_POSTS_PER_GROUP = 1000
    MAX_COMMENTS_PER_POST = 1000

    # Настройки очередей задач
    TASK_QUEUE_SIZE = 1000
    MAX_CONCURRENT_TASKS = 5

    # Таймауты
    TASK_TIMEOUT_SECONDS = 3600  # 1 час
    REQUEST_TIMEOUT_SECONDS = 30
    CONNECTION_TIMEOUT_SECONDS = 10

    # Настройки повторных попыток
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 5

    @classmethod
    def get_parsing_limits(cls) -> dict:
        """Получить лимиты парсинга"""
        return {
            "max_posts": cls.MAX_POSTS_PER_REQUEST,
            "max_comments": cls.MAX_COMMENTS_PER_REQUEST,
            "max_groups": cls.MAX_GROUPS_PER_REQUEST,
            "max_users": cls.MAX_USERS_PER_REQUEST,
        }

    @classmethod
    def get_vk_api_config(cls) -> dict:
        """Получить конфигурацию VK API"""
        return {
            "base_url": cls.VK_API_BASE_URL,
            "version": cls.VK_API_VERSION,
            "timeout": cls.VK_API_TIMEOUT,
            "access_token": settings.vk_access_token,
        }

    @classmethod
    def get_task_config(cls) -> dict:
        """Получить конфигурацию задач"""
        return {
            "queue_size": cls.TASK_QUEUE_SIZE,
            "max_concurrent": cls.MAX_CONCURRENT_TASKS,
            "timeout": cls.TASK_TIMEOUT_SECONDS,
        }

    @classmethod
    def get_retry_config(cls) -> dict:
        """Получить конфигурацию повторных попыток"""
        return {
            "max_attempts": cls.MAX_RETRY_ATTEMPTS,
            "delay": cls.RETRY_DELAY_SECONDS,
        }

    @classmethod
    def validate_group_count(cls, count: int) -> bool:
        """Валидировать количество групп"""
        return 1 <= count <= cls.MAX_GROUP_IDS_PER_REQUEST

    @classmethod
    def validate_posts_count(cls, count: int) -> bool:
        """Валидировать количество постов"""
        return 1 <= count <= cls.MAX_POSTS_PER_GROUP

    @classmethod
    def validate_comments_count(cls, count: int) -> bool:
        """Валидировать количество комментариев"""
        return 1 <= count <= cls.MAX_COMMENTS_PER_POST


# Экземпляр конфигурации
parser_config = ParserConfig()


# Экспорт
__all__ = [
    "ParserConfig",
    "parser_config",
]
