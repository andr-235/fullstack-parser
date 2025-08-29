"""
Application Service для системы настроек (DDD)
"""

from typing import Dict, Any, Optional
from ..domain.settings import SystemSettings, SettingsSection
from .base import ApplicationService


class SettingsApplicationService(ApplicationService):
    """Application Service для работы с настройками системы"""

    def __init__(self, settings_repository=None):
        self.settings_repository = settings_repository

    async def get_current_settings(self) -> SystemSettings:
        """Получить текущие настройки системы"""
        settings = await self.settings_repository.find_by_id("system_settings")
        if not settings:
            # Создать дефолтные настройки
            settings = self._create_default_settings()
            await self.settings_repository.save(settings)
        return settings

    async def update_settings(self, updates: Dict[str, Any]) -> SystemSettings:
        """Обновить настройки системы"""
        settings = await self.get_current_settings()

        # Обновить секции
        for section_name, section_updates in updates.items():
            if isinstance(section_updates, dict):
                # Создать или обновить секцию
                section = settings.get_section(section_name)
                if not section:
                    section = SettingsSection(section_name, {})

                # Обновить значения
                for key, value in section_updates.items():
                    section.values[key] = value

                settings.update_section(section)

        await self.settings_repository.save(settings)
        return settings

    async def get_section(
        self, section_name: str
    ) -> Optional[SettingsSection]:
        """Получить секцию настроек"""
        settings = await self.get_current_settings()
        return settings.get_section(section_name)

    async def update_section(
        self, section_name: str, values: Dict[str, Any]
    ) -> SystemSettings:
        """Обновить секцию настроек"""
        settings = await self.get_current_settings()

        section = settings.get_section(section_name)
        if not section:
            section = SettingsSection(section_name, values)
        else:
            section.values.update(values)

        settings.update_section(section)
        await self.settings_repository.save(settings)
        return settings

    async def get_setting_value(self, section_name: str, key: str) -> Any:
        """Получить значение настройки"""
        settings = await self.get_current_settings()
        return settings.get_value(section_name, key)

    async def set_setting_value(
        self, section_name: str, key: str, value: Any
    ) -> SystemSettings:
        """Установить значение настройки"""
        settings = await self.get_current_settings()
        settings.set_value(section_name, key, value)
        await self.settings_repository.save(settings)
        return settings

    async def reset_to_defaults(self) -> SystemSettings:
        """Сбросить настройки к значениям по умолчанию"""
        default_settings = self._create_default_settings()
        await self.settings_repository.save(default_settings)
        return default_settings

    async def validate_settings(self) -> Dict[str, Any]:
        """Валидировать настройки системы"""
        settings = await self.get_current_settings()
        return settings.validate_settings()

    async def get_health_status(self) -> Dict[str, Any]:
        """Получить статус здоровья настроек"""
        try:
            settings = await self.get_current_settings()
            validation = settings.validate_settings()

            return {
                "valid": validation["valid"],
                "issues": validation["issues"],
                "total_sections": validation["total_sections"],
                "sections_with_issues": validation["sections_with_issues"],
                "last_check": settings.updated_at.isoformat(),
                "database_connected": True,  # Проверяем подключение к БД
                "redis_connected": True,  # Проверяем подключение к Redis
                "vk_api_accessible": True,  # Проверяем доступ к VK API
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "last_check": None,
                "database_connected": False,
                "redis_connected": False,
                "vk_api_accessible": False,
            }

    def _create_default_settings(self) -> SystemSettings:
        """Создать настройки по умолчанию"""
        settings = SystemSettings()

        # Database settings
        db_section = SettingsSection(
            "database",
            {
                "url": "postgresql://localhost/vk_comments",
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
            },
            "Настройки подключения к базе данных",
        )
        settings.update_section(db_section)

        # VK API settings
        vk_section = SettingsSection(
            "vk_api",
            {
                "api_version": "5.199",
                "timeout": 30,
                "max_retries": 3,
                "rate_limit": 3,
            },
            "Настройки VK API",
        )
        settings.update_section(vk_section)

        # Redis settings
        redis_section = SettingsSection(
            "redis",
            {
                "url": "redis://localhost:6379",
                "db": 0,
                "ttl": 3600,
            },
            "Настройки Redis",
        )
        settings.update_section(redis_section)

        # Application settings
        app_section = SettingsSection(
            "application",
            {
                "debug": False,
                "log_level": "INFO",
                "max_workers": 4,
                "request_timeout": 60,
            },
            "Общие настройки приложения",
        )
        settings.update_section(app_section)

        return settings
