"""
Вспомогательные функции модуля Keywords

Содержит утилиты для работы с ключевыми словами
"""

import re
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .constants import (
    MAX_KEYWORD_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_CATEGORY_LENGTH,
    MIN_PRIORITY,
    MAX_PRIORITY,
    DEFAULT_PRIORITY,
    REGEX_WORD_VALIDATION,
    REGEX_SEARCH_QUERY,
    ALLOWED_EXPORT_FORMATS,
    MAX_KEYWORDS_PER_REQUEST,
)


def validate_keyword_word(word: str) -> Tuple[bool, str]:
    """
    Валидировать ключевое слово

    Args:
        word: Ключевое слово для валидации

    Returns:
        Tuple[bool, str]: (валидно ли, сообщение об ошибке)
    """
    if not word or not word.strip():
        return False, "Ключевое слово не может быть пустым"

    word = word.strip()
    if len(word) > MAX_KEYWORD_LENGTH:
        return (
            False,
            f"Ключевое слово слишком длинное (макс {MAX_KEYWORD_LENGTH} символов)",
        )

    # Проверка на допустимые символы
    if not re.match(REGEX_WORD_VALIDATION, word):
        return False, "Ключевое слово содержит недопустимые символы"

    return True, ""


def validate_description(description: str) -> Tuple[bool, str]:
    """
    Валидировать описание ключевого слова

    Args:
        description: Описание для валидации

    Returns:
        Tuple[bool, str]: (валидно ли, сообщение об ошибке)
    """
    if description and len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            False,
            f"Описание слишком длинное (макс {MAX_DESCRIPTION_LENGTH} символов)",
        )

    return True, ""


def validate_category_name(category_name: str) -> Tuple[bool, str]:
    """
    Валидировать название категории

    Args:
        category_name: Название категории для валидации

    Returns:
        Tuple[bool, str]: (валидно ли, сообщение об ошибке)
    """
    if category_name and len(category_name) > MAX_CATEGORY_LENGTH:
        return (
            False,
            f"Название категории слишком длинное (макс {MAX_CATEGORY_LENGTH} символов)",
        )

    if category_name and not category_name.strip():
        return False, "Название категории не может быть пустым"

    return True, ""


def validate_priority(priority: int) -> Tuple[bool, str]:
    """
    Валидировать приоритет

    Args:
        priority: Приоритет для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not isinstance(priority, int):
        return False, "Приоритет должен быть целым числом"

    if not (MIN_PRIORITY <= priority <= MAX_PRIORITY):
        return (
            False,
            f"Приоритет должен быть от {MIN_PRIORITY} до {MAX_PRIORITY}",
        )

    return True, ""


def validate_bulk_keywords(
    keywords_data: List[Dict[str, Any]]
) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Валидировать список ключевых слов для массовой загрузки

    Args:
        keywords_data: Список данных ключевых слов

    Returns:
        Tuple[bool, str, List[Dict[str, Any]]]: (валиден ли, сообщение об ошибке, валидные данные)
    """
    if not keywords_data:
        return False, "Список ключевых слов не может быть пустым", []

    if len(keywords_data) > MAX_KEYWORDS_PER_REQUEST:
        return (
            False,
            f"Слишком много ключевых слов (макс {MAX_KEYWORDS_PER_REQUEST})",
            [],
        )

    valid_keywords = []
    errors = []

    for i, keyword_data in enumerate(keywords_data):
        try:
            # Валидация ключевого слова
            word = keyword_data.get("word", "").strip()
            if not word:
                errors.append(f"Строка {i}: отсутствует ключевое слово")
                continue

            is_valid, error = validate_keyword_word(word)
            if not is_valid:
                errors.append(f"Строка {i}: {error}")
                continue

            # Валидация описания
            description = keyword_data.get("description", "")
            is_valid, error = validate_description(description)
            if not is_valid:
                errors.append(f"Строка {i}: {error}")
                continue

            # Валидация категории
            category_name = keyword_data.get("category_name", "")
            if category_name:
                is_valid, error = validate_category_name(category_name)
                if not is_valid:
                    errors.append(f"Строка {i}: {error}")
                    continue

            # Валидация приоритета
            priority = keyword_data.get("priority", DEFAULT_PRIORITY)
            is_valid, error = validate_priority(priority)
            if not is_valid:
                errors.append(f"Строка {i}: {error}")
                continue

            # Добавление валидных данных
            valid_data = {
                "word": word,
                "description": description,
                "category_name": category_name,
                "category_description": keyword_data.get(
                    "category_description", ""
                ),
                "priority": priority,
            }
            valid_keywords.append(valid_data)

        except Exception as e:
            errors.append(f"Строка {i}: неожиданная ошибка - {str(e)}")

    if errors:
        error_message = f"Найдено {len(errors)} ошибок: " + "; ".join(
            errors[:5]
        )
        if len(errors) > 5:
            error_message += f" и ещё {len(errors) - 5} ошибок"
        return False, error_message, valid_keywords

    return True, "", valid_keywords


def validate_search_query(query: str) -> Tuple[bool, str]:
    """
    Валидировать поисковый запрос

    Args:
        query: Поисковый запрос

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not query or not query.strip():
        return False, "Поисковый запрос не может быть пустым"

    query = query.strip()
    if len(query) > 255:
        return False, "Поисковый запрос слишком длинный"

    # Проверка на допустимые символы
    if not re.match(REGEX_SEARCH_QUERY, query):
        return False, "Поисковый запрос содержит недопустимые символы"

    return True, ""


def validate_export_format(format_type: str) -> Tuple[bool, str]:
    """
    Валидировать формат экспорта

    Args:
        format_type: Формат экспорта

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if format_type not in ALLOWED_EXPORT_FORMATS:
        return (
            False,
            f"Недопустимый формат экспорта. Допустимые: {', '.join(ALLOWED_EXPORT_FORMATS)}",
        )

    return True, ""


def generate_cache_key(operation: str, data: Any, **params) -> str:
    """
    Сгенерировать ключ кеша для операции

    Args:
        operation: Тип операции
        data: Данные для хеширования
        **params: Дополнительные параметры

    Returns:
        str: Ключ кеша
    """
    # Создаем строку для хеширования
    if isinstance(data, dict):
        data_str = json.dumps(data, sort_keys=True, default=str)
    elif isinstance(data, list):
        data_str = json.dumps(data, sort_keys=True, default=str)
    else:
        data_str = str(data)

    cache_string = f"keywords:{operation}:{data_str}"

    if params:
        sorted_params = sorted(params.items())
        cache_string += f":{sorted_params}"

    # Создаем хеш
    return hashlib.md5(cache_string.encode()).hexdigest()[:16]


def sanitize_keyword_word(word: str) -> str:
    """
    Очистить ключевое слово от потенциально опасных символов

    Args:
        word: Исходное ключевое слово

    Returns:
        str: Очищенное ключевое слово
    """
    if not word:
        return ""

    # Удаляем лишние пробелы
    word = word.strip()

    # Удаляем потенциально опасные символы
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        word = word.replace(char, "")

    return word


def sanitize_description(description: str) -> str:
    """
    Очистить описание от потенциально опасных символов

    Args:
        description: Исходное описание

    Returns:
        str: Очищенное описание
    """
    if not description:
        return ""

    # Удаляем лишние пробелы
    description = description.strip()

    # Удаляем потенциально опасные символы
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        description = description.replace(char, "")

    return description


def format_keyword_for_display(keyword: Dict[str, Any]) -> Dict[str, Any]:
    """
    Форматировать ключевое слово для отображения

    Args:
        keyword: Данные ключевого слова

    Returns:
        Dict[str, Any]: Форматированные данные
    """
    formatted = keyword.copy()

    # Форматирование дат
    if "created_at" in formatted and formatted["created_at"]:
        if isinstance(formatted["created_at"], datetime):
            formatted["created_at"] = formatted["created_at"].isoformat()

    if "updated_at" in formatted and formatted["updated_at"]:
        if isinstance(formatted["updated_at"], datetime):
            formatted["updated_at"] = formatted["updated_at"].isoformat()

    # Форматирование категории
    if "category" in formatted and formatted["category"]:
        category = formatted["category"]
        if isinstance(category, dict):
            formatted["category_name"] = category.get("name", "")
            formatted["category_description"] = category.get("description", "")
        else:
            formatted["category_name"] = str(category)
            formatted["category_description"] = ""

    # Форматирование статуса
    if "status" in formatted and formatted["status"]:
        status = formatted["status"]
        if isinstance(status, dict):
            formatted["is_active"] = status.get("is_active", True)
            formatted["is_archived"] = status.get("is_archived", False)
        else:
            formatted["is_active"] = bool(status)
            formatted["is_archived"] = False

    return formatted


def calculate_keywords_stats(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Вычислить статистику ключевых слов

    Args:
        keywords: Список ключевых слов

    Returns:
        Dict[str, Any]: Статистика
    """
    if not keywords:
        return {
            "total": 0,
            "active": 0,
            "archived": 0,
            "avg_priority": 0,
            "avg_matches": 0,
        }

    total = len(keywords)
    active = sum(
        1 for k in keywords if k.get("status", {}).get("is_active", True)
    )
    archived = sum(
        1 for k in keywords if k.get("status", {}).get("is_archived", False)
    )

    priorities = [k.get("priority", DEFAULT_PRIORITY) for k in keywords]
    avg_priority = (
        sum(priorities) / len(priorities) if priorities else DEFAULT_PRIORITY
    )

    matches = [k.get("match_count", 0) for k in keywords]
    avg_matches = sum(matches) / len(matches) if matches else 0

    return {
        "total": total,
        "active": active,
        "archived": archived,
        "avg_priority": round(avg_priority, 2),
        "avg_matches": round(avg_matches, 2),
    }


def group_keywords_by_category(
    keywords: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Группировать ключевые слова по категориям

    Args:
        keywords: Список ключевых слов

    Returns:
        Dict[str, List[Dict[str, Any]]]: Группированные ключевые слова
    """
    grouped = {}

    for keyword in keywords:
        category = keyword.get("category", {})
        if isinstance(category, dict):
            category_name = category.get("name", "без категории")
        else:
            category_name = str(category) if category else "без категории"

        if category_name not in grouped:
            grouped[category_name] = []

        grouped[category_name].append(keyword)

    return grouped


def sort_keywords(
    keywords: List[Dict[str, Any]],
    sort_by: str = "created_at",
    order: str = "desc",
) -> List[Dict[str, Any]]:
    """
    Сортировать ключевые слова

    Args:
        keywords: Список ключевых слов
        sort_by: Поле для сортировки
        order: Порядок сортировки (asc/desc)

    Returns:
        List[Dict[str, Any]]: Отсортированный список
    """
    reverse = order.lower() == "desc"

    if sort_by == "word":
        return sorted(
            keywords, key=lambda x: x.get("word", "").lower(), reverse=reverse
        )
    elif sort_by == "priority":
        return sorted(
            keywords,
            key=lambda x: x.get("priority", DEFAULT_PRIORITY),
            reverse=reverse,
        )
    elif sort_by == "match_count":
        return sorted(
            keywords, key=lambda x: x.get("match_count", 0), reverse=reverse
        )
    elif sort_by == "created_at":
        return sorted(
            keywords,
            key=lambda x: x.get("created_at", datetime.min),
            reverse=reverse,
        )
    elif sort_by == "updated_at":
        return sorted(
            keywords,
            key=lambda x: x.get("updated_at", datetime.min),
            reverse=reverse,
        )
    else:
        return keywords


def paginate_keywords(
    keywords: List[Dict[str, Any]], limit: int, offset: int
) -> Dict[str, Any]:
    """
    Пагинировать ключевые слова

    Args:
        keywords: Список ключевых слов
        limit: Количество на странице
        offset: Смещение

    Returns:
        Dict[str, Any]: Результаты пагинации
    """
    total = len(keywords)
    paginated = keywords[offset : offset + limit]

    return {
        "items": paginated,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total,
        "has_prev": offset > 0,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
        "current_page": (offset // limit) + 1 if limit > 0 else 1,
    }


def create_bulk_operation_summary(
    operation: str, results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Создать сводку массовой операции

    Args:
        operation: Тип операции
        results: Результаты операций

    Returns:
        Dict[str, Any]: Сводка
    """
    successful = sum(1 for r in results if r.get("success", False))
    failed = len(results) - successful

    errors = [
        r.get("error")
        for r in results
        if not r.get("success", False) and r.get("error")
    ]

    return {
        "operation": operation,
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "success_rate": successful / len(results) if results else 0,
        "errors": errors[:10],  # Ограничиваем количество ошибок
    }


def format_keywords_for_export(
    keywords: List[Dict[str, Any]], format_type: str = "json"
) -> str:
    """
    Форматировать ключевые слова для экспорта

    Args:
        keywords: Список ключевых слов
        format_type: Формат экспорта

    Returns:
        str: Форматированные данные
    """
    # Форматируем ключевые слова для экспорта
    export_data = []
    for keyword in keywords:
        export_item = {
            "id": keyword.get("id"),
            "word": keyword.get("word"),
            "category": (
                keyword.get("category", {}).get("name")
                if keyword.get("category")
                else ""
            ),
            "description": keyword.get("description", ""),
            "priority": keyword.get("priority"),
            "is_active": keyword.get("status", {}).get("is_active", True),
            "match_count": keyword.get("match_count", 0),
            "created_at": (
                keyword.get("created_at").isoformat()
                if keyword.get("created_at")
                else None
            ),
        }
        export_data.append(export_item)

    if format_type == "json":
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    elif format_type == "txt":
        lines = []
        for item in export_data:
            line = (
                f"{item['word']} [{item['category']}] - {item['description']}"
            )
            lines.append(line)
        return "\n".join(lines)
    else:
        return json.dumps(export_data, ensure_ascii=False)


def parse_import_data(import_data: str) -> List[Dict[str, Any]]:
    """
    Разобрать данные импорта

    Args:
        import_data: Данные для импорта

    Returns:
        List[Dict[str, Any]]: Разобранные данные
    """
    try:
        data = json.loads(import_data)
        if not isinstance(data, list):
            raise ValueError("Данные должны быть списком")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Неверный JSON формат: {str(e)}")


def merge_keyword_updates(
    existing: Dict[str, Any], updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Объединить обновления ключевого слова с существующими данными

    Args:
        existing: Существующие данные
        updates: Обновления

    Returns:
        Dict[str, Any]: Объединенные данные
    """
    merged = existing.copy()

    # Обновляем простые поля
    simple_fields = ["word", "description", "priority"]
    for field in simple_fields:
        if field in updates:
            merged[field] = updates[field]

    # Обновляем категорию
    if "category_name" in updates:
        merged["category"] = {
            "name": updates["category_name"],
            "description": updates.get("category_description", ""),
        }

    # Обновляем статус
    if "is_active" in updates:
        merged["status"] = {
            "is_active": updates["is_active"],
            "is_archived": merged.get("status", {}).get("is_archived", False),
        }

    # Обновляем время изменения
    merged["updated_at"] = datetime.utcnow()

    return merged


# Экспорт всех функций
__all__ = [
    "validate_keyword_word",
    "validate_description",
    "validate_category_name",
    "validate_priority",
    "validate_bulk_keywords",
    "validate_search_query",
    "validate_export_format",
    "generate_cache_key",
    "sanitize_keyword_word",
    "sanitize_description",
    "format_keyword_for_display",
    "calculate_keywords_stats",
    "group_keywords_by_category",
    "sort_keywords",
    "paginate_keywords",
    "create_bulk_operation_summary",
    "format_keywords_for_export",
    "parse_import_data",
    "merge_keyword_updates",
]
