"""
Конфигурация модуля Parser

Содержит настройки специфичные для модуля парсера VK с использованием Pydantic Settings
"""

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class ParserSettings(BaseSettings):
    """Настройки модуля парсера с валидацией через Pydantic"""

    # VK API настройки
    vk_api_base_url: str = Field(
        default="https://api.vk.com/method", description="Базовый URL VK API"
    )
    vk_api_version: str = Field(default="5.199", description="Версия VK API")
    vk_api_timeout: int = Field(
        default=30, ge=5, le=300, description="Таймаут VK API в секундах"
    )

    # Rate limiting
    max_requests_per_second: int = Field(
        default=3, ge=1, le=5, description="Максимум запросов в секунду"
    )
    max_posts_per_request: int = Field(
        default=10, ge=1, le=1000, description="Максимум постов за запрос"
    )
    max_comments_per_request: int = Field(
        default=100, ge=1, le=1000, description="Максимум комментариев за запрос"
    )

    # Настройки парсинга по умолчанию
    default_max_posts: int = Field(
        default=10, ge=1, le=1000, description="Максимум постов по умолчанию"
    )
    default_max_comments_per_post: int = Field(
        default=100, ge=1, le=1000, description="Максимум комментариев на пост по умолчанию"
    )
    default_force_reparse: bool = Field(
        default=False, description="Принудительный перепарсинг по умолчанию"
    )
    default_priority: Literal["low", "normal", "high"] = Field(
        default="normal", description="Приоритет по умолчанию"
    )

    # Ограничения
    max_group_ids_per_request: int = Field(
        default=100, ge=1, le=1000, description="Максимум ID групп за запрос"
    )
    max_posts_per_group: int = Field(
        default=1000, ge=1, le=10000, description="Максимум постов в группе"
    )
    max_comments_per_post: int = Field(
        default=1000, ge=1, le=10000, description="Максимум комментариев на пост"
    )

    # Настройки задач
    task_queue_size: int = Field(
        default=1000, ge=100, le=10000, description="Размер очереди задач"
    )
    max_concurrent_tasks: int = Field(
        default=5, ge=1, le=20, description="Максимум одновременных задач"
    )
    task_timeout_seconds: int = Field(
        default=3600, ge=60, le=86400, description="Таймаут задачи в секундах"
    )

    # Настройки повторных попыток
    max_retry_attempts: int = Field(
        default=3, ge=0, le=10, description="Максимум попыток повтора"
    )
    retry_delay_seconds: int = Field(
        default=5, ge=1, le=300, description="Задержка между попытками в секундах"
    )

    class Config:
        env_prefix = "PARSER_"
        case_sensitive = False


# Глобальный экземпляр настроек
parser_settings = ParserSettings()

# Экспорт
__all__ = ["ParserSettings", "parser_settings"]
