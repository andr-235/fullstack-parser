"""
Упрощенная конфигурация VK Comments Parser
"""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Упрощенные настройки приложения"""

    # База данных
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/vk_parser",
        alias="DATABASE_URL",
    )

    # VK API
    vk_access_token: str = Field(default="stub_token", alias="VK_ACCESS_TOKEN")
    vk_api_version: str = Field(default="5.199", alias="VK_API_VERSION")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # Основные настройки
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Упрощенные настройки мониторинга
    monitoring_enabled: bool = Field(default=False)
    monitoring_interval: int = Field(default=300)  # 5 минут


# Глобальный объект настроек
settings = Settings()
