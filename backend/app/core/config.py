"""
Конфигурация VK Comments Parser
"""

from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    user: str = Field(alias="DB_USER", default="postgres")
    password: str = Field(alias="DB_PASSWORD", default="postgres")
    host: str = Field(alias="DB_HOST", default="postgres")
    port: int = Field(alias="DB_PORT", default=5432)
    name: str = Field(alias="DB_NAME", default="vk_parser")
    url: Optional[PostgresDsn] = None

    @field_validator("url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v, info):
        values = info.data
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("user"),
                password=values.get("password"),
                host=values.get("host"),
                port=values.get("port"),
                path=values.get("name") or "",
            )
        )


class VKSettings(BaseSettings):
    access_token: str = Field(default="stub_token", alias="VK_ACCESS_TOKEN")
    api_version: str = Field(default="5.131", alias="VK_API_VERSION")
    requests_per_second: int = Field(default=3, alias="VK_REQUESTS_PER_SECOND")


class Settings(BaseSettings):
    app_name: str = "VK Comments Parser"
    debug: bool = Field(default=False)
    api_v1_str: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        alias="CORS_ORIGINS",
    )
    database: DatabaseSettings = DatabaseSettings()
    redis_url: Optional[RedisDsn] = Field(default=None, alias="REDIS_URL")
    vk: VKSettings = VKSettings()
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    def get_cors_origins(self) -> list[str]:
        return self.cors_origins


# Глобальный объект настроек
settings = Settings()
