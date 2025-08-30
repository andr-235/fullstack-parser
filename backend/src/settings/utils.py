"""
Вспомогательные функции модуля Settings

Содержит утилиты для работы с настройками системы
"""

import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


def validate_settings_section_name(section_name: str) -> Tuple[bool, str]:
    """
    Валидировать название секции настроек

    Args:
        section_name: Название секции

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not section_name or not section_name.strip():
        return False, "Название секции не может быть пустым"

    section_name = section_name.strip()

    # Проверяем длину
    if len(section_name) > 50:
        return False, "Название секции слишком длинное (макс 50 символов)"

    # Проверяем допустимые символы
    if not section_name.replace("_", "").replace("-", "").isalnum():
        return (
            False,
            "Название секции может содержать только буквы, цифры, _ и -",
        )

    # Проверяем, что не начинается с цифры
    if section_name[0].isdigit():
        return False, "Название секции не может начинаться с цифры"

    return True, ""


def validate_settings_key(key: str) -> Tuple[bool, str]:
    """
    Валидировать ключ настройки

    Args:
        key: Ключ настройки

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not key or not key.strip():
        return False, "Ключ настройки не может быть пустым"

    key = key.strip()

    # Проверяем длину
    if len(key) > 100:
        return False, "Ключ настройки слишком длинный (макс 100 символов)"

    # Проверяем допустимые символы
    if not key.replace("_", "").replace("-", "").isalnum():
        return False, "Ключ может содержать только буквы, цифры, _ и -"

    return True, ""


def sanitize_settings_value(value: Any) -> Any:
    """
    Очистить значение настройки от потенциально опасных данных

    Args:
        value: Значение настройки

    Returns:
        Any: Очищенное значение
    """
    if isinstance(value, str):
        # Удаляем лишние пробелы
        value = value.strip()

        # Ограничиваем длину строк
        if len(value) > 10000:
            value = value[:10000] + "..."

    elif isinstance(value, dict):
        # Рекурсивно очищаем вложенные словари
        sanitized_dict = {}
        for k, v in value.items():
            if isinstance(k, str) and len(k) <= 100:
                sanitized_dict[k] = sanitize_settings_value(v)
        value = sanitized_dict

    elif isinstance(value, list):
        # Ограничиваем размер списков
        if len(value) > 1000:
            value = value[:1000]
        value = [sanitize_settings_value(item) for item in value]

    return value


def calculate_settings_hash(settings: Dict[str, Any]) -> str:
    """
    Вычислить хеш настроек для обнаружения изменений

    Args:
        settings: Настройки

    Returns:
        str: Хеш настроек
    """
    # Сортируем ключи для консистентности
    sorted_settings = sort_dict_recursive(settings)

    # Преобразуем в JSON строку
    settings_json = json.dumps(sorted_settings, sort_keys=True, default=str)

    # Вычисляем хеш
    return hashlib.sha256(settings_json.encode()).hexdigest()


def sort_dict_recursive(data: Any) -> Any:
    """
    Рекурсивно отсортировать ключи в словаре

    Args:
        data: Данные для сортировки

    Returns:
        Any: Отсортированные данные
    """
    if isinstance(data, dict):
        return {k: sort_dict_recursive(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [sort_dict_recursive(item) for item in data]
    else:
        return data


def diff_settings(
    old_settings: Dict[str, Any], new_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Найти различия между двумя наборами настроек

    Args:
        old_settings: Старые настройки
        new_settings: Новые настройки

    Returns:
        Dict[str, Any]: Различия
    """
    diff: Dict[str, Dict[str, Any]] = {
        "added": {},
        "removed": {},
        "modified": {},
    }

    # Находим добавленные и измененные секции
    for section_name, new_section in new_settings.items():
        if section_name not in old_settings:
            diff["added"][section_name] = new_section
        elif old_settings[section_name] != new_section:
            diff["modified"][section_name] = {
                "old": old_settings[section_name],
                "new": new_section,
            }

    # Находим удаленные секции
    for section_name in old_settings:
        if section_name not in new_settings:
            diff["removed"][section_name] = old_settings[section_name]

    return diff


def flatten_settings(
    settings: Dict[str, Any], prefix: str = ""
) -> Dict[str, str]:
    """
    Преобразовать вложенные настройки в плоскую структуру

    Args:
        settings: Вложенные настройки
        prefix: Префикс для ключей

    Returns:
        Dict[str, str]: Плоские настройки
    """
    flat_settings = {}

    for key, value in settings.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            flat_settings.update(flatten_settings(value, full_key))
        elif isinstance(value, list):
            flat_settings[full_key] = json.dumps(value)
        else:
            flat_settings[full_key] = str(value)

    return flat_settings


def unflatten_settings(flat_settings: Dict[str, str]) -> Dict[str, Any]:
    """
    Преобразовать плоские настройки в вложенную структуру

    Args:
        flat_settings: Плоские настройки

    Returns:
        Dict[str, Any]: Вложенные настройки
    """
    nested_settings: Dict[str, Any] = {}

    for flat_key, value in flat_settings.items():
        keys = flat_key.split(".")
        current_dict = nested_settings

        # Проходим по всем ключам кроме последнего
        for key in keys[:-1]:
            if key not in current_dict:
                current_dict[key] = {}
            current_dict = current_dict[key]

        # Устанавливаем значение для последнего ключа
        last_key = keys[-1]

        # Пытаемся распарсить JSON для списков
        try:
            parsed_value = json.loads(value)
            current_dict[last_key] = parsed_value
        except (json.JSONDecodeError, TypeError):
            # Если не JSON, сохраняем как строку
            current_dict[last_key] = value

    return nested_settings


def filter_settings_by_permissions(
    settings: Dict[str, Any],
    user_permissions: list,
    critical_sections: list = None,
) -> Dict[str, Any]:
    """
    Фильтровать настройки по правам доступа пользователя

    Args:
        settings: Полные настройки
        user_permissions: Права пользователя
        critical_sections: Критические секции

    Returns:
        Dict[str, Any]: Отфильтрованные настройки
    """
    if not critical_sections:
        critical_sections = []

    filtered_settings = {}
    has_admin_access = "settings:admin" in user_permissions

    for section_name, section_data in settings.items():
        # Проверяем доступ к критическим секциям
        if section_name in critical_sections and not has_admin_access:
            continue

        # Проверяем права на чтение секции
        section_read_permission = f"settings:read:{section_name}"
        if (
            section_read_permission not in user_permissions
            and "settings:read" not in user_permissions
            and not has_admin_access
        ):
            continue

        filtered_settings[section_name] = section_data

    return filtered_settings


def create_settings_backup(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создать резервную копию настроек

    Args:
        settings: Настройки для бэкапа

    Returns:
        Dict[str, Any]: Резервная копия с метаданными
    """
    return {
        "settings": settings.copy(),
        "backup_created_at": datetime.utcnow().isoformat(),
        "version": "1.0",
        "hash": calculate_settings_hash(settings),
        "sections_count": len(settings),
    }


def validate_settings_backup(backup: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Валидировать резервную копию настроек

    Args:
        backup: Резервная копия для валидации

    Returns:
        Tuple[bool, str]: (валидна ли, сообщение об ошибке)
    """
    required_fields = [
        "settings",
        "backup_created_at",
        "version",
        "hash",
        "sections_count",
    ]

    for field in required_fields:
        if field not in backup:
            return False, f"Missing required field: {field}"

    if not isinstance(backup["settings"], dict):
        return False, "Settings field must be a dictionary"

    # Проверяем хеш
    calculated_hash = calculate_settings_hash(backup["settings"])
    if calculated_hash != backup["hash"]:
        return False, "Settings hash mismatch - backup may be corrupted"

    return True, ""


def get_settings_summary(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Получить сводку по настройкам

    Args:
        settings: Настройки

    Returns:
        Dict[str, Any]: Сводка
    """
    total_sections = len(settings)
    total_keys = sum(
        len(section)
        for section in settings.values()
        if isinstance(section, dict)
    )
    total_size = len(json.dumps(settings).encode("utf-8"))

    # Анализ типов значений
    value_types: Dict[str, int] = {}
    for section in settings.values():
        if isinstance(section, dict):
            for value in section.values():
                value_type = type(value).__name__
                value_types[value_type] = value_types.get(value_type, 0) + 1

    return {
        "total_sections": total_sections,
        "total_keys": total_keys,
        "total_size_bytes": total_size,
        "value_types": value_types,
        "sections_list": list(settings.keys()),
        "last_updated": datetime.utcnow().isoformat(),
    }


def merge_settings_with_defaults(
    current_settings: Dict[str, Any], default_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Объединить текущие настройки с настройками по умолчанию

    Args:
        current_settings: Текущие настройки
        default_settings: Настройки по умолчанию

    Returns:
        Dict[str, Any]: Объединенные настройки
    """
    merged = default_settings.copy()

    for section_name, current_section in current_settings.items():
        if section_name not in merged:
            merged[section_name] = {}

        if isinstance(current_section, dict) and isinstance(
            merged[section_name], dict
        ):
            merged[section_name].update(current_section)
        else:
            merged[section_name] = current_section

    return merged


# Экспорт всех функций
__all__ = [
    "validate_settings_section_name",
    "validate_settings_key",
    "sanitize_settings_value",
    "calculate_settings_hash",
    "sort_dict_recursive",
    "diff_settings",
    "flatten_settings",
    "unflatten_settings",
    "filter_settings_by_permissions",
    "create_settings_backup",
    "validate_settings_backup",
    "get_settings_summary",
    "merge_settings_with_defaults",
]
