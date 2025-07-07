"""
Конфигурация VK Comments Parser
"""

from typing import Optional
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


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

    DATABASE_URL: PostgresDsn
    VK_ACCESS_TOKEN: str
    VK_API_VERSION: str = "5.131"
    REDIS_URL: str = "redis://redis:6379/0"

    def get_cors_origins(self) -> list[str]:
        """Получить список CORS origins"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"


# Глобальный объект настроек
settings = Settings()
