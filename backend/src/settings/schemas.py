"""
Pydantic схемы для модуля Settings

Определяет входные и выходные модели данных для API настроек
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Упрощенная пагинация без shared модуля
class PaginatedResponse:
    """Базовый класс для пагинированных ответов"""
    pass


class SettingsSection(BaseModel):
    """Секция настроек"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Название секции")
    values: Dict[str, Any] = Field(..., description="Значения в секции")
    description: Optional[str] = Field(None, description="Описание секции")


class SystemSettings(BaseModel):
    """Системные настройки"""

    model_config = ConfigDict(from_attributes=True)

    sections: Dict[str, SettingsSection] = Field(
        ..., description="Секции настроек"
    )


class SettingsResponse(BaseModel):
    """Ответ с настройками системы"""

    sections: Dict[str, SettingsSection] = Field(
        ..., description="Секции настроек"
    )


class SettingsSectionResponse(BaseModel):
    """Ответ с секцией настроек"""

    name: str = Field(..., description="Название секции")
    values: Dict[str, Any] = Field(..., description="Значения секции")
    description: Optional[str] = Field(None, description="Описание секции")


class SettingsUpdateRequest(BaseModel):
    """Запрос на обновление настроек"""

    sections: Dict[str, Dict[str, Any]] = Field(
        ..., description="Секции для обновления"
    )


class SettingsSectionUpdateRequest(BaseModel):
    """Запрос на обновление секции настроек"""

    values: Dict[str, Any] = Field(..., description="Новые значения секции")


class SettingsValueUpdateRequest(BaseModel):
    """Запрос на обновление значения настройки"""

    value: Any = Field(..., description="Новое значение")


class SettingsValidationResult(BaseModel):
    """Результат валидации настроек"""

    model_config = ConfigDict(from_attributes=True)

    valid: bool = Field(..., description="Валидны ли настройки")
    issues: Dict[str, Any] = Field(..., description="Проблемы валидации")
    total_sections: int = Field(..., description="Общее количество секций")
    sections_with_issues: int = Field(..., description="Секций с проблемами")


class SettingsExportResponse(BaseModel):
    """Ответ с экспортированными настройками"""

    model_config = ConfigDict(from_attributes=True)

    settings: Dict[str, Any] = Field(
        ..., description="Экспортированные настройки"
    )
    exported_at: str = Field(..., description="Время экспорта")
    version: str = Field(..., description="Версия формата")
    format: str = Field(..., description="Формат экспорта")
    sections_count: int = Field(..., description="Количество секций")


class SettingsImportRequest(BaseModel):
    """Запрос на импорт настроек"""

    settings: Dict[str, Any] = Field(..., description="Настройки для импорта")
    merge: bool = Field(True, description="Объединить с существующими")
    backup_before_import: bool = Field(
        True, description="Создать бэкап перед импортом"
    )


class SettingsHealthResponse(BaseModel):
    """Ответ со статусом здоровья настроек"""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Статус здоровья")
    timestamp: str = Field(..., description="Время проверки")
    cache: Dict[str, Any] = Field(..., description="Статистика кеша")
    settings_loaded: bool = Field(..., description="Загружены ли настройки")
    sections_count: int = Field(..., description="Количество секций")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")


class SettingsCacheStats(BaseModel):
    """Статистика кеша настроек"""

    model_config = ConfigDict(from_attributes=True)

    cache_valid: bool = Field(..., description="Валиден ли кеш")
    cache_age_seconds: float = Field(
        ..., description="Возраст кеша в секундах"
    )
    cache_size: int = Field(..., description="Размер кеша в байтах")
    sections_cached: int = Field(..., description="Количество секций в кеше")


class SettingsSummary(BaseModel):
    """Сводка по настройкам"""

    model_config = ConfigDict(from_attributes=True)

    total_sections: int = Field(..., description="Общее количество секций")
    total_keys: int = Field(..., description="Общее количество ключей")
    total_size_bytes: int = Field(..., description="Общий размер в байтах")
    value_types: Dict[str, int] = Field(
        ..., description="Распределение типов значений"
    )
    sections_list: List[str] = Field(..., description="Список секций")
    last_updated: str = Field(..., description="Время последнего обновления")


class SettingsBackup(BaseModel):
    """Резервная копия настроек"""

    model_config = ConfigDict(from_attributes=True)

    settings: Dict[str, Any] = Field(..., description="Настройки")
    backup_created_at: str = Field(..., description="Время создания бэкапа")
    version: str = Field(..., description="Версия")
    hash: str = Field(..., description="Хеш настроек")
    sections_count: int = Field(..., description="Количество секций")


class SettingsDiff(BaseModel):
    """Различия между настройками"""

    model_config = ConfigDict(from_attributes=True)

    added: Dict[str, Any] = Field(..., description="Добавленные секции")
    removed: Dict[str, Any] = Field(..., description="Удаленные секции")
    modified: Dict[str, Any] = Field(..., description="Измененные секции")


class SettingsSectionListResponse(BaseModel):
    """Ответ со списком секций настроек"""

    sections: List[str] = Field(..., description="Список названий секций")
    total_count: int = Field(..., description="Общее количество секций")


class SettingsKeyListResponse(BaseModel):
    """Ответ со списком ключей в секции"""

    section_name: str = Field(..., description="Название секции")
    keys: List[str] = Field(..., description="Список ключей")
    total_count: int = Field(..., description="Общее количество ключей")


class SettingsValueResponse(BaseModel):
    """Ответ со значением настройки"""

    section_name: str = Field(..., description="Название секции")
    key: str = Field(..., description="Ключ")
    value: Any = Field(..., description="Значение")
    value_type: str = Field(..., description="Тип значения")


class SettingsOperationResult(BaseModel):
    """Результат операции с настройками"""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(..., description="Успешность операции")
    operation: str = Field(..., description="Тип операции")
    message: str = Field(..., description="Сообщение")
    timestamp: str = Field(..., description="Время операции")
    affected_sections: List[str] = Field(..., description="Затронутые секции")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")


class SettingsBulkUpdateRequest(BaseModel):
    """Запрос на массовое обновление настроек"""

    updates: Dict[str, Dict[str, Any]] = Field(
        ..., description="Обновления по секциям"
    )
    validate_before_update: bool = Field(
        True, description="Валидировать перед обновлением"
    )
    create_backup: bool = Field(
        True, description="Создать бэкап перед обновлением"
    )


class SettingsBulkUpdateResponse(BaseModel):
    """Ответ на массовое обновление настроек"""

    model_config = ConfigDict(from_attributes=True)

    updated_sections: List[str] = Field(..., description="Обновленные секции")
    total_updates: int = Field(..., description="Общее количество обновлений")
    validation_passed: bool = Field(..., description="Прошла ли валидация")
    backup_created: bool = Field(..., description="Создан ли бэкап")
    timestamp: str = Field(..., description="Время операции")


class SettingsSearchRequest(BaseModel):
    """Запрос на поиск в настройках"""

    query: str = Field(..., description="Поисковый запрос")
    section_filter: Optional[str] = Field(None, description="Фильтр по секции")
    case_sensitive: bool = Field(
        False, description="Чувствительность к регистру"
    )


class SettingsSearchResult(BaseModel):
    """Результат поиска в настройках"""

    model_config = ConfigDict(from_attributes=True)

    section_name: str = Field(..., description="Название секции")
    key: str = Field(..., description="Ключ")
    value: Any = Field(..., description="Значение")
    match_type: str = Field(..., description="Тип совпадения")


class SettingsSearchResponse(BaseModel):
    """Ответ на поиск в настройках"""

    results: List[SettingsSearchResult] = Field(
        ..., description="Результаты поиска"
    )
    total_matches: int = Field(..., description="Общее количество совпадений")
    query: str = Field(..., description="Поисковый запрос")


class SettingsPermissionCheck(BaseModel):
    """Проверка прав доступа к настройкам"""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="ID пользователя")
    permissions: List[str] = Field(..., description="Права пользователя")
    section_name: Optional[str] = Field(None, description="Название секции")
    can_read: bool = Field(..., description="Может ли читать")
    can_write: bool = Field(..., description="Может ли писать")
    is_admin: bool = Field(..., description="Является ли админом")


# Экспорт всех схем
__all__ = [
    "SettingsSection",
    "SystemSettings",
    "SettingsResponse",
    "SettingsSectionResponse",
    "SettingsUpdateRequest",
    "SettingsSectionUpdateRequest",
    "SettingsValueUpdateRequest",
    "SettingsValidationResult",
    "SettingsExportResponse",
    "SettingsImportRequest",
    "SettingsHealthResponse",
    "SettingsCacheStats",
    "SettingsSummary",
    "SettingsBackup",
    "SettingsDiff",
    "SettingsSectionListResponse",
    "SettingsKeyListResponse",
    "SettingsValueResponse",
    "SettingsOperationResult",
    "SettingsBulkUpdateRequest",
    "SettingsBulkUpdateResponse",
    "SettingsSearchRequest",
    "SettingsSearchResult",
    "SettingsSearchResponse",
    "SettingsPermissionCheck",
]
