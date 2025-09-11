"""
Конфигурация модуля Parser

Содержит настройки специфичные для модуля парсера VK с использованием Pydantic Settings
"""

from typing import Optional, Literal
from pydantic import Field, validator
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
        default=3, ge=1, le=10, description="Максимум запросов в секунду"
    )
    max_posts_per_request: int = Field(
        default=10, ge=1, le=1000, description="Максимум постов за запрос"
    )
    max_comments_per_request: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Максимум комментариев за запрос",
    )
    max_groups_per_request: int = Field(
        default=10000, ge=1, le=50000, description="Максимум групп за запрос"
    )
    max_users_per_request: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Максимум пользователей за запрос",
    )

    # Настройки парсинга по умолчанию
    default_max_posts: int = Field(
        default=10, ge=1, le=1000, description="Максимум постов по умолчанию"
    )
    default_max_comments_per_post: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Максимум комментариев на пост по умолчанию",
    )
    default_force_reparse: bool = Field(
        default=False, description="Принудительный перепарсинг по умолчанию"
    )
    default_priority: Literal["low", "normal", "high"] = Field(
        default="normal", description="Приоритет по умолчанию"
    )

    # Ограничения
    max_group_ids_per_request: int = Field(
        default=10000,
        ge=1,
        le=50000,
        description="Максимум ID групп за запрос",
    )
    max_posts_per_group: int = Field(
        default=1000, ge=1, le=10000, description="Максимум постов в группе"
    )
    max_comments_per_post: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Максимум комментариев на пост",
    )

    # Лимиты запросов
    max_total_requests: int = Field(
        default=50_000_000,
        ge=100_000,
        le=100_000_000,
        description="Максимальное общее количество запросов для парсинга",
    )
    max_total_requests_warning: int = Field(
        default=5_000_000,
        ge=50_000,
        le=50_000_000,
        description="Порог предупреждения для количества запросов",
    )

    # Реалистичные коэффициенты для расчета
    avg_posts_per_group: float = Field(
        default=10.0,
        ge=1.0,
        le=100.0,
        description="Среднее количество постов в группе для расчета",
    )
    avg_comments_per_post: float = Field(
        default=5.0,
        ge=0.1,
        le=50.0,
        description="Среднее количество комментариев на пост для расчета",
    )

    # Настройки очередей задач
    task_queue_size: int = Field(
        default=1000, ge=100, le=10000, description="Размер очереди задач"
    )
    max_concurrent_tasks: int = Field(
        default=5, ge=1, le=20, description="Максимум одновременных задач"
    )

    # Таймауты
    task_timeout_seconds: int = Field(
        default=3600, ge=60, le=86400, description="Таймаут задачи в секундах"
    )
    request_timeout_seconds: int = Field(
        default=30, ge=5, le=300, description="Таймаут запроса в секундах"
    )
    connection_timeout_seconds: int = Field(
        default=10, ge=1, le=60, description="Таймаут соединения в секундах"
    )

    # Настройки повторных попыток
    max_retry_attempts: int = Field(
        default=3, ge=0, le=10, description="Максимум попыток повтора"
    )
    retry_delay_seconds: int = Field(
        default=5,
        ge=1,
        le=300,
        description="Задержка между попытками в секундах",
    )

    @validator("max_requests_per_second")
    def validate_rate_limit(cls, v):
        """Валидация rate limit"""
        if v > 5:
            raise ValueError(
                "Rate limit не должен превышать 5 запросов в секунду"
            )
        return v

    @validator("max_group_ids_per_request")
    def validate_group_limit(cls, v):
        """Валидация лимита групп"""
        if v > 20000:
            raise ValueError("Лимит групп не должен превышать 20000")
        return v

    class Config:
        env_prefix = "PARSER_"
        case_sensitive = False


# Глобальный экземпляр настроек
parser_settings = ParserSettings()


# Обратная совместимость - класс конфигурации
class ParserConfig:
    """Класс конфигурации для обратной совместимости"""

    @classmethod
    def get_parsing_limits(cls) -> dict:
        """Получить лимиты парсинга"""
        return {
            "max_posts": parser_settings.max_posts_per_request,
            "max_comments": parser_settings.max_comments_per_request,
            "max_groups": parser_settings.max_groups_per_request,
            "max_users": parser_settings.max_users_per_request,
        }

    @classmethod
    def get_vk_api_config(cls) -> dict:
        """Получить конфигурацию VK API"""
        from ..config import settings

        return {
            "base_url": parser_settings.vk_api_base_url,
            "version": parser_settings.vk_api_version,
            "timeout": parser_settings.vk_api_timeout,
            "access_token": settings.vk_access_token,
        }

    @classmethod
    def get_task_config(cls) -> dict:
        """Получить конфигурацию задач"""
        return {
            "queue_size": parser_settings.task_queue_size,
            "max_concurrent": parser_settings.max_concurrent_tasks,
            "timeout": parser_settings.task_timeout_seconds,
        }

    @classmethod
    def get_retry_config(cls) -> dict:
        """Получить конфигурацию повторных попыток"""
        return {
            "max_attempts": parser_settings.max_retry_attempts,
            "delay": parser_settings.retry_delay_seconds,
        }

    @classmethod
    def validate_group_count(cls, count: int) -> bool:
        """Валидировать количество групп"""
        return 1 <= count <= parser_settings.max_group_ids_per_request

    @classmethod
    def validate_posts_count(cls, count: int) -> bool:
        """Валидировать количество постов"""
        return 1 <= count <= parser_settings.max_posts_per_group

    @classmethod
    def validate_comments_count(cls, count: int) -> bool:
        """Валидировать количество комментариев"""
        return 1 <= count <= parser_settings.max_comments_per_post


# Экспорт
__all__ = [
    "ParserSettings",
    "ParserConfig",
    "parser_settings",
    "parser_config",
]
