"""
Pydantic схемы для модуля VK API

Определяет входные и выходные модели данных для API VK
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class VKAPIConfig(BaseModel):
    """Конфигурация VK API"""

    model_config = ConfigDict(from_attributes=True)

    version: str = Field(..., description="Версия VK API")
    base_url: str = Field(..., description="Базовый URL VK API")
    access_token: Optional[str] = Field(None, description="Токен доступа")
    timeout: float = Field(..., description="Таймаут запросов")
    max_requests_per_second: int = Field(
        ..., description="Максимум запросов в секунду"
    )
    cache_enabled: bool = Field(..., description="Включено ли кеширование")


class VKAPIHealthCheck(BaseModel):
    """Результат проверки здоровья VK API"""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Статус здоровья")
    timestamp: str = Field(..., description="Время проверки")
    client: Optional[Dict[str, Any]] = Field(
        None, description="Статус клиента"
    )
    repository: Optional[Dict[str, Any]] = Field(
        None, description="Статус репозитория"
    )
    cache_enabled: Optional[bool] = Field(
        None, description="Включено ли кеширование"
    )
    error: Optional[str] = Field(None, description="Сообщение об ошибке")


class VKAPIStats(BaseModel):
    """Статистика VK API"""

    model_config = ConfigDict(from_attributes=True)

    client_stats: Dict[str, Any] = Field(..., description="Статистика клиента")
    repository_stats: Dict[str, Any] = Field(
        ..., description="Статистика репозитория"
    )
    cache_enabled: bool = Field(..., description="Включено ли кеширование")
    token_configured: bool = Field(..., description="Настроен ли токен")
    timestamp: str = Field(..., description="Время получения статистики")


class VKAPILimits(BaseModel):
    """Лимиты VK API"""

    model_config = ConfigDict(from_attributes=True)

    max_requests_per_second: int = Field(
        ..., description="Максимум запросов в секунду"
    )
    max_posts_per_request: int = Field(
        ..., description="Максимум постов за запрос"
    )
    max_comments_per_request: int = Field(
        ..., description="Максимум комментариев за запрос"
    )
    max_groups_per_request: int = Field(
        ..., description="Максимум групп за запрос"
    )
    max_users_per_request: int = Field(
        ..., description="Максимум пользователей за запрос"
    )
    current_request_count: int = Field(
        ..., description="Текущий счетчик запросов"
    )
    last_request_time: float = Field(
        ..., description="Время последнего запроса"
    )
    time_until_reset: float = Field(
        ..., description="Время до сброса счетчика"
    )


class VKGroupInfo(BaseModel):
    """Информация о группе VK"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID группы")
    name: str = Field(..., description="Название группы")
    screen_name: str = Field(..., description="Короткое имя группы")
    description: str = Field(..., description="Описание группы")
    members_count: int = Field(..., description="Количество участников")
    photo_url: str = Field(..., description="URL фото группы")
    is_closed: bool = Field(..., description="Закрыта ли группа")
    type: str = Field(..., description="Тип группы")
    fetched_at: str = Field(..., description="Время получения данных")


class VKUserInfo(BaseModel):
    """Информация о пользователе VK"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID пользователя")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    photo_url: Optional[str] = Field(None, description="URL фото профиля")
    sex: Optional[int] = Field(None, description="Пол")
    city: Optional[Dict[str, Any]] = Field(None, description="Город")
    country: Optional[Dict[str, Any]] = Field(None, description="Страна")


class VKPostInfo(BaseModel):
    """Информация о посте VK"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID поста")
    owner_id: int = Field(..., description="ID владельца поста")
    from_id: int = Field(..., description="ID автора поста")
    created_by: Optional[int] = Field(None, description="ID создателя поста")
    date: int = Field(..., description="Дата публикации (timestamp)")
    text: str = Field(..., description="Текст поста")
    attachments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Вложения"
    )
    comments: Dict[str, Any] = Field(
        ..., description="Информация о комментариях"
    )
    likes: Dict[str, Any] = Field(..., description="Информация о лайках")
    reposts: Dict[str, Any] = Field(..., description="Информация о репостах")
    views: Dict[str, Any] = Field(..., description="Информация о просмотрах")
    is_pinned: bool = Field(..., description="Закреплен ли пост")
    fetched_at: str = Field(..., description="Время получения данных")


class VKCommentInfo(BaseModel):
    """Информация о комментарии VK"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID комментария")
    from_id: int = Field(..., description="ID автора комментария")
    date: int = Field(..., description="Дата комментария (timestamp)")
    text: str = Field(..., description="Текст комментария")
    likes: Dict[str, Any] = Field(..., description="Информация о лайках")
    attachments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Вложения"
    )
    thread: Optional[Dict[str, Any]] = Field(
        None, description="Информация о треде"
    )


class VKGroupPostsRequest(BaseModel):
    """Запрос на получение постов группы"""

    group_id: int = Field(..., description="ID группы VK", gt=0)
    count: int = Field(20, description="Количество постов", ge=1, le=100)
    offset: int = Field(0, description="Смещение", ge=0)


class VKGroupPostsResponse(BaseModel):
    """Ответ с постами группы"""

    posts: List[Dict[str, Any]] = Field(..., description="Список постов")
    total_count: int = Field(..., description="Общее количество постов")
    group_id: int = Field(..., description="ID группы")
    requested_count: int = Field(..., description="Запрошенное количество")
    offset: int = Field(..., description="Смещение")
    has_more: bool = Field(..., description="Есть ли еще посты")
    fetched_at: str = Field(..., description="Время получения данных")


class VKPostCommentsRequest(BaseModel):
    """Запрос на получение комментариев к посту"""

    group_id: int = Field(..., description="ID группы VK", gt=0)
    post_id: int = Field(..., description="ID поста", gt=0)
    count: int = Field(
        100, description="Количество комментариев", ge=1, le=100
    )
    offset: int = Field(0, description="Смещение", ge=0)
    sort: str = Field("asc", description="Сортировка", enum=["asc", "desc"])


class VKPostCommentsResponse(BaseModel):
    """Ответ с комментариями к посту"""

    comments: List[Dict[str, Any]] = Field(
        ..., description="Список комментариев"
    )
    total_count: int = Field(..., description="Общее количество комментариев")
    group_id: int = Field(..., description="ID группы")
    post_id: int = Field(..., description="ID поста")
    requested_count: int = Field(..., description="Запрошенное количество")
    offset: int = Field(..., description="Смещение")
    sort: str = Field(..., description="Сортировка")
    has_more: bool = Field(..., description="Есть ли еще комментарии")
    fetched_at: str = Field(..., description="Время получения данных")


class VKGroupInfoResponse(BaseModel):
    """Ответ с информацией о группе"""

    id: int = Field(..., description="ID группы")
    name: str = Field(..., description="Название группы")
    screen_name: str = Field(..., description="Короткое имя группы")
    description: str = Field(..., description="Описание группы")
    members_count: int = Field(..., description="Количество участников")
    photo_url: str = Field(..., description="URL фото группы")
    is_closed: bool = Field(..., description="Закрыта ли группа")
    type: str = Field(..., description="Тип группы")
    fetched_at: str = Field(..., description="Время получения данных")


class VKUsersInfoRequest(BaseModel):
    """Запрос на получение информации о пользователях"""

    user_ids: List[int] = Field(
        ...,
        description="Список ID пользователей",
        min_length=1,
        max_length=1000,
    )


class VKUsersInfoResponse(BaseModel):
    """Ответ с информацией о пользователях"""

    users: List[Dict[str, Any]] = Field(
        ..., description="Список пользователей"
    )
    requested_ids: List[int] = Field(..., description="Запрошенные ID")
    found_count: int = Field(..., description="Найденное количество")
    fetched_at: str = Field(..., description="Время получения данных")


class VKGroupsSearchRequest(BaseModel):
    """Запрос на поиск групп"""

    query: str = Field(
        ..., description="Поисковый запрос", min_length=1, max_length=255
    )
    count: int = Field(20, description="Количество результатов", ge=1, le=1000)
    offset: int = Field(0, description="Смещение", ge=0)
    country: Optional[int] = Field(None, description="ID страны")
    city: Optional[int] = Field(None, description="ID города")


class VKGroupsSearchResponse(BaseModel):
    """Ответ с результатами поиска групп"""

    groups: List[Dict[str, Any]] = Field(..., description="Список групп")
    total_count: int = Field(..., description="Общее количество результатов")
    query: str = Field(..., description="Поисковый запрос")
    requested_count: int = Field(..., description="Запрошенное количество")
    offset: int = Field(..., description="Смещение")
    has_more: bool = Field(..., description="Есть ли еще результаты")
    fetched_at: str = Field(..., description="Время получения данных")


class VKPostByIdRequest(BaseModel):
    """Запрос на получение поста по ID"""

    group_id: int = Field(..., description="ID группы VK", gt=0)
    post_id: int = Field(..., description="ID поста", gt=0)


class VKPostByIdResponse(BaseModel):
    """Ответ с постом по ID"""

    id: int = Field(..., description="ID поста")
    owner_id: int = Field(..., description="ID владельца поста")
    from_id: int = Field(..., description="ID автора поста")
    created_by: Optional[int] = Field(None, description="ID создателя поста")
    date: int = Field(..., description="Дата публикации (timestamp)")
    text: str = Field(..., description="Текст поста")
    attachments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Вложения"
    )
    comments: Dict[str, Any] = Field(
        ..., description="Информация о комментариях"
    )
    likes: Dict[str, Any] = Field(..., description="Информация о лайках")
    reposts: Dict[str, Any] = Field(..., description="Информация о репостах")
    views: Dict[str, Any] = Field(..., description="Информация о просмотрах")
    is_pinned: bool = Field(..., description="Закреплен ли пост")
    fetched_at: str = Field(..., description="Время получения данных")


class VKTokenValidationResponse(BaseModel):
    """Ответ валидации токена VK"""

    valid: bool = Field(..., description="Валиден ли токен")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    user_name: Optional[str] = Field(None, description="Имя пользователя")
    checked_at: str = Field(..., description="Время проверки")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")


class VKRequestLog(BaseModel):
    """Лог запроса к VK API"""

    model_config = ConfigDict(from_attributes=True)

    method: str = Field(..., description="Метод VK API")
    params_count: int = Field(..., description="Количество параметров")
    response_time: float = Field(..., description="Время ответа")
    success: bool = Field(..., description="Успешность запроса")
    error_message: Optional[str] = Field(
        None, description="Сообщение об ошибке"
    )
    timestamp: datetime = Field(..., description="Время запроса")


class VKErrorLog(BaseModel):
    """Лог ошибки VK API"""

    model_config = ConfigDict(from_attributes=True)

    method: str = Field(..., description="Метод VK API")
    error_code: int = Field(..., description="Код ошибки")
    error_message: str = Field(..., description="Сообщение об ошибке")
    params: Dict[str, Any] = Field(..., description="Параметры запроса")
    timestamp: datetime = Field(..., description="Время ошибки")


class VKAPILogsResponse(BaseModel):
    """Ответ с логами VK API"""

    request_logs: List[VKRequestLog] = Field(..., description="Логи запросов")
    error_logs: List[VKErrorLog] = Field(..., description="Логи ошибок")
    total_requests: int = Field(..., description="Общее количество запросов")
    total_errors: int = Field(..., description="Общее количество ошибок")


class VKBulkPostsRequest(BaseModel):
    """Запрос на массовое получение постов"""

    group_id: int = Field(..., description="ID группы VK", gt=0)
    post_ids: List[int] = Field(
        ..., description="Список ID постов", min_length=1, max_length=100
    )


class VKBulkPostsResponse(BaseModel):
    """Ответ с массовым получением постов"""

    posts: List[Dict[str, Any]] = Field(..., description="Список постов")
    total_requested: int = Field(..., description="Общее запрошено")
    total_found: int = Field(..., description="Общее найдено")
    group_id: int = Field(..., description="ID группы")
    fetched_at: str = Field(..., description="Время получения данных")


class VKGroupMembersRequest(BaseModel):
    """Запрос на получение участников группы"""

    group_id: int = Field(..., description="ID группы VK", gt=0)
    count: int = Field(
        1000, description="Количество участников", ge=1, le=1000
    )
    offset: int = Field(0, description="Смещение", ge=0)


class VKGroupMembersResponse(BaseModel):
    """Ответ с участниками группы"""

    members: List[int] = Field(..., description="Список ID участников")
    total_count: int = Field(..., description="Общее количество участников")
    group_id: int = Field(..., description="ID группы")
    requested_count: int = Field(..., description="Запрошенное количество")
    offset: int = Field(..., description="Смещение")
    has_more: bool = Field(..., description="Есть ли еще участники")
    fetched_at: str = Field(..., description="Время получения данных")


# Экспорт всех схем
__all__ = [
    "VKAPIConfig",
    "VKAPIHealthCheck",
    "VKAPIStats",
    "VKAPILimits",
    "VKGroupInfo",
    "VKUserInfo",
    "VKPostInfo",
    "VKCommentInfo",
    "VKGroupPostsRequest",
    "VKGroupPostsResponse",
    "VKPostCommentsRequest",
    "VKPostCommentsResponse",
    "VKGroupInfoResponse",
    "VKUsersInfoRequest",
    "VKUsersInfoResponse",
    "VKGroupsSearchRequest",
    "VKGroupsSearchResponse",
    "VKPostByIdRequest",
    "VKPostByIdResponse",
    "VKTokenValidationResponse",
    "VKRequestLog",
    "VKErrorLog",
    "VKAPILogsResponse",
    "VKBulkPostsRequest",
    "VKBulkPostsResponse",
    "VKGroupMembersRequest",
    "VKGroupMembersResponse",
]
