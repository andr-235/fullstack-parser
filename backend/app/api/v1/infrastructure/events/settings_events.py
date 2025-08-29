"""
Domain Events для настроек (DDD Infrastructure Layer)

Конкретные реализации Domain Events для работы с настройками
в рамках DDD архитектуры.
"""

from typing import List, Optional, Dict, Any
from .domain_event_publisher import DomainEvent


class SettingsUpdatedEvent(DomainEvent):
    """
    Событие обновления настроек

    Генерируется при изменении настроек приложения.
    """

    def __init__(
        self,
        section: str,
        updated_keys: List[str],
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        updated_by: Optional[str] = None,
        update_method: str = "api",
    ):
        """
        Args:
            section: Секция настроек (vk_api, monitoring, database, logging, ui)
            updated_keys: Список измененных ключей
            old_values: Старые значения
            new_values: Новые значения
            updated_by: Пользователь, выполнивший обновление
            update_method: Метод обновления (api, config, env)
        """
        super().__init__(section)  # Используем section как aggregate_id
        self.section = section
        self.updated_keys = updated_keys
        self.old_values = old_values or {}
        self.new_values = new_values or {}
        self.updated_by = updated_by
        self.update_method = update_method

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "section": self.section,
            "updated_keys": self.updated_keys,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "updated_by": self.updated_by,
            "update_method": self.update_method,
        }


class SettingsResetEvent(DomainEvent):
    """
    Событие сброса настроек

    Генерируется при сбросе настроек к значениям по умолчанию.
    """

    def __init__(
        self,
        reset_sections: List[str],
        old_settings: Optional[Dict[str, Any]] = None,
        reset_by: Optional[str] = None,
        reason: str = "manual",
    ):
        """
        Args:
            reset_sections: Список сброшенных секций
            old_settings: Старые настройки
            reset_by: Пользователь, выполнивший сброс
            reason: Причина сброса (manual, error, migration)
        """
        super().__init__("settings_reset")
        self.reset_sections = reset_sections
        self.old_settings = old_settings or {}
        self.reset_by = reset_by
        self.reason = reason

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "reset_sections": self.reset_sections,
            "old_settings": self.old_settings,
            "reset_by": self.reset_by,
            "reason": self.reason,
        }


class SettingsExportedEvent(DomainEvent):
    """
    Событие экспорта настроек

    Генерируется при экспорте настроек из системы.
    """

    def __init__(
        self,
        export_format: str,
        exported_sections: List[str],
        export_size: int,
        exported_by: Optional[str] = None,
        export_filters: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            export_format: Формат экспорта (json, yaml, etc.)
            exported_sections: Экспортированные секции
            export_size: Размер экспорта в байтах
            exported_by: Пользователь, выполнивший экспорт
            export_filters: Фильтры экспорта
        """
        super().__init__("settings_export")
        self.export_format = export_format
        self.exported_sections = exported_sections
        self.export_size = export_size
        self.exported_by = exported_by
        self.export_filters = export_filters or {}

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "export_format": self.export_format,
            "exported_sections": self.exported_sections,
            "export_size": self.export_size,
            "exported_by": self.exported_by,
            "export_filters": self.export_filters,
        }


class SettingsImportedEvent(DomainEvent):
    """
    Событие импорта настроек

    Генерируется при импорте настроек в систему.
    """

    def __init__(
        self,
        import_format: str,
        imported_sections: List[str],
        merge_mode: bool,
        imported_count: int,
        imported_by: Optional[str] = None,
        import_source: Optional[str] = None,
    ):
        """
        Args:
            import_format: Формат импорта (json, yaml, etc.)
            imported_sections: Импортированные секции
            merge_mode: Режим слияния (True - merge, False - replace)
            imported_count: Количество импортированных настроек
            imported_by: Пользователь, выполнивший импорт
            import_source: Источник импорта (file, api, etc.)
        """
        super().__init__("settings_import")
        self.import_format = import_format
        self.imported_sections = imported_sections
        self.merge_mode = merge_mode
        self.imported_count = imported_count
        self.imported_by = imported_by
        self.import_source = import_source

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "import_format": self.import_format,
            "imported_sections": self.imported_sections,
            "merge_mode": self.merge_mode,
            "imported_count": self.imported_count,
            "imported_by": self.imported_by,
            "import_source": self.import_source,
        }


class SettingsValidationFailedEvent(DomainEvent):
    """
    Событие ошибки валидации настроек

    Генерируется при обнаружении ошибок валидации настроек.
    """

    def __init__(
        self,
        section: str,
        validation_errors: List[str],
        invalid_values: Optional[Dict[str, Any]] = None,
        validation_context: Optional[str] = None,
    ):
        """
        Args:
            section: Секция с ошибками валидации
            validation_errors: Список ошибок валидации
            invalid_values: Недействительные значения
            validation_context: Контекст валидации
        """
        super().__init__(section)
        self.section = section
        self.validation_errors = validation_errors
        self.invalid_values = invalid_values or {}
        self.validation_context = validation_context
        self.error_count = len(validation_errors)

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "section": self.section,
            "validation_errors": self.validation_errors,
            "invalid_values": self.invalid_values,
            "validation_context": self.validation_context,
            "error_count": self.error_count,
        }


class SettingsCacheClearedEvent(DomainEvent):
    """
    Событие очистки кеша настроек

    Генерируется при принудительной очистке кеша настроек.
    """

    def __init__(
        self,
        cache_type: str = "settings",
        cleared_by: Optional[str] = None,
        reason: str = "manual",
        cache_age_seconds: Optional[int] = None,
    ):
        """
        Args:
            cache_type: Тип очищенного кеша
            cleared_by: Пользователь, выполнивший очистку
            reason: Причина очистки (manual, ttl, error)
            cache_age_seconds: Возраст кеша в секундах
        """
        super().__init__("settings_cache")
        self.cache_type = cache_type
        self.cleared_by = cleared_by
        self.reason = reason
        self.cache_age_seconds = cache_age_seconds

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "cache_type": self.cache_type,
            "cleared_by": self.cleared_by,
            "reason": self.reason,
            "cache_age_seconds": self.cache_age_seconds,
        }


# Вспомогательные функции для создания событий


def create_settings_updated_event(
    section: str,
    updated_keys: List[str],
    updated_by: Optional[str] = None,
) -> SettingsUpdatedEvent:
    """
    Создать событие обновления настроек

    Args:
        section: Секция настроек
        updated_keys: Измененные ключи
        updated_by: Пользователь, выполнивший обновление

    Returns:
        SettingsUpdatedEvent
    """
    return SettingsUpdatedEvent(
        section=section,
        updated_keys=updated_keys,
        updated_by=updated_by,
    )


def create_settings_reset_event(
    reset_sections: List[str],
    reset_by: Optional[str] = None,
) -> SettingsResetEvent:
    """
    Создать событие сброса настроек

    Args:
        reset_sections: Сбросенные секции
        reset_by: Пользователь, выполнивший сброс

    Returns:
        SettingsResetEvent
    """
    return SettingsResetEvent(
        reset_sections=reset_sections,
        reset_by=reset_by,
    )


def create_settings_exported_event(
    export_format: str,
    exported_sections: List[str],
    export_size: int,
    exported_by: Optional[str] = None,
) -> SettingsExportedEvent:
    """
    Создать событие экспорта настроек

    Args:
        export_format: Формат экспорта
        exported_sections: Экспортированные секции
        export_size: Размер экспорта
        exported_by: Пользователь, выполнивший экспорт

    Returns:
        SettingsExportedEvent
    """
    return SettingsExportedEvent(
        export_format=export_format,
        exported_sections=exported_sections,
        export_size=export_size,
        exported_by=exported_by,
    )


def create_settings_validation_failed_event(
    section: str,
    validation_errors: List[str],
    validation_context: Optional[str] = None,
) -> SettingsValidationFailedEvent:
    """
    Создать событие ошибки валидации настроек

    Args:
        section: Секция с ошибками
        validation_errors: Ошибки валидации
        validation_context: Контекст валидации

    Returns:
        SettingsValidationFailedEvent
    """
    return SettingsValidationFailedEvent(
        section=section,
        validation_errors=validation_errors,
        validation_context=validation_context,
    )
