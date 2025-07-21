"""
Схемы для настроек приложения
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class VKAPISettings(BaseModel):
    """Настройки VK API"""

    access_token: str = Field(..., description="VK Access Token")
    api_version: str = Field(default="5.131", description="Версия VK API")
    requests_per_second: int = Field(
        default=3, ge=1, le=20, description="Запросов в секунду"
    )


class MonitoringSettings(BaseModel):
    """Настройки мониторинга"""

    scheduler_interval_seconds: int = Field(
        default=300, ge=60, le=3600, description="Интервал планировщика (сек)"
    )
    max_concurrent_groups: int = Field(
        default=10, ge=1, le=50, description="Макс. групп одновременно"
    )
    group_delay_seconds: int = Field(
        default=1, ge=0, le=10, description="Задержка между группами (сек)"
    )
    auto_start_scheduler: bool = Field(
        default=False, description="Автозапуск планировщика"
    )


class DatabaseSettings(BaseModel):
    """Настройки базы данных"""

    pool_size: int = Field(
        default=10, ge=5, le=50, description="Размер пула соединений"
    )
    max_overflow: int = Field(
        default=20, ge=10, le=100, description="Макс. переполнение пула"
    )
    pool_recycle: int = Field(
        default=3600,
        ge=300,
        le=7200,
        description="Пересоздание соединений (сек)",
    )


class LoggingSettings(BaseModel):
    """Настройки логирования"""

    level: str = Field(default="INFO", description="Уровень логирования")
    format: str = Field(default="json", description="Формат логов")
    include_timestamp: bool = Field(
        default=True, description="Включать временные метки"
    )


class UISettings(BaseModel):
    """Настройки пользовательского интерфейса"""

    theme: str = Field(default="system", description="Тема интерфейса")
    auto_refresh: bool = Field(
        default=True, description="Автообновление данных"
    )
    refresh_interval: int = Field(
        default=30, ge=10, le=300, description="Интервал обновления (сек)"
    )
    items_per_page: int = Field(
        default=20, ge=10, le=100, description="Элементов на странице"
    )
    show_notifications: bool = Field(
        default=True, description="Показывать уведомления"
    )


class ApplicationSettings(BaseModel):
    """Полные настройки приложения"""

    vk_api: VKAPISettings
    monitoring: MonitoringSettings
    database: DatabaseSettings
    logging: LoggingSettings
    ui: UISettings


class SettingsUpdateRequest(BaseModel):
    """Запрос на обновление настроек"""

    vk_api: Optional[VKAPISettings] = None
    monitoring: Optional[MonitoringSettings] = None
    database: Optional[DatabaseSettings] = None
    logging: Optional[LoggingSettings] = None
    ui: Optional[UISettings] = None


class SettingsResponse(BaseModel):
    """Ответ с настройками"""

    settings: ApplicationSettings
    message: str = "Настройки успешно загружены"
