"""
Сервис для управления настройками приложения
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from functools import lru_cache

import structlog
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from sqlalchemy import text
from app.schemas.settings import (
    ApplicationSettings,
    VKAPISettings,
    MonitoringSettings,
    DatabaseSettings,
    LoggingSettings,
    UISettings,
    SettingsUpdateRequest,
)

logger = structlog.get_logger()


class SettingsService:
    """Сервис для управления настройками приложения"""

    def __init__(self):
        self._settings_cache: Optional[ApplicationSettings] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 300  # 5 минут

    async def get_current_settings(self) -> ApplicationSettings:
        """Получить текущие настройки приложения"""
        # Проверяем кеш
        if self._is_cache_valid():
            return self._settings_cache

        # Загружаем настройки из конфигурации
        current_settings = ApplicationSettings(
            vk_api=VKAPISettings(
                access_token=settings.vk.access_token,
                api_version=settings.vk.api_version,
                requests_per_second=settings.vk.requests_per_second,
            ),
            monitoring=MonitoringSettings(
                scheduler_interval_seconds=settings.monitoring.scheduler_interval_seconds,
                max_concurrent_groups=settings.monitoring.max_concurrent_groups,
                group_delay_seconds=settings.monitoring.group_delay_seconds,
                auto_start_scheduler=settings.monitoring.auto_start_scheduler,
            ),
            database=DatabaseSettings(
                pool_size=10,  # Извлекаем из конфигурации БД
                max_overflow=20,
                pool_recycle=3600,
            ),
            logging=LoggingSettings(
                level=settings.log_level,
                format="json",
                include_timestamp=True,
            ),
            ui=UISettings(
                theme="system",
                auto_refresh=True,
                refresh_interval=30,
                items_per_page=20,
                show_notifications=True,
            ),
        )

        # Обновляем кеш
        self._update_cache(current_settings)
        return current_settings

    async def update_settings(
        self, request: SettingsUpdateRequest
    ) -> ApplicationSettings:
        """Обновить настройки приложения"""
        current_settings = await self.get_current_settings()

        # Обновляем только переданные секции
        if request.vk_api:
            current_settings.vk_api = request.vk_api
        if request.monitoring:
            current_settings.monitoring = request.monitoring
        if request.database:
            current_settings.database = request.database
        if request.logging:
            current_settings.logging = request.logging
        if request.ui:
            current_settings.ui = request.ui

        # Валидируем обновленные настройки
        await self._validate_settings(current_settings)

        # Применяем настройки
        await self._apply_settings(current_settings)

        # Обновляем кеш
        self._update_cache(current_settings)

        logger.info(
            "settings_updated",
            sections=list(request.dict(exclude_none=True).keys()),
        )

        return current_settings

    async def reset_to_defaults(self) -> ApplicationSettings:
        """Сбросить настройки к значениям по умолчанию"""
        default_settings = ApplicationSettings(
            vk_api=VKAPISettings(
                access_token="",
                api_version="5.131",
                requests_per_second=3,
            ),
            monitoring=MonitoringSettings(
                scheduler_interval_seconds=300,
                max_concurrent_groups=10,
                group_delay_seconds=1,
                auto_start_scheduler=False,
            ),
            database=DatabaseSettings(
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            ),
            logging=LoggingSettings(
                level="INFO",
                format="json",
                include_timestamp=True,
            ),
            ui=UISettings(
                theme="system",
                auto_refresh=True,
                refresh_interval=30,
                items_per_page=20,
                show_notifications=True,
            ),
        )

        # Применяем дефолтные настройки
        await self._apply_settings(default_settings)

        # Обновляем кеш
        self._update_cache(default_settings)

        logger.info("settings_reset_to_defaults")
        return default_settings

    async def get_health_status(self) -> Dict[str, Any]:
        """Получить статус здоровья настроек"""
        try:
            # Проверяем подключение к БД
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                database_connected = True
        except Exception as e:
            logger.warning("database_health_check_failed", error=str(e))
            database_connected = False

        # Проверяем подключение к Redis
        try:
            import redis.asyncio as redis

            redis_client = redis.from_url(settings.redis_url)
            await redis_client.ping()
            redis_connected = True
        except Exception as e:
            logger.warning("redis_health_check_failed", error=str(e))
            redis_connected = False

        # Проверяем доступность VK API
        try:
            current_settings = await self.get_current_settings()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.vk.com/method/users.get",
                    params={
                        "access_token": current_settings.vk_api.access_token,
                        "v": current_settings.vk_api.api_version,
                        "user_ids": "1",
                    },
                )
                vk_api_accessible = response.status_code == 200
        except Exception as e:
            logger.warning("vk_api_health_check_failed", error=str(e))
            vk_api_accessible = False

        return {
            "valid": True,
            "database_connected": database_connected,
            "redis_connected": redis_connected,
            "vk_api_accessible": vk_api_accessible,
            "last_check": datetime.now().isoformat(),
        }

    async def _validate_settings(self, settings: ApplicationSettings) -> None:
        """Валидировать настройки"""
        # Проверяем VK API токен
        if not settings.vk_api.access_token:
            raise ValueError("VK API токен не может быть пустым")

        # Проверяем интервалы мониторинга
        if settings.monitoring.scheduler_interval_seconds < 60:
            raise ValueError(
                "Интервал планировщика должен быть не менее 60 секунд"
            )

        if settings.monitoring.max_concurrent_groups < 1:
            raise ValueError(
                "Максимальное количество групп должно быть не менее 1"
            )

        # Проверяем настройки БД
        if settings.database.pool_size < 5:
            raise ValueError("Размер пула соединений должен быть не менее 5")

        # Проверяем уровень логирования
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if settings.logging.level.upper() not in valid_log_levels:
            raise ValueError(
                f"Неверный уровень логирования. Допустимые значения: {', '.join(valid_log_levels)}"
            )

    async def _apply_settings(self, settings: ApplicationSettings) -> None:
        """Применить настройки к системе"""
        # Применяем настройки VK API
        os.environ["VK_ACCESS_TOKEN"] = settings.vk_api.access_token
        os.environ["VK_API_VERSION"] = settings.vk_api.api_version
        os.environ["VK_REQUESTS_PER_SECOND"] = str(
            settings.vk_api.requests_per_second
        )

        # Применяем настройки мониторинга
        os.environ["MONITORING_SCHEDULER_INTERVAL_SECONDS"] = str(
            settings.monitoring.scheduler_interval_seconds
        )
        os.environ["MONITORING_MAX_CONCURRENT_GROUPS"] = str(
            settings.monitoring.max_concurrent_groups
        )
        os.environ["MONITORING_GROUP_DELAY_SECONDS"] = str(
            settings.monitoring.group_delay_seconds
        )
        os.environ["MONITORING_AUTO_START_SCHEDULER"] = str(
            settings.monitoring.auto_start_scheduler
        ).lower()

        # Применяем настройки логирования
        os.environ["LOG_LEVEL"] = settings.logging.level

        logger.info(
            "settings_applied", sections=["vk_api", "monitoring", "logging"]
        )

    def _is_cache_valid(self) -> bool:
        """Проверить валидность кеша"""
        if not self._settings_cache or not self._cache_timestamp:
            return False

        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self._cache_ttl

    def _update_cache(self, settings: ApplicationSettings) -> None:
        """Обновить кеш настроек"""
        self._settings_cache = settings
        self._cache_timestamp = datetime.now()


@lru_cache(maxsize=1)
def get_settings_service() -> SettingsService:
    """Получить экземпляр сервиса настроек"""
    return SettingsService()
