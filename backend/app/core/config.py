"""
Конфигурация VK Comments Parser
"""

from typing import Optional
from pathlib import Path
from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    # Application
    app_name: str = "VK Comments Parser"
    debug: bool = Field(default=False)

    # API
    api_v1_str: str = "/api/v1"

    # CORS - поддержка переменной окружения CORS_ORIGINS
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000", alias="CORS_ORIGINS"
    )

    # Database connection components from .env
    db_user: str = Field(alias="DB_USER", default="postgres")
    db_password: str = Field(alias="DB_PASSWORD", default="postgres")
    db_host: str = Field(alias="DB_HOST", default="postgres")
    db_port: int = Field(alias="DB_PORT", default=5432)
    db_name: str = Field(alias="DB_NAME", default="vk_parser")

    # Assembled Database URL
    database_url: Optional[PostgresDsn] = None

    @validator("database_url", pre=True, always=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("db_user"),
                password=values.get("db_password"),
                host=values.get("db_host"),
                port=values.get("db_port"),
                path=values.get("db_name") or "",
            )
        )

    # Redis
    redis_url: str = Field(alias="REDIS_URL", default="redis://redis:6379/0")

    # VK API Settings
    vk_access_token: str = Field(
        alias="VK_ACCESS_TOKEN", description="VK API access token"
    )
    vk_api_version: str = Field(default="5.131", alias="VK_API_VERSION")
    vk_requests_per_second: int = Field(
        default=3,
        alias="VK_REQUESTS_PER_SECOND",
        description="Максимальное количество запросов к VK API в секунду",
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    def get_cors_origins(self) -> list[str]:
        """Получить список CORS origins"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Глобальный объект настроек
settings = Settings()
