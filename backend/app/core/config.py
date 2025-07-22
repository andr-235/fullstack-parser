"""
Конфигурация VK Comments Parser
"""

import json
import logging
from typing import Optional

from pydantic import ConfigDict, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

# Настройка логирования для отладки
logger = logging.getLogger(__name__)


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
    api_version: str = Field(default="5.199", alias="VK_API_VERSION")
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
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )
    database: DatabaseSettings = DatabaseSettings()
    redis_url: Optional[str] = Field(
        default="redis://redis:6379/0", alias="REDIS_URL"
    )
    vk: VKSettings = VKSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    def get_cors_origins(self) -> list[str]:
        """Парсит CORS_ORIGINS из строки в список"""
        try:
            if not self.cors_origins:
                return ["http://localhost:3000", "http://127.0.0.1:3000"]

            # Пробуем парсить как JSON
            if self.cors_origins.startswith(
                "["
            ) and self.cors_origins.endswith("]"):
                try:
                    parsed = json.loads(self.cors_origins)
                    if isinstance(parsed, list):
                        return [
                            str(origin).strip() for origin in parsed if origin
                        ]

                except (json.JSONDecodeError, ValueError, TypeError):
                    pass

            # Парсим как строку с запятыми
            origins = [
                origin.strip()
                for origin in self.cors_origins.split(",")
                if origin.strip()
            ]
            return (
                origins
                if origins
                else ["http://localhost:3000", "http://127.0.0.1:3000"]
            )

        except Exception:
            # В случае любой ошибки возвращаем дефолт
            return ["http://localhost:3000", "http://127.0.0.1:3000"]


# Глобальный объект настроек
try:
    settings = Settings()

    logger.info(
        f"Settings initialized successfully. CORS_ORIGINS: {settings.cors_origins}"
    )

except Exception as e:
    logger.error(f"Failed to initialize settings: {e}")
    raise
