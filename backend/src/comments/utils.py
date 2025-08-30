"""
Вспомогательные функции модуля Comments

Содержит утилиты для работы с комментариями
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .constants import (
    MAX_COMMENT_TEXT_LENGTH,
    MAX_AUTHOR_NAME_LENGTH,
    MAX_VK_ID_LENGTH,
    MIN_SEARCH_LENGTH,
)


def validate_comment_data(comment_data: Dict[str, Any]) -> List[str]:
    """
    Валидировать данные комментария

    Args:
        comment_data: Данные комментария для валидации

    Returns:
        List[str]: Список ошибок валидации (пустой если валидация прошла)
    """
    errors = []

    # Проверка обязательных полей
    required_fields = [
        "vk_comment_id",
        "vk_post_id",
        "vk_group_id",
        "author_id",
        "author_name",
        "text",
        "date",
    ]
    for field in required_fields:
        if field not in comment_data or not comment_data[field]:
            errors.append(f"Обязательное поле '{field}' не заполнено")

    # Валидация VK ID
    vk_fields = ["vk_comment_id", "vk_post_id", "vk_group_id"]
    for field in vk_fields:
        if field in comment_data:
            value = str(comment_data[field])
            if len(value) > MAX_VK_ID_LENGTH:
                errors.append(
                    f"Поле '{field}' слишком длинное (макс {MAX_VK_ID_LENGTH} символов)"
                )
            if not value.strip():
                errors.append(f"Поле '{field}' не может быть пустым")

    # Валидация имени автора
    if "author_name" in comment_data:
        author_name = str(comment_data["author_name"])
        if len(author_name) > MAX_AUTHOR_NAME_LENGTH:
            errors.append(
                f"Имя автора слишком длинное (макс {MAX_AUTHOR_NAME_LENGTH} символов)"
            )

    # Валидация текста комментария
    if "text" in comment_data:
        text = str(comment_data["text"])
        if len(text) > MAX_COMMENT_TEXT_LENGTH:
            errors.append(
                f"Текст комментария слишком длинный (макс {MAX_COMMENT_TEXT_LENGTH} символов)"
            )

    # Валидация даты
    if "date" in comment_data:
        try:
            if isinstance(comment_data["date"], str):
                datetime.fromisoformat(
                    comment_data["date"].replace("Z", "+00:00")
                )
            elif not isinstance(comment_data["date"], datetime):
                errors.append(
                    "Поле 'date' должно быть датой или строкой в формате ISO"
                )
        except ValueError:
            errors.append("Поле 'date' содержит некорректную дату")

    # Валидация количества лайков
    if "likes_count" in comment_data:
        try:
            likes = int(comment_data["likes_count"])
            if likes < 0:
                errors.append("Количество лайков не может быть отрицательным")
        except (ValueError, TypeError):
            errors.append("Поле 'likes_count' должно быть целым числом")

    return errors


def sanitize_comment_text(text: str) -> str:
    """
    Очистить текст комментария от нежелательного контента

    Args:
        text: Исходный текст комментария

    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""

    # Удаление лишних пробелов
    text = re.sub(r"\s+", " ", text.strip())

    # Удаление потенциально опасных символов (но оставляем базовые)
    # Можно расширить по необходимости
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",  # Скрипты
        r"javascript:",  # JavaScript ссылки
        r'on\w+="[^"]*"',  # HTML события
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text[:MAX_COMMENT_TEXT_LENGTH]


def format_comment_for_display(comment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Форматировать комментарий для отображения в API

    Args:
        comment: Данные комментария из базы данных

    Returns:
        Dict[str, Any]: Форматированные данные комментария
    """
    formatted = comment.copy()

    # Форматирование даты
    if "date" in formatted and isinstance(formatted["date"], datetime):
        formatted["date"] = formatted["date"].isoformat()

    if "created_at" in formatted and isinstance(
        formatted["created_at"], datetime
    ):
        formatted["created_at"] = formatted["created_at"].isoformat()

    if "updated_at" in formatted and isinstance(
        formatted["updated_at"], datetime
    ):
        formatted["updated_at"] = formatted["updated_at"].isoformat()

    if "processed_at" in formatted and isinstance(
        formatted["processed_at"], datetime
    ):
        formatted["processed_at"] = formatted["processed_at"].isoformat()

    # Форматирование числовых полей
    if "likes_count" in formatted:
        formatted["likes_count"] = int(formatted["likes_count"] or 0)

    return formatted


def extract_keywords_from_text(text: str) -> List[str]:
    """
    Извлечь ключевые слова из текста комментария

    Args:
        text: Текст комментария

    Returns:
        List[str]: Список потенциальных ключевых слов
    """
    if not text:
        return []

    # Простая экстракция: слова длиннее 3 символов
    words = re.findall(r"\b\w{3,}\b", text.lower())

    # Удаление стоп-слов (можно расширить)
    stop_words = {
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "an",
        "a",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "my",
        "your",
        "his",
        "its",
        "our",
        "their",
    }

    keywords = [word for word in words if word not in stop_words]

    # Удаление дубликатов с сохранением порядка
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword)

    return unique_keywords[:10]  # Ограничение количества


def calculate_comment_age(comment_date: datetime) -> str:
    """
    Вычислить возраст комментария в человеко-читаемом формате

    Args:
        comment_date: Дата комментария

    Returns:
        str: Возраст в формате "X дней назад", "X часов назад" и т.д.
    """
    now = datetime.utcnow()
    diff = now - comment_date

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} {'год' if years == 1 else 'года' if 2 <= years <= 4 else 'лет'} назад"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'} назад"
    elif diff.days > 0:
        return f"{diff.days} {'день' if diff.days == 1 else 'дня' if 2 <= diff.days <= 4 else 'дней'} назад"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} {'час' if hours == 1 else 'часа' if 2 <= hours <= 4 else 'часов'} назад"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} {'минуту' if minutes == 1 else 'минуты' if 2 <= minutes <= 4 else 'минут'} назад"
    else:
        return "только что"


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


def generate_comment_summary(comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Сгенерировать сводку по списку комментариев

    Args:
        comments: Список комментариев

    Returns:
        Dict[str, Any]: Сводная статистика
    """
    if not comments:
        return {
            "total_comments": 0,
            "total_likes": 0,
            "avg_likes": 0,
            "authors_count": 0,
            "date_range": None,
        }

    total_likes = sum(comment.get("likes_count", 0) for comment in comments)
    authors = set(
        comment.get("author_id")
        for comment in comments
        if comment.get("author_id")
    )

    dates = [
        comment.get("date") for comment in comments if comment.get("date")
    ]
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        date_range = {
            "from": (
                min_date.isoformat()
                if isinstance(min_date, datetime)
                else min_date
            ),
            "to": (
                max_date.isoformat()
                if isinstance(max_date, datetime)
                else max_date
            ),
        }
    else:
        date_range = None

    return {
        "total_comments": len(comments),
        "total_likes": total_likes,
        "avg_likes": round(total_likes / len(comments), 2),
        "authors_count": len(authors),
        "date_range": date_range,
    }


# Экспорт всех функций
__all__ = [
    "validate_comment_data",
    "sanitize_comment_text",
    "format_comment_for_display",
    "extract_keywords_from_text",
    "calculate_comment_age",
    "truncate_text",
    "generate_comment_summary",
]
