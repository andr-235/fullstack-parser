"""
Вспомогательные функции модуля VK API

Содержит утилиты для работы с VK API
"""

import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .config import (
    REGEX_VK_GROUP_ID,
    REGEX_VK_USER_ID,
    REGEX_VK_POST_ID,
    vk_api_config,
)


def validate_vk_group_id(group_id: str) -> Tuple[bool, str]:
    """
    Валидировать ID группы VK

    Args:
        group_id: ID группы для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not group_id or not group_id.strip():
        return False, "ID группы не может быть пустым"

    group_id = group_id.strip()

    # Проверяем формат
    if not re.match(REGEX_VK_GROUP_ID, group_id):
        return False, "Неверный формат ID группы"

    # Преобразуем в число для дополнительной проверки
    try:
        group_num = int(group_id)
        if group_num <= 0:
            return False, "ID группы должен быть положительным числом"
    except ValueError:
        return False, "ID группы должен быть числом"

    return True, ""


def validate_vk_user_id(user_id: str) -> Tuple[bool, str]:
    """
    Валидировать ID пользователя VK

    Args:
        user_id: ID пользователя для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not user_id or not user_id.strip():
        return False, "ID пользователя не может быть пустым"

    user_id = user_id.strip()

    # Проверяем формат
    if not re.match(REGEX_VK_USER_ID, user_id):
        return False, "Неверный формат ID пользователя"

    # Преобразуем в число для дополнительной проверки
    try:
        user_num = int(user_id)
        if user_num <= 0:
            return False, "ID пользователя должен быть положительным числом"
    except ValueError:
        return False, "ID пользователя должен быть числом"

    return True, ""


def validate_vk_post_id(post_id: str) -> Tuple[bool, str]:
    """
    Валидировать ID поста VK

    Args:
        post_id: ID поста для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not post_id or not post_id.strip():
        return False, "ID поста не может быть пустым"

    post_id = post_id.strip()

    # Проверяем формат
    if not re.match(REGEX_VK_POST_ID, post_id):
        return False, "Неверный формат ID поста"

    # Преобразуем в число для дополнительной проверки
    try:
        post_num = int(post_id)
        if post_num <= 0:
            return False, "ID поста должен быть положительным числом"
    except ValueError:
        return False, "ID поста должен быть числом"

    return True, ""


def convert_group_id_to_owner_id(group_id: int) -> int:
    """
    Преобразовать ID группы в owner_id для VK API

    Args:
        group_id: ID группы

    Returns:
        int: owner_id для VK API
    """
    return -abs(group_id)


def convert_owner_id_to_group_id(owner_id: int) -> int:
    """
    Преобразовать owner_id в ID группы

    Args:
        owner_id: owner_id из VK API

    Returns:
        int: ID группы
    """
    return abs(owner_id)


def generate_vk_api_url(method: str, params: Dict[str, Any] = None) -> str:
    """
    Сгенерировать URL для запроса к VK API

    Args:
        method: Метод VK API
        params: Параметры запроса

    Returns:
        str: Полный URL запроса
    """
    url = f"{vk_api_config.base_url}{method}"

    if params:
        # Преобразуем параметры в строку запроса
        query_params = []
        for key, value in params.items():
            if isinstance(value, list):
                # Для списков создаем отдельные параметры
                for item in value:
                    query_params.append(f"{key}[]={item}")
            else:
                query_params.append(f"{key}={value}")

        if query_params:
            url += "?" + "&".join(query_params)

    return url


def parse_vk_datetime(timestamp: int) -> datetime:
    """
    Преобразовать timestamp VK в объект datetime

    Args:
        timestamp: Timestamp из VK API

    Returns:
        datetime: Объект datetime
    """
    return datetime.fromtimestamp(timestamp)


def format_vk_datetime(dt: datetime) -> str:
    """
    Форматировать datetime для VK API

    Args:
        dt: Объект datetime

    Returns:
        str: Отформатированная дата
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def generate_request_hash(method: str, params: Dict[str, Any]) -> str:
    """
    Сгенерировать хеш запроса для кеширования

    Args:
        method: Метод VK API
        params: Параметры запроса

    Returns:
        str: Хеш запроса
    """
    # Создаем строку для хеширования
    hash_string = f"{method}:"

    # Сортируем параметры для консистентности
    sorted_params = sorted(params.items())
    for key, value in sorted_params:
        if isinstance(value, (list, tuple)):
            hash_string += f"{key}:{','.join(map(str, value))}:"
        else:
            hash_string += f"{key}:{value}:"

    # Создаем хеш
    return hashlib.md5(hash_string.encode()).hexdigest()[:16]


def extract_vk_attachments(
    attachments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Извлечь информацию о вложениях VK

    Args:
        attachments: Список вложений из VK API

    Returns:
        Dict[str, Any]: Информация о вложениях
    """
    result = {
        "photos": [],
        "videos": [],
        "audios": [],
        "docs": [],
        "links": [],
        "other": [],
    }

    for attachment in attachments:
        attachment_type = attachment.get("type")

        if attachment_type == "photo":
            photo = attachment.get("photo", {})
            result["photos"].append(
                {
                    "id": photo.get("id"),
                    "owner_id": photo.get("owner_id"),
                    "url": get_best_photo_url(photo),
                    "text": photo.get("text", ""),
                }
            )
        elif attachment_type == "video":
            video = attachment.get("video", {})
            result["videos"].append(
                {
                    "id": video.get("id"),
                    "owner_id": video.get("owner_id"),
                    "title": video.get("title", ""),
                    "duration": video.get("duration"),
                }
            )
        elif attachment_type == "audio":
            audio = attachment.get("audio", {})
            result["audios"].append(
                {
                    "id": audio.get("id"),
                    "owner_id": audio.get("owner_id"),
                    "artist": audio.get("artist", ""),
                    "title": audio.get("title", ""),
                }
            )
        elif attachment_type == "doc":
            doc = attachment.get("doc", {})
            result["docs"].append(
                {
                    "id": doc.get("id"),
                    "owner_id": doc.get("owner_id"),
                    "title": doc.get("title", ""),
                    "size": doc.get("size"),
                    "url": doc.get("url"),
                }
            )
        elif attachment_type == "link":
            link = attachment.get("link", {})
            result["links"].append(
                {
                    "url": link.get("url"),
                    "title": link.get("title", ""),
                    "description": link.get("description", ""),
                }
            )
        else:
            result["other"].append(attachment)

    return result


def get_best_photo_url(photo: Dict[str, Any]) -> Optional[str]:
    """
    Получить лучший URL фото из объекта VK

    Args:
        photo: Объект фото из VK API

    Returns:
        Optional[str]: URL лучшего качества фото
    """
    # Проверяем размеры в порядке убывания качества
    size_keys = [
        "photo_2560",
        "photo_1280",
        "photo_807",
        "photo_604",
        "photo_130",
        "photo_75",
    ]

    for size_key in size_keys:
        if size_key in photo:
            return photo[size_key]

    return None


def calculate_vk_api_stats(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Вычислить статистику постов VK

    Args:
        posts: Список постов из VK API

    Returns:
        Dict[str, Any]: Статистика постов
    """
    if not posts:
        return {
            "total_posts": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_reposts": 0,
            "total_views": 0,
            "avg_likes_per_post": 0,
            "avg_comments_per_post": 0,
            "avg_reposts_per_post": 0,
            "avg_views_per_post": 0,
        }

    total_posts = len(posts)
    total_likes = sum(post.get("likes", {}).get("count", 0) for post in posts)
    total_comments = sum(
        post.get("comments", {}).get("count", 0) for post in posts
    )
    total_reposts = sum(
        post.get("reposts", {}).get("count", 0) for post in posts
    )
    total_views = sum(post.get("views", {}).get("count", 0) for post in posts)

    return {
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_reposts": total_reposts,
        "total_views": total_views,
        "avg_likes_per_post": (
            total_likes / total_posts if total_posts > 0 else 0
        ),
        "avg_comments_per_post": (
            total_comments / total_posts if total_posts > 0 else 0
        ),
        "avg_reposts_per_post": (
            total_reposts / total_posts if total_posts > 0 else 0
        ),
        "avg_views_per_post": (
            total_views / total_posts if total_posts > 0 else 0
        ),
    }


def validate_vk_api_response(response: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Валидировать ответ VK API

    Args:
        response: Ответ от VK API

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not isinstance(response, dict):
        return False, "Ответ должен быть объектом"

    if "error" in response:
        error_info = response["error"]
        error_code = error_info.get("error_code", 0)
        error_msg = error_info.get("error_msg", "Unknown error")
        return False, f"VK API Error {error_code}: {error_msg}"

    if "response" not in response:
        return False, "Ответ не содержит поле 'response'"

    return True, ""


def sanitize_vk_text(text: str) -> str:
    """
    Очистить текст от потенциально опасных символов VK

    Args:
        text: Исходный текст

    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""

    # Удаляем лишние пробелы и переносы строк
    text = re.sub(r"\s+", " ", text.strip())

    # Удаляем потенциально опасные символы
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, "")

    return text


def format_vk_user_display_name(user: Dict[str, Any]) -> str:
    """
    Форматировать отображаемое имя пользователя VK

    Args:
        user: Объект пользователя из VK API

    Returns:
        str: Отформатированное имя
    """
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")

    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    else:
        return f"User {user.get('id', 'unknown')}"


def format_vk_group_display_name(group: Dict[str, Any]) -> str:
    """
    Форматировать отображаемое имя группы VK

    Args:
        group: Объект группы из VK API

    Returns:
        str: Отформатированное имя
    """
    name = group.get("name", "")
    screen_name = group.get("screen_name", "")

    if name:
        return name
    elif screen_name:
        return screen_name
    else:
        return f"Group {group.get('id', 'unknown')}"


def create_vk_api_request_summary(
    method: str, params: Dict[str, Any], response_time: float, success: bool
) -> Dict[str, Any]:
    """
    Создать сводку запроса к VK API

    Args:
        method: Метод VK API
        params: Параметры запроса
        response_time: Время ответа
        success: Успешность запроса

    Returns:
        Dict[str, Any]: Сводка запроса
    """
    return {
        "method": method,
        "params_count": len(params),
        "response_time": round(response_time, 3),
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Экспорт всех функций
__all__ = [
    "validate_vk_group_id",
    "validate_vk_user_id",
    "validate_vk_post_id",
    "convert_group_id_to_owner_id",
    "convert_owner_id_to_group_id",
    "generate_vk_api_url",
    "parse_vk_datetime",
    "format_vk_datetime",
    "generate_request_hash",
    "extract_vk_attachments",
    "get_best_photo_url",
    "calculate_vk_api_stats",
    "validate_vk_api_response",
    "sanitize_vk_text",
    "format_vk_user_display_name",
    "format_vk_group_display_name",
    "create_vk_api_request_summary",
]
