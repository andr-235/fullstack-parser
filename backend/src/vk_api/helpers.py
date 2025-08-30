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
    Получить текущий timestamp в формате ISO

    Returns:
        str: Текущий timestamp
    """
    return datetime.now(timezone.utc).isoformat()


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

    if total_count is not None:
        response["total_count"] = total_count
    if requested_count is not None:
        response["requested_count"] = requested_count

    return response


def create_posts_response(
    posts: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
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
    )
    # Перемещаем данные в правильное поле для API
    result["posts"] = result.pop("data")
    return result


def create_comments_response(
    comments: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
    group_id: int,
    post_id: int,
    sort: str,
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
    result = create_standard_response(
        data=comments,
        total_count=total_count,
        requested_count=requested_count,
        offset=offset,
        has_more=has_more,
        group_id=group_id,
        post_id=post_id,
        sort=sort,
        success=True,
    )
    # Перемещаем данные в правильное поле для API
    result["comments"] = result.pop("data")
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
    result = create_standard_response(
        data=users,
        requested_ids=requested_ids,
        found_count=found_count,
        success=True,
    )
    # Перемещаем данные в правильное поле для API
    result["users"] = result.pop("data")
    return result


def create_groups_response(
    groups: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
    query: str,
    country: Optional[int] = None,
    city: Optional[int] = None,
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
    additional_fields = {"query": query}
    if country is not None:
        additional_fields["country"] = country
    if city is not None:
        additional_fields["city"] = city

    result = create_standard_response(
        data=groups,
        total_count=total_count,
        requested_count=requested_count,
        offset=offset,
        has_more=has_more,
        success=True,
        **additional_fields,
    )
    # Перемещаем данные в правильное поле для API
    result["groups"] = result.pop("data")
    return result


def create_post_response(post_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для одного поста

    Args:
        post_data: Данные поста

    Returns:
        Dict[str, Any]: Ответ с постом
    """
    result = create_standard_response(data=post_data, success=True)
    # Для поста данные должны быть в корне ответа
    result.update(result.pop("data"))
    return result


def create_group_response(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создать стандартизированный ответ для группы

    Args:
        group_data: Данные группы

    Returns:
        Dict[str, Any]: Ответ с группой
    """
    result = create_standard_response(data=group_data, success=True)
    # Для групп данные должны быть в корне ответа
    group_info = result.pop("data")
    result.update(group_info)
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
    response = {"status": status, "timestamp": get_current_timestamp()}

    if client_status:
        response["client"] = client_status
    if repository_status:
        response["repository"] = repository_status
    if error:
        response["error"] = error

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
        "client_stats": client_stats,
        "repository_stats": repository_stats,
        "cache_enabled": cache_enabled,
        "token_configured": token_configured,
        "timestamp": get_current_timestamp(),
    }


def create_limits_response(
    max_requests_per_second: int,
    max_posts_per_request: int,
    max_comments_per_request: int,
    max_groups_per_request: int,
    max_users_per_request: int,
    current_request_count: int,
    last_request_time: float,
    time_until_reset: float,
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
    return {
        "max_requests_per_second": max_requests_per_second,
        "max_posts_per_request": max_posts_per_request,
        "max_comments_per_request": max_comments_per_request,
        "max_groups_per_request": max_groups_per_request,
        "max_users_per_request": max_users_per_request,
        "current_request_count": current_request_count,
        "last_request_time": last_request_time,
        "time_until_reset": time_until_reset,
    }


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
        "valid": valid,
        "checked_at": get_current_timestamp(),
    }

    if user_id is not None:
        response["user_id"] = user_id
    if user_name is not None:
        response["user_name"] = user_name
    if error is not None:
        response["error"] = error

    return response


def create_group_members_response(
    members: list,
    total_count: int,
    requested_count: int,
    offset: int,
    has_more: bool,
    group_id: int,
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
    )
    # Перемещаем данные в правильное поле для API
    result["members"] = result.pop("data")
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
