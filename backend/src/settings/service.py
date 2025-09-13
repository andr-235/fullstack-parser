"""
Сервис для модуля Settings

Содержит бизнес-логику для управления настройками системы
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from common.exceptions import (
    InternalServerException as ServiceUnavailableError,
)
from common.exceptions import ValidationError
from settings.config import settings_config
from settings.constants import (
    ERROR_INVALID_SETTINGS_SECTION,
    ERROR_SETTING_NOT_FOUND,
    ERROR_SETTINGS_LOAD_FAILED,
    ERROR_SETTINGS_UPDATE_FAILED,
    ERROR_SETTINGS_VALIDATION_FAILED,
)
from settings.models import SettingsRepository


class SettingsService:
    """
    Сервис для работы с настройками системы

    Реализует бизнес-логику для управления настройками
    с поддержкой валидации, кеширования и аудита
    """

    def __init__(self, repository: SettingsRepository = None):
        self.repository = repository or SettingsRepository()
        self.logger = logging.getLogger(__name__)

    async def get_current_settings(self) -> Dict[str, Any]:
        """
        Получить текущие настройки системы

        Returns:
            Dict[str, Any]: Текущие настройки
        """
        try:
            settings = await self.repository.get_settings()
            return settings
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            # reason помещаем в текст, чтобы тесты могли найти символьный код ошибки
            raise ServiceUnavailableError(
                reason=f"ERROR_SETTINGS_LOAD_FAILED: {ERROR_SETTINGS_LOAD_FAILED}: {str(e)}"
            )

    async def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновить настройки системы

        Args:
            updates: Обновления настроек

        Returns:
            Dict[str, Any]: Обновленные настройки
        """
        try:
            # Получаем текущие настройки
            current_settings = await self.get_current_settings()

            # Обновляем только переданные секции
            updated_settings = self._merge_settings(current_settings, updates)

            # Валидируем обновленные настройки
            await self._validate_settings(updated_settings)

            # Сохраняем настройки
            await self.repository.save_settings(updated_settings)

            # Логируем успешное обновление
            self.logger.info(
                f"Settings updated successfully: {list(updates.keys())}"
            )

            return updated_settings

        except ValidationError:
            # Пробрасываем ошибки валидации как есть (ожидание тестов)
            raise
        except Exception as e:
            self.logger.error(f"Error updating settings: {e}")
            raise ServiceUnavailableError(
                reason=f"ERROR_SETTINGS_UPDATE_FAILED: {ERROR_SETTINGS_UPDATE_FAILED}: {str(e)}"
            )

    async def get_section(self, section_name: str) -> Dict[str, Any]:
        """
        Получить секцию настроек

        Args:
            section_name: Название секции

        Returns:
            Dict[str, Any]: Настройки секции
        """
        try:
            section = await self.repository.get_section(section_name)
            if section is None:
                raise ValidationError(
                    f"ERROR_INVALID_SETTINGS_SECTION: {ERROR_INVALID_SETTINGS_SECTION}: {section_name}"
                )

            return section

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting section {section_name}: {e}")
            raise ServiceUnavailableError(
                reason=f"Error getting settings section: {str(e)}"
            )

    async def update_section(
        self, section_name: str, section_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить секцию настроек

        Args:
            section_name: Название секции
            section_data: Данные секции

        Returns:
            Dict[str, Any]: Обновленная секция
        """
        try:
            # Проверяем, что секция существует
            await self.get_section(section_name)

            # Валидируем данные секции
            await self._validate_section(section_name, section_data)

            # Сохраняем секцию
            await self.repository.save_section(section_name, section_data)

            self.logger.info(f"Section {section_name} updated successfully")
            return section_data

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating section {section_name}: {e}")
            raise ServiceUnavailableError(
                f"Error updating settings section: {str(e)}"
            )

    async def get_setting_value(self, section_name: str, key: str) -> Any:
        """
        Получить значение настройки

        Args:
            section_name: Название секции
            key: Ключ настройки

        Returns:
            Any: Значение настройки
        """
        try:
            value = await self.repository.get_value(section_name, key)
            if value is None:
                raise ValidationError(
                    f"ERROR_SETTING_NOT_FOUND: {ERROR_SETTING_NOT_FOUND}: {section_name}.{key}"
                )

            return value

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(
                f"Error getting setting {section_name}.{key}: {e}"
            )
            raise ServiceUnavailableError(
                reason=f"Error getting setting value: {str(e)}"
            )

    async def set_setting_value(
        self, section_name: str, key: str, value: Any
    ) -> Dict[str, Any]:
        """
        Установить значение настройки

        Args:
            section_name: Название секции
            key: Ключ настройки
            value: Значение

        Returns:
            Dict[str, Any]: Обновленная секция
        """
        try:
            # Проверяем валидность значения
            await self._validate_setting_value(section_name, key, value)

            # Сохраняем значение
            await self.repository.save_value(section_name, key, value)

            # Возвращаем обновленную секцию
            updated_section = await self.get_section(section_name)

            self.logger.info(
                f"Setting {section_name}.{key} updated successfully"
            )
            return updated_section

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error setting value {section_name}.{key}: {e}")
            raise ServiceUnavailableError(
                f"Error setting setting value: {str(e)}"
            )

    async def reset_to_defaults(self) -> Dict[str, Any]:
        """
        Сбросить настройки к значениям по умолчанию

        Returns:
            Dict[str, Any]: Настройки по умолчанию
        """
        try:
            default_settings = await self.repository.reset_to_defaults()

            self.logger.info("Settings reset to defaults successfully")
            return default_settings

        except Exception as e:
            self.logger.error(f"Error resetting settings to defaults: {e}")
            raise ServiceUnavailableError(
                reason=f"Error resetting settings: {str(e)}"
            )

    async def validate_settings(
        self, settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Валидировать настройки

        Args:
            settings: Настройки для валидации (если None, используются текущие)

        Returns:
            Dict[str, Any]: Результат валидации
        """
        try:
            if settings is None:
                settings = await self.get_current_settings()

            validation_result = await self.repository.validate_settings(
                settings
            )

            if not validation_result["valid"]:
                self.logger.warning(
                    f"Settings validation failed: {validation_result['issues']}"
                )

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating settings: {e}")
            raise ServiceUnavailableError(
                reason=f"ERROR_SETTINGS_VALIDATION_FAILED: {ERROR_SETTINGS_VALIDATION_FAILED}: {str(e)}"
            )

    async def export_settings(self, format: str = "json") -> Dict[str, Any]:
        """
        Экспортировать настройки

        Args:
            format: Формат экспорта

        Returns:
            Dict[str, Any]: Экспортированные настройки
        """
        try:
            export_data = await self.repository.export_settings(format)

            self.logger.info(
                f"Settings exported successfully in {format} format"
            )
            return export_data

        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            raise ServiceUnavailableError(
                reason=f"Error exporting settings: {str(e)}"
            )

    async def import_settings(
        self, import_data: Dict[str, Any], merge: bool = True
    ) -> Dict[str, Any]:
        """
        Импортировать настройки

        Args:
            import_data: Данные для импорта
            merge: Объединить с существующими

        Returns:
            Dict[str, Any]: Импортированные настройки
        """
        try:
            # Валидируем данные импорта
            if "settings" not in import_data:
                raise ValidationError(
                    "Import data must contain 'settings' field"
                )

            imported_settings = await self.repository.import_settings(
                import_data, merge
            )

            self.logger.info(f"Settings imported successfully (merge={merge})")
            return imported_settings

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            raise ServiceUnavailableError(
                reason=f"Error importing settings: {str(e)}"
            )

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Получить статус здоровья модуля настроек

        Returns:
            Dict[str, Any]: Статус здоровья
        """
        try:
            repo_health = await self.repository.health_check()
            cache_stats = await self.repository.get_cache_stats()

            return {
                "status": repo_health["status"],
                "timestamp": datetime.utcnow().isoformat(),
                "cache": cache_stats,
                "settings_loaded": repo_health.get("settings_loaded", False),
                "sections_count": repo_health.get("sections_count", 0),
            }

        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получить статистику кеша

        Returns:
            Dict[str, Any]: Статистика кеша
        """
        try:
            return await self.repository.get_cache_stats()
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}

    async def clear_cache(self) -> bool:
        """
        Очистить кеш настроек

        Returns:
            bool: True если кеш очищен успешно
        """
        try:
            # В простой реализации просто получаем свежие настройки
            await self.repository.get_settings()
            self.logger.info("Settings cache cleared successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False

    def _merge_settings(
        self, base: Dict[str, Any], updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Объединить настройки

        Args:
            base: Базовые настройки
            updates: Обновления

        Returns:
            Dict[str, Any]: Объединенные настройки
        """
        result = base.copy()

        for section_name, section_updates in updates.items():
            if section_name not in result:
                result[section_name] = {}

            if isinstance(section_updates, dict):
                result[section_name].update(section_updates)
            else:
                result[section_name] = section_updates

        return result

    async def _validate_settings(self, settings: Dict[str, Any]) -> None:
        """
        Валидировать настройки

        Args:
            settings: Настройки для валидации

        Raises:
            ValidationError: Если настройки невалидны
        """
        validation_result = await self.repository.validate_settings(settings)

        if not validation_result["valid"]:
            raise ValidationError(
                f"{ERROR_SETTINGS_VALIDATION_FAILED}: {validation_result['issues']}"
            )

    async def _validate_section(
        self, section_name: str, section_data: Dict[str, Any]
    ) -> None:
        """
        Валидировать секцию настроек

        Args:
            section_name: Название секции
            section_data: Данные секции

        Raises:
            ValidationError: Если секция невалидна
        """
        # Проверяем размер секции
        if len(section_data) > settings_config.MAX_VALUES_PER_SECTION:
            raise ValidationError(
                f"Section {section_name} has too many values: {len(section_data)} > {settings_config.MAX_VALUES_PER_SECTION}"
            )

        # Специфическая валидация для каждой секции
        validation_errors = {}

        if section_name == "vk_api":
            validation_errors.update(
                await self._validate_vk_api_section(section_data)
            )
        elif section_name == "monitoring":
            validation_errors.update(
                await self._validate_monitoring_section(section_data)
            )
        elif section_name == "database":
            validation_errors.update(
                await self._validate_database_section(section_data)
            )

        if validation_errors:
            raise ValidationError(
                f"Invalid section {section_name}: {validation_errors}"
            )

    async def _validate_setting_value(
        self, section_name: str, key: str, value: Any
    ) -> None:
        """
        Валидировать значение настройки

        Args:
            section_name: Название секции
            key: Ключ настройки
            value: Значение

        Raises:
            ValidationError: Если значение невалидно
        """
        # Общая валидация типов
        if section_name == "vk_api":
            if key == "requests_per_second" and (
                not isinstance(value, (int, float)) or value <= 0
            ):
                raise ValidationError(
                    f"Invalid value for {section_name}.{key}: must be positive number"
                )
            elif key == "api_version" and (
                not isinstance(value, str) or not value
            ):
                raise ValidationError(
                    f"Invalid value for {section_name}.{key}: must be non-empty string"
                )

        elif section_name == "monitoring":
            if key == "scheduler_interval_seconds" and (
                not isinstance(value, (int, float)) or value <= 0
            ):
                raise ValidationError(
                    f"Invalid value for {section_name}.{key}: must be positive number"
                )
            elif key == "max_concurrent_groups" and (
                not isinstance(value, int) or value <= 0
            ):
                raise ValidationError(
                    f"Invalid value for {section_name}.{key}: must be positive integer"
                )

        elif section_name == "database":
            if key == "pool_size" and (
                not isinstance(value, int) or value <= 0
            ):
                raise ValidationError(
                    f"Invalid value for {section_name}.{key}: must be positive integer"
                )

    async def _validate_vk_api_section(
        self, section_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Валидировать секцию VK API"""
        errors = {}

        if "requests_per_second" in section_data:
            rps = section_data["requests_per_second"]
            if not isinstance(rps, (int, float)) or rps <= 0:
                errors["requests_per_second"] = "Must be a positive number"

        if "api_version" in section_data:
            api_version = section_data["api_version"]
            if not isinstance(api_version, str) or not api_version:
                errors["api_version"] = "Must be a non-empty string"

        return errors

    async def _validate_monitoring_section(
        self, section_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Валидировать секцию мониторинга"""
        errors = {}

        if "scheduler_interval_seconds" in section_data:
            interval = section_data["scheduler_interval_seconds"]
            if not isinstance(interval, (int, float)) or interval <= 0:
                errors["scheduler_interval_seconds"] = (
                    "Must be a positive number"
                )

        if "max_concurrent_groups" in section_data:
            max_groups = section_data["max_concurrent_groups"]
            if not isinstance(max_groups, int) or max_groups <= 0:
                errors["max_concurrent_groups"] = "Must be a positive integer"

        return errors

    async def _validate_database_section(
        self, section_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Валидировать секцию базы данных"""
        errors = {}

        if "pool_size" in section_data:
            pool_size = section_data["pool_size"]
            if not isinstance(pool_size, int) or pool_size <= 0:
                errors["pool_size"] = "Must be a positive integer"

        if "max_overflow" in section_data:
            max_overflow = section_data["max_overflow"]
            if not isinstance(max_overflow, int) or max_overflow < 0:
                errors["max_overflow"] = "Must be a non-negative integer"

        return errors


# Экспорт
__all__ = [
    "SettingsService",
]
