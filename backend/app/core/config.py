"""
Конфигурация VK Comments Parser
"""

from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    # Application
    app_name: str = "VK Comments Parser"
    debug: bool = Field(default=False)

    # API
    api_v1_str: str = "/api/v1"

    # CORS - упрощенная конфигурация
    cors_origins: str = Field(default="http://localhost:3000")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/vk_parser"
    )

    # Redis
    redis_url: str = Field(default="redis://redis:6379/0")

    # VK API Settings (optional for testing)
    vk_access_token: str = Field(
        default="your-vk-token", description="VK API access token"
    )
    vk_api_version: str = Field(default="5.131")
    vk_app_id: Optional[str] = Field(default=None)

    # VK API Rate Limits
    vk_requests_per_second: int = Field(default=3)
    vk_max_comments_per_request: int = Field(default=100)

    # Parser Settings
    parser_batch_size: int = Field(default=50)
    parser_max_posts_per_group: int = Field(default=1000)
    parser_schedule_interval: int = Field(default=3600)  # seconds

    # Logging
    log_level: str = Field(default="INFO")

    def get_cors_origins(self) -> List[str]:
        """Получить список CORS origins"""
        if "," in self.cors_origins:
            return [url.strip() for url in self.cors_origins.split(",") if url.strip()]
        return [self.cors_origins.strip()]

    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


# Глобальный объект настроек
settings = Settings()
