"""
SettingsService - DDD Application Service для управления настройками

Мигрирован из app/services/settings_service.py
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class SettingsService:
    """
    DDD Application Service для управления настройками приложения.

    Предоставляет высокоуровневый интерфейс для:
    - Получения текущих настроек
    - Обновления настроек
    - Сброса к значениям по умолчанию
    - Управления различными секциями настроек
    """

    def __init__(self, settings_repository=None, cache_service=None):
        """
        Инициализация SettingsService.

        Args:
            settings_repository: Репозиторий настроек
            cache_service: Сервис кеширования
        """
        self.settings_repository = settings_repository
        self.cache_service = cache_service
        self._settings_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 300  # 5 минут

    # =============== МИГРАЦИЯ SettingsService В DDD ===============

    async def get_current_settings(self) -> Dict[str, Any]:
        """
        Получить текущие настройки приложения (мигрировано из SettingsService)

        Returns:
            Текущие настройки приложения
        """
        # Проверяем кеш
        if self._is_cache_valid():
            return self._settings_cache

        # Загружаем настройки из конфигурации
        current_settings = await self._load_settings_from_config()

        # Обновляем кеш
        self._update_cache(current_settings)
        return current_settings

    async def update_settings(
        self, settings_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить настройки приложения (мигрировано из SettingsService)

        Args:
            settings_data: Данные для обновления настроек

        Returns:
            Обновленные настройки
        """
        current_settings = await self.get_current_settings()

        # Обновляем только переданные секции
        if "vk_api" in settings_data:
            current_settings["vk_api"].update(settings_data["vk_api"])
        if "monitoring" in settings_data:
            current_settings["monitoring"].update(settings_data["monitoring"])
        if "database" in settings_data:
            current_settings["database"].update(settings_data["database"])
        if "logging" in settings_data:
            current_settings["logging"].update(settings_data["logging"])
        if "ui" in settings_data:
            current_settings["ui"].update(settings_data["ui"])

        # Валидируем обновленные настройки
        await self._validate_settings(current_settings)

        # Применяем настройки
        await self._apply_settings(current_settings)

        # Публикуем Domain Event об обновлении настроек
        from ..infrastructure.events.settings_events import (
            SettingsUpdatedEvent,
            create_settings_updated_event,
        )
        from ..infrastructure.events.domain_event_publisher import (
            publish_domain_event,
        )

        for section in settings_data.keys():
            settings_updated_event = create_settings_updated_event(
                section=section,
                updated_keys=(
                    list(settings_data[section].keys())
                    if isinstance(settings_data[section], dict)
                    else []
                ),
                updated_by=None,  # TODO: передать реального пользователя
            )
            await publish_domain_event(settings_updated_event)

        # Обновляем кеш
        self._update_cache(current_settings)

        return current_settings

    async def reset_to_defaults(self) -> Dict[str, Any]:
        """
        Сбросить настройки к значениям по умолчанию (мигрировано из SettingsService)

        Returns:
            Настройки по умолчанию
        """
        default_settings = {
            "vk_api": {
                "access_token": "",
                "api_version": "5.131",
                "requests_per_second": 3,
            },
            "monitoring": {
                "scheduler_interval_seconds": 300,
                "max_concurrent_groups": 10,
                "group_delay_seconds": 1,
                "auto_start_scheduler": False,
            },
            "database": {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_recycle": 3600,
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "include_timestamp": True,
            },
            "ui": {
                "theme": "system",
                "auto_refresh": True,
                "refresh_interval": 30,
                "items_per_page": 20,
                "show_notifications": True,
            },
        }

        # Применяем дефолтные настройки
        await self._apply_settings(default_settings)

        # Публикуем Domain Event о сбросе настроек
        from ..infrastructure.events.settings_events import (
            SettingsResetEvent,
            create_settings_reset_event,
        )
        from ..infrastructure.events.domain_event_publisher import (
            publish_domain_event,
        )

        settings_reset_event = create_settings_reset_event(
            reset_sections=list(default_settings.keys()),
            reset_by=None,  # TODO: передать реального пользователя
            reason="api_request",
        )
        await publish_domain_event(settings_reset_event)

        # Обновляем кеш
        self._update_cache(default_settings)

        return default_settings

    async def get_settings_by_section(self, section: str) -> Dict[str, Any]:
        """
        Получить настройки конкретной секции (мигрировано из SettingsService)

        Args:
            section: Название секции (vk_api, monitoring, database, logging, ui)

        Returns:
            Настройки секции
        """
        current_settings = await self.get_current_settings()

        if section not in current_settings:
            raise ValueError(f"Unknown settings section: {section}")

        return current_settings[section]

    async def update_settings_section(
        self, section: str, section_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить настройки конкретной секции (мигрировано из SettingsService)

        Args:
            section: Название секции
            section_data: Данные для обновления секции

        Returns:
            Обновленные настройки секции
        """
        current_settings = await self.get_current_settings()

        if section not in current_settings:
            raise ValueError(f"Unknown settings section: {section}")

        # Обновляем секцию
        current_settings[section].update(section_data)

        # Валидируем обновленные настройки
        await self._validate_settings(current_settings)

        # Применяем настройки
        await self._apply_settings(current_settings)

        # Обновляем кеш
        self._update_cache(current_settings)

        return current_settings[section]

    async def export_settings(self) -> Dict[str, Any]:
        """
        Экспортировать все настройки (мигрировано из SettingsService)

        Returns:
            Все настройки с метаданными
        """
        current_settings = await self.get_current_settings()

        return {
            "settings": current_settings,
            "exported_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "format": "json",
        }

    async def import_settings(
        self, settings_data: Dict[str, Any], merge: bool = True
    ) -> Dict[str, Any]:
        """
        Импортировать настройки (мигрировано из SettingsService)

        Args:
            settings_data: Данные настроек для импорта
            merge: Объединить с существующими или заменить полностью

        Returns:
            Импортированные настройки
        """
        if merge:
            current_settings = await self.get_current_settings()
            # Рекурсивно объединяем настройки
            updated_settings = self._deep_merge(
                current_settings, settings_data.get("settings", {})
            )
        else:
            updated_settings = settings_data.get("settings", {})

        # Валидируем импортированные настройки
        await self._validate_settings(updated_settings)

        # Применяем настройки
        await self._apply_settings(updated_settings)

        # Обновляем кеш
        self._update_cache(updated_settings)

        return updated_settings

    # =============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===============

    async def _load_settings_from_config(self) -> Dict[str, Any]:
        """
        Загрузить настройки из конфигурации

        Returns:
            Настройки из конфигурации
        """
        # Импортируем здесь чтобы избежать циклических зависимостей
        from app.core.config import settings

        return {
            "vk_api": {
                "access_token": settings.vk_access_token or "",
                "api_version": settings.vk_api_version or "5.131",
                "requests_per_second": 3,
            },
            "monitoring": {
                "scheduler_interval_seconds": settings.monitoring_interval
                or 300,
                "max_concurrent_groups": 5,
                "group_delay_seconds": 1,
                "auto_start_scheduler": settings.monitoring_enabled or False,
            },
            "database": {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_recycle": 3600,
            },
            "logging": {
                "level": settings.log_level or "INFO",
                "format": "json",
                "include_timestamp": True,
            },
            "ui": {
                "theme": "system",
                "auto_refresh": True,
                "refresh_interval": 30,
                "items_per_page": 20,
                "show_notifications": True,
            },
        }

    async def _validate_settings(self, settings: Dict[str, Any]) -> None:
        """
        Валидировать настройки

        Args:
            settings: Настройки для валидации

        Raises:
            ValueError: Если настройки невалидны
        """
        # Валидация VK API настроек
        if "vk_api" in settings:
            vk_api = settings["vk_api"]
            if vk_api.get("requests_per_second", 0) <= 0:
                raise ValueError("requests_per_second must be positive")

        # Валидация настроек мониторинга
        if "monitoring" in settings:
            monitoring = settings["monitoring"]
            if monitoring.get("scheduler_interval_seconds", 0) <= 0:
                raise ValueError("scheduler_interval_seconds must be positive")
            if monitoring.get("max_concurrent_groups", 0) <= 0:
                raise ValueError("max_concurrent_groups must be positive")

        # Валидация настроек базы данных
        if "database" in settings:
            database = settings["database"]
            if database.get("pool_size", 0) <= 0:
                raise ValueError("pool_size must be positive")
            if database.get("max_overflow", 0) < 0:
                raise ValueError("max_overflow must be non-negative")

    async def _apply_settings(self, settings: Dict[str, Any]) -> None:
        """
        Применить настройки к системе

        Args:
            settings: Настройки для применения
        """
        # Здесь можно добавить логику применения настроек
        # Например, обновление конфигурации логгера, перезапуск планировщика и т.д.
        pass

    def _is_cache_valid(self) -> bool:
        """
        Проверить валидность кеша

        Returns:
            True если кеш валиден
        """
        if not self._settings_cache or not self._cache_timestamp:
            return False

        elapsed = (datetime.utcnow() - self._cache_timestamp).total_seconds()
        return elapsed < self._cache_ttl

    def _update_cache(self, settings: Dict[str, Any]) -> None:
        """
        Обновить кеш настроек

        Args:
            settings: Настройки для кеширования
        """
        self._settings_cache = settings.copy()
        self._cache_timestamp = datetime.utcnow()

    def _deep_merge(
        self, base: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Рекурсивно объединить словари

        Args:
            base: Базовый словарь
            update: Словарь с обновлениями

        Returns:
            Объединенный словарь
        """
        result = base.copy()

        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result
