"""
Helper Functions for VK API Module

Этот модуль содержит вспомогательные функции для стандартизации ответов API,
работы с временными метками и создания унифицированных структур данных.

Основные функции:
- get_current_timestamp: Получение текущего timestamp в ISO формате
- create_*_response: Функции для создания стандартизированных ответов
- Стандартизация форматов ответов для различных типов данных

Архитектурные принципы:
- Single Responsibility: Каждая функция отвечает за один тип ответа
- DRY: Устранение дублирования кода создания ответов
- Consistency: Единый формат всех ответов API
- Type Safety: Явное указание типов для всех параметров

Примеры использования:

    # Создание ответа с постами
    response = create_posts_response(
        posts=post_list,
        total_count=100,
        requested_count=20,
        offset=0,
        has_more=True
    )

    # Создание ответа для проверки здоровья
    health_response = create_health_response(
        status="healthy",
        client_status=client_data,
        repository_status=repo_data
    )

Автор: AI Assistant
Версия: 1.0
Дата: 2024
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional


def get_current_timestamp() -> str:
    """
    Получить текущий timestamp в формате ISO UTC

    Returns:
        str: Текущий timestamp в UTC формате
    """
    return (
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    )


def create_standard_response(
    data: Any,
    total_count: Optional[int] = None,
    requested_count: Optional[int] = None,
    offset: int = 0,
    has_more: bool = False,
    **additional_fields,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ API

    Args:
        data: Основные данные ответа
        total_count: Общее количество элементов
        requested_count: Запрошенное количество
        offset: Смещение
        has_more: Есть ли еще элементы
        **additional_fields: Дополнительные поля

    Returns:
        Dict[str, Any]: Стандартизированный ответ
    """
    response = {
        "data": data,
        "fetched_at": get_current_timestamp(),
        "offset": offset,
        "has_more": has_more,
        **additional_fields,
    }

    # Всегда добавляем поля, даже если None
    response["total_count"] = total_count
    response["requested_count"] = requested_count

    return response


def create_posts_response(
    posts: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
    **additional_fields,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для постов

    Args:
        posts: Список постов
        total_count: Общее количество постов
        requested_count: Запрошенное количество
        offset: Смещение
        has_more: Есть ли еще посты

    Returns:
        Dict[str, Any]: Ответ с постами
    """
    result = create_standard_response(
        data=posts,
        total_count=total_count,
        requested_count=requested_count,
        offset=offset,
        has_more=has_more,
        success=True,
        **additional_fields,
    )
    # Перемещаем данные в правильное поле для API
    result["posts"] = result.pop("data")
    result["data_type"] = "posts"
    return result


def create_comments_response(
    comments: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
    group_id: Optional[int] = None,
    post_id: Optional[int] = None,
    sort: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для комментариев

    Args:
        comments: Список комментариев
        total_count: Общее количество комментариев
        requested_count: Запрошенное количество
        offset: Смещение
        has_more: Есть ли еще комментарии
        group_id: ID группы
        post_id: ID поста
        sort: Сортировка

    Returns:
        Dict[str, Any]: Ответ с комментариями
    """
    additional_fields = {}
    if group_id is not None:
        additional_fields["group_id"] = group_id
    if post_id is not None:
        additional_fields["post_id"] = post_id
    if sort is not None:
        additional_fields["sort"] = sort

    result = create_standard_response(
        data=comments,
        total_count=total_count,
        requested_count=requested_count,
        offset=offset,
        has_more=has_more,
        success=True,
        **additional_fields,
    )
    # Перемещаем данные в правильное поле для API
    result["comments"] = result.pop("data")
    result["data_type"] = "comments"
    return result


def create_users_response(
    users: list, requested_ids: list, found_count: int
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для пользователей

    Args:
        users: Список пользователей
        requested_ids: Запрошенные ID
        found_count: Найденное количество

    Returns:
        Dict[str, Any]: Ответ с пользователями
    """
    # Добавляем поле name для каждого пользователя
    users_with_names = []
    for user in users:
        user_copy = user.copy()
        first_name = user.get("first_name", "")
        last_name = user.get("last_name", "")
        if first_name and last_name:
            user_copy["name"] = f"{first_name} {last_name}"
        elif first_name:
            user_copy["name"] = first_name
        elif last_name:
            user_copy["name"] = last_name
        else:
            user_copy["name"] = ""
        users_with_names.append(user_copy)

    result = create_standard_response(
        data=users_with_names,
        requested_ids=requested_ids,
        found_count=found_count,
        success=True,
    )
    # Перемещаем данные в правильное поле для API
    result["users"] = result.pop("data")
    result["data_type"] = "users"
    return result


def create_groups_response(
    groups: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
    query: Optional[str] = None,
    country: Optional[int] = None,
    city: Optional[int] = None,
    **additional_fields,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для групп

    Args:
        groups: Список групп
        total_count: Общее количество групп
        requested_count: Запрошенное количество
        offset: Смещение
        has_more: Есть ли еще группы
        query: Поисковый запрос
        country: ID страны
        city: ID города

    Returns:
        Dict[str, Any]: Ответ с группами
    """
    extra_fields = {}
    if query is not None:
        extra_fields["query"] = query
    if country is not None:
        extra_fields["country"] = country
    if city is not None:
        extra_fields["city"] = city

    result = create_standard_response(
        data=groups,
        total_count=total_count,
        requested_count=requested_count,
        offset=offset,
        has_more=has_more,
        success=True,
        **extra_fields,
        **additional_fields,
    )
    # Перемещаем данные в правильное поле для API
    result["groups"] = result.pop("data")
    result["data_type"] = "groups"
    return result


def create_post_response(post_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для одного поста

    Args:
        post_data: Данные поста

    Returns:
        Dict[str, Any]: Ответ с постом
    """
    # Добавляем недостающие поля по умолчанию
    post_with_defaults = {"attachments": [], "is_pinned": False, **post_data}

    result = create_standard_response(data=post_with_defaults, success=True)
    # Для поста данные должны быть в поле post
    result["post"] = result.pop("data")
    result["data_type"] = "post"
    return result


def create_group_response(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для группы

    Args:
        group_data: Данные группы

    Returns:
        Dict[str, Any]: Ответ с группой
    """
    # Добавляем недостающие поля по умолчанию
    group_with_defaults = {
        "description": "",
        "members_count": 0,
        "photo_url": "",
        "is_closed": False,
        "type": "group",
        **group_data,
    }

    result = create_standard_response(data=group_with_defaults, success=True)
    # Для групп данные должны быть в поле group
    result["group"] = result.pop("data")
    result["data_type"] = "group"
    return result


def create_health_response(
    status: str,
    client_status: Optional[Dict[str, Any]] = None,
    repository_status: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для проверки здоровья

    Args:
        status: Статус здоровья
        client_status: Статус клиента
        repository_status: Статус репозитория
        error: Сообщение об ошибке

    Returns:
        Dict[str, Any]: Ответ со статусом здоровья
    """
    response = {
        "status": status,
        "timestamp": get_current_timestamp(),
        "success": True,
    }

    if client_status:
        response["client_status"] = client_status
    if repository_status:
        response["repository_status"] = repository_status
    if error:
        response["error"] = error

    response["data_type"] = "health"
    return response


def create_stats_response(
    client_stats: Dict[str, Any],
    repository_stats: Dict[str, Any],
    cache_enabled: bool,
    token_configured: bool,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для статистики

    Args:
        client_stats: Статистика клиента
        repository_stats: Статистика репозитория
        cache_enabled: Включено ли кеширование
        token_configured: Настроен ли токен

    Returns:
        Dict[str, Any]: Ответ со статистикой
    """
    return {
        "success": True,
        "client_stats": client_stats,
        "repository_stats": repository_stats,
        "cache_enabled": cache_enabled,
        "token_configured": token_configured,
        "timestamp": get_current_timestamp(),
        "data_type": "stats",
    }


def create_limits_response(
    max_requests_per_second: int,
    max_posts_per_request: int,
    max_comments_per_request: int = 100,
    max_groups_per_request: int = 1000,
    max_users_per_request: int = 1000,
    current_request_count: int = 0,
    last_request_time: float = 0.0,
    time_until_reset: float = 0.0,
    **additional_fields,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для лимитов

    Args:
        max_requests_per_second: Максимум запросов в секунду
        max_posts_per_request: Максимум постов за запрос
        max_comments_per_request: Максимум комментариев за запрос
        max_groups_per_request: Максимум групп за запрос
        max_users_per_request: Максимум пользователей за запрос
        current_request_count: Текущий счетчик запросов
        last_request_time: Время последнего запроса
        time_until_reset: Время до сброса счетчика

    Returns:
        Dict[str, Any]: Ответ с лимитами
    """
    result = {
        "success": True,
        "max_requests_per_second": max_requests_per_second,
        "max_posts_per_request": max_posts_per_request,
        "max_comments_per_request": max_comments_per_request,
        "max_groups_per_request": max_groups_per_request,
        "max_users_per_request": max_users_per_request,
        "current_request_count": current_request_count,
        "last_request_time": last_request_time,
        "time_until_reset": time_until_reset,
        "data_type": "limits",
    }
    result.update(additional_fields)
    return result


def create_token_validation_response(
    valid: bool,
    user_id: Optional[int] = None,
    user_name: Optional[str] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для валидации токена

    Args:
        valid: Валиден ли токен
        user_id: ID пользователя
        user_name: Имя пользователя
        error: Сообщение об ошибке

    Returns:
        Dict[str, Any]: Ответ с результатом валидации
    """
    response = {
        "success": True,
        "valid": valid,
        "checked_at": get_current_timestamp(),
    }

    if user_id is not None:
        response["user_id"] = user_id
    if user_name is not None:
        response["user_name"] = user_name
    if error is not None:
        response["error"] = error

    response["data_type"] = "token_validation"
    return response


def create_group_members_response(
    members: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
    group_id: int,
    **additional_fields,
) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для участников группы

    Args:
        members: Список участников группы
        total_count: Общее количество участников
        requested_count: Запрошенное количество участников
        offset: Смещение в списке
        has_more: Есть ли еще участники для загрузки
        group_id: ID группы

    Returns:
        Dict[str, Any]: Стандартизированный ответ
    """
    result = create_standard_response(
        data=members,
        total_count=total_count,
        requested_count=requested_count,
        offset=offset,
        has_more=has_more,
        group_id=group_id,
        success=True,
        **additional_fields,
    )
    # Перемещаем данные в правильное поле для API
    result["members"] = result.pop("data")
    result["data_type"] = "group_members"
    return result


# Экспорт
__all__ = [
    "get_current_timestamp",
    "create_standard_response",
    "create_posts_response",
    "create_comments_response",
    "create_users_response",
    "create_groups_response",
    "create_post_response",
    "create_group_response",
    "create_health_response",
    "create_stats_response",
    "create_limits_response",
    "create_token_validation_response",
    "create_group_members_response",
]
