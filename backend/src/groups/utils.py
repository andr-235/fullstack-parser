"""
Вспомогательные функции модуля Groups

Содержит утилиты для работы с группами VK
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .constants import (
    MAX_GROUP_NAME_LENGTH,
    MAX_SCREEN_NAME_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MIN_VK_ID_VALUE,
    MAX_VK_ID_VALUE,
)


def validate_group_data(group_data: Dict[str, Any]) -> List[str]:
    """
    Валидировать данные группы

    Args:
        group_data: Данные группы для валидации

    Returns:
        List[str]: Список ошибок валидации (пустой если валидация прошла)
    """
    errors = []

    # Проверка обязательных полей
    required_fields = ["vk_id", "screen_name", "name"]
    for field in required_fields:
        if field not in group_data or not group_data[field]:
            errors.append(f"Обязательное поле '{field}' не заполнено")

    # Валидация VK ID
    if "vk_id" in group_data:
        try:
            vk_id = int(group_data["vk_id"])
            if not (MIN_VK_ID_VALUE <= vk_id <= MAX_VK_ID_VALUE):
                errors.append(
                    f"VK ID должен быть в диапазоне {MIN_VK_ID_VALUE}-{MAX_VK_ID_VALUE}"
                )
        except (ValueError, TypeError):
            errors.append("VK ID должен быть целым числом")

    # Валидация screen_name
    if "screen_name" in group_data:
        screen_name = str(group_data["screen_name"])
        if len(screen_name) > MAX_SCREEN_NAME_LENGTH:
            errors.append(
                f"Screen name слишком длинный (макс {MAX_SCREEN_NAME_LENGTH} символов)"
            )
        if not re.match(r"^[a-zA-Z0-9_.]+$", screen_name):
            errors.append(
                "Screen name может содержать только буквы, цифры, точки и подчеркивания"
            )

    # Валидация названия группы
    if "name" in group_data:
        name = str(group_data["name"])
        if len(name) > MAX_GROUP_NAME_LENGTH:
            errors.append(
                f"Название группы слишком длинное (макс {MAX_GROUP_NAME_LENGTH} символов)"
            )

    # Валидация описания
    if "description" in group_data and group_data["description"]:
        description = str(group_data["description"])
        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"Описание группы слишком длинное (макс {MAX_DESCRIPTION_LENGTH} символов)"
            )

    # Валидация количества участников
    if "members_count" in group_data:
        try:
            members = int(group_data["members_count"])
            if members < 0:
                errors.append(
                    "Количество участников не может быть отрицательным"
                )
        except (ValueError, TypeError):
            errors.append("Количество участников должно быть целым числом")

    # Валидация max_posts_to_check
    if "max_posts_to_check" in group_data:
        try:
            max_posts = int(group_data["max_posts_to_check"])
            if max_posts < 1:
                errors.append(
                    "max_posts_to_check должен быть положительным числом"
                )
        except (ValueError, TypeError):
            errors.append("max_posts_to_check должен быть целым числом")

    return errors


def sanitize_group_name(name: str) -> str:
    """
    Очистить название группы от нежелательного контента

    Args:
        name: Исходное название группы

    Returns:
        str: Очищенное название
    """
    if not name:
        return ""

    # Удаление лишних пробелов
    name = re.sub(r"\s+", " ", name.strip())

    # Удаление потенциально опасных символов
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        name = name.replace(char, "")

    return name[:MAX_GROUP_NAME_LENGTH]


def format_group_for_display(group: Dict[str, Any]) -> Dict[str, Any]:
    """
    Форматировать группу для отображения в API

    Args:
        group: Данные группы из базы данных

    Returns:
        Dict[str, Any]: Форматированные данные группы
    """
    formatted = group.copy()

    # Форматирование даты
    if "last_parsed_at" in formatted and isinstance(
        formatted["last_parsed_at"], datetime
    ):
        formatted["last_parsed_at"] = formatted["last_parsed_at"].isoformat()

    if "created_at" in formatted and isinstance(
        formatted["created_at"], datetime
    ):
        formatted["created_at"] = formatted["created_at"].isoformat()

    if "updated_at" in formatted and isinstance(
        formatted["updated_at"], datetime
    ):
        formatted["updated_at"] = formatted["updated_at"].isoformat()

    # Форматирование числовых полей
    numeric_fields = [
        "members_count",
        "total_posts_parsed",
        "total_comments_found",
    ]
    for field in numeric_fields:
        if field in formatted:
            formatted[field] = int(formatted[field] or 0)

    return formatted


def generate_group_screen_name(name: str) -> str:
    """
    Сгенерировать screen_name на основе названия группы

    Args:
        name: Название группы

    Returns:
        str: Сгенерированный screen_name
    """
    if not name:
        return ""

    # Преобразование в нижний регистр
    screen_name = name.lower()

    # Замена русских букв на английские
    translit_map = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }

    for ru, en in translit_map.items():
        screen_name = screen_name.replace(ru, en)

    # Замена пробелов и специальных символов на подчеркивания
    screen_name = re.sub(r"[^a-zA-Z0-9]", "_", screen_name)

    # Удаление множественных подчеркиваний
    screen_name = re.sub(r"_+", "_", screen_name)

    # Удаление подчеркиваний в начале и конце
    screen_name = screen_name.strip("_")

    return screen_name[:MAX_SCREEN_NAME_LENGTH]


def calculate_group_activity_score(group: Dict[str, Any]) -> float:
    """
    Вычислить оценку активности группы

    Args:
        group: Данные группы

    Returns:
        float: Оценка активности (0-100)
    """
    score = 0.0

    # Базовая оценка за наличие данных
    if group.get("members_count", 0) > 0:
        score += 20

    if group.get("total_posts_parsed", 0) > 0:
        score += 30

    if group.get("total_comments_found", 0) > 0:
        score += 30

    # Бонус за недавнюю активность
    last_parsed = group.get("last_parsed_at")
    if last_parsed and isinstance(last_parsed, datetime):
        days_since_last_parse = (datetime.utcnow() - last_parsed).days
        if days_since_last_parse <= 1:
            score += 10
        elif days_since_last_parse <= 7:
            score += 5

    return min(score, 100.0)


def truncate_text(
    text: str, max_length: int = 100, suffix: str = "..."
) -> str:
    """
    Обрезать текст до указанной длины

    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста

    Returns:
        str: Обрезанный текст
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def generate_groups_summary(groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Сгенерировать сводку по списку групп

    Args:
        groups: Список групп

    Returns:
        Dict[str, Any]: Сводная статистика
    """
    if not groups:
        return {
            "total_groups": 0,
            "active_groups": 0,
            "total_members": 0,
            "avg_members_per_group": 0,
            "total_posts_parsed": 0,
            "total_comments_found": 0,
        }

    total_groups = len(groups)
    active_groups = sum(1 for g in groups if g.get("is_active", False))
    total_members = sum(g.get("members_count", 0) for g in groups)
    total_posts = sum(g.get("total_posts_parsed", 0) for g in groups)
    total_comments = sum(g.get("total_comments_found", 0) for g in groups)

    return {
        "total_groups": total_groups,
        "active_groups": active_groups,
        "total_members": total_members,
        "avg_members_per_group": round(total_members / total_groups, 2),
        "total_posts_parsed": total_posts,
        "total_comments_found": total_comments,
    }


def validate_vk_group_url(url: str) -> Optional[int]:
    """
    Извлечь VK ID группы из URL

    Args:
        url: URL группы VK

    Returns:
        Optional[int]: VK ID группы или None если невалидный URL
    """
    if not url:
        return None

    # Паттерны для различных форматов URL групп VK
    patterns = [
        r"vk\.com/(?:club|public|event)(\d+)",  # vk.com/club123, vk.com/public123, vk.com/event123
        r"vk\.com/([a-zA-Z0-9_.]+)",  # vk.com/screen_name
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            group_identifier = match.group(1)

            # Если это числовой ID (club123 -> 123)
            if group_identifier.isdigit():
                return int(group_identifier)
            else:
                # Для screen_name нужно будет дополнительное преобразование
                # Пока возвращаем None, так как для этого нужен API вызов
                return None

    return None


# Экспорт всех функций
__all__ = [
    "validate_group_data",
    "sanitize_group_name",
    "format_group_for_display",
    "generate_group_screen_name",
    "calculate_group_activity_score",
    "truncate_text",
    "generate_groups_summary",
    "validate_vk_group_url",
]
