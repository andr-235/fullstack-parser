"""
Конфигурация VK Comments Parser
"""

import json
from typing import Optional

from pydantic import ConfigDict, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    model_config = ConfigDict(extra="allow")

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
    model_config = ConfigDict(extra="allow")
    access_token: str = Field(default="stub_token", alias="VK_ACCESS_TOKEN")
    api_version: str = Field(default="5.131", alias="VK_API_VERSION")
    requests_per_second: int = Field(default=3, alias="VK_REQUESTS_PER_SECOND")


class MonitoringSettings(BaseSettings):
    model_config = ConfigDict(extra="allow")

    # Интервал запуска планировщика в секундах
    scheduler_interval_seconds: int = Field(
        default=300,
        alias="MONITORING_SCHEDULER_INTERVAL_SECONDS",  # 5 минут
    )

    # Максимальное количество групп для одновременного мониторинга
    max_concurrent_groups: int = Field(
        default=10, alias="MONITORING_MAX_CONCURRENT_GROUPS"
    )

    # Задержка между мониторингом групп в секундах
    group_delay_seconds: int = Field(
        default=1, alias="MONITORING_GROUP_DELAY_SECONDS"
    )

    # Включить автоматический запуск планировщика при старте приложения
    auto_start_scheduler: bool = Field(
        default=False, alias="MONITORING_AUTO_START_SCHEDULER"
    )


class Settings(BaseSettings):
    model_config = ConfigDict(extra="allow")

    app_name: str = "VK Comments Parser"
    debug: bool = Field(default=False)
    api_v1_str: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "https://parser.mysite.ru",
        ],
        alias="CORS_ORIGINS",
    )
    database: DatabaseSettings = DatabaseSettings()
    redis_url: Optional[RedisDsn] = Field(default=None, alias="REDIS_URL")
    vk: VKSettings = VKSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Парсит CORS_ORIGINS из различных форматов"""
        if isinstance(v, list):
            return v

        if not isinstance(v, str):
            return ["https://parser.mysite.ru"]

        v = v.strip()
        if not v:
            return ["https://parser.mysite.ru"]

        # Пробуем парсить как JSON
        try:
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
        except (json.JSONDecodeError, ValueError):
            pass

        # Парсим как строку с запятыми
        try:
            origins = [
                origin.strip() for origin in v.split(",") if origin.strip()
            ]
            return origins if origins else ["https://parser.mysite.ru"]
        except Exception:
            pass

        # Fallback к дефолтным значениям
        return ["https://parser.mysite.ru"]

    def get_cors_origins(self) -> list[str]:
        return self.cors_origins


# Глобальный объект настроек
settings = Settings()
