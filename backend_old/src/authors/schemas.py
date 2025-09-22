"""
Pydantic схемы для модуля авторов
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, ValidationError

# Константы для валидации
MAX_NAME_LENGTH = 255
MAX_SCREEN_NAME_LENGTH = 100
MAX_PHOTO_URL_LENGTH = 500
DEFAULT_LIMIT = 50
MAX_LIMIT = 1000
MIN_LIMIT = 1
DEFAULT_OFFSET = 0
MIN_OFFSET = 0
MIN_QUERY_LENGTH = 1
MAX_QUERY_LENGTH = 100
MIN_AUTHOR_IDS = 1


class AuthorStatus(str, Enum):
    """Статус автора в системе.

    Определяет возможные состояния автора в системе мониторинга.

    Attributes:
        ACTIVE: Активный автор, доступен для мониторинга.
        INACTIVE: Неактивный автор, временно не отслеживается.
        SUSPENDED: Приостановленный автор, заблокирован.
        DELETED: Удаленный автор, недоступен.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class AuthorBase(BaseModel):
    """Базовая Pydantic схема автора VK.

    Определяет общие поля и валидацию для всех схем автора.
    Используется как базовый класс для создания, обновления и ответов.

    Attributes:
        vk_id (int): Уникальный идентификатор автора в VK (должен быть > 0).
        first_name (Optional[str]): Имя автора (макс. 255 символов).
        last_name (Optional[str]): Фамилия автора (макс. 255 символов).
        screen_name (Optional[str]): Короткое имя автора (макс. 100 символов).
        photo_url (Optional[HttpUrl]): URL фотографии профиля.
        status (AuthorStatus): Статус автора в системе (по умолчанию ACTIVE).
        is_closed (bool): Флаг закрытого профиля VK (по умолчанию False).
        is_verified (bool): Флаг верификации автора VK (по умолчанию False).
        followers_count (int): Количество подписчиков (>= 0).
        last_activity (Optional[datetime]): Время последней активности.
        metadata (Optional[Dict[str, Any]]): Дополнительные метаданные в формате JSON.
        comments_count (int): Количество комментариев автора (>= 0).
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    vk_id: int = Field(gt=0, description="VK ID автора")
    first_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH, description="Имя")
    last_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH, description="Фамилия")
    screen_name: Optional[str] = Field(None, max_length=MAX_SCREEN_NAME_LENGTH, description="Screen name")
    photo_url: Optional[HttpUrl] = Field(None, description="URL фото")
    status: AuthorStatus = Field(AuthorStatus.ACTIVE, description="Статус")
    is_closed: bool = Field(False, description="Закрытый профиль")
    is_verified: bool = Field(False, description="Верифицированный")
    followers_count: int = Field(0, ge=0, description="Количество подписчиков")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")
    comments_count: int = Field(0, ge=0, description="Количество комментариев")

    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Валидирует метаданные автора.

        Проверяет, что все значения в метаданных имеют допустимые типы данных
        (str, int, float, bool, list, dict, None) и рекурсивно валидирует вложенные структуры.

        Args:
            v: Словарь с метаданными автора для валидации.

        Returns:
            Optional[Dict[str, Any]]: Валидированный словарь метаданных или None,
            если метаданные не предоставлены.

        Raises:
            ValueError: Если метаданные содержат недопустимые типы данных или
            ключи не являются строками.

        Examples:
            >>> AuthorBase.validate_metadata({"key": "value", "count": 42})
            {'key': 'value', 'count': 42}

            >>> AuthorBase.validate_metadata({"nested": {"inner": [1, 2, 3]}})
            {'nested': {'inner': [1, 2, 3]}}
        """
        if v is None:
            return v

        allowed_types = (str, int, float, bool, list, dict, type(None))

        def check_value(value: Any) -> None:
            if not isinstance(value, allowed_types):
                raise ValueError(f"Недопустимый тип данных в метаданных: {type(value)}")
            if isinstance(value, list):
                for item in value:
                    check_value(item)
            elif isinstance(value, dict):
                for key, val in value.items():
                    if not isinstance(key, str):
                        raise ValueError("Ключи метаданных должны быть строками")
                    check_value(val)

        try:
            check_value(v)
        except ValueError as e:
            raise ValueError(f"Ошибка валидации метаданных: {e}") from e

        return v


class AuthorCreate(AuthorBase):
    """
    Схема для создания нового автора.

    Наследует все поля от AuthorBase и добавляет специфическую валидацию.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @field_validator('screen_name')
    @classmethod
    def validate_screen_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Валидирует screen name автора.

        Проверяет, что screen name содержит только допустимые символы:
        буквы, цифры, подчеркивания и дефисы.

        Args:
            v: Screen name автора для валидации.

        Returns:
            Optional[str]: Валидированный screen name или None,
            если screen name не предоставлен.

        Raises:
            ValueError: Если screen name содержит недопустимые символы
            (не буквы, цифры, _ или -).

        Examples:
            >>> AuthorCreate.validate_screen_name("valid_name123")
            'valid_name123'

            >>> AuthorCreate.validate_screen_name("invalid@name")
            Traceback (most recent call last):
                ValueError: Screen name must contain only letters, numbers, _ and -
        """
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Screen name must contain only letters, numbers, _ and -')
        return v


class AuthorUpdate(BaseModel):
    """
    Схема для обновления данных автора.

    Все поля опциональны, что позволяет частичное обновление.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    first_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH)
    last_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH)
    screen_name: Optional[str] = Field(None, max_length=MAX_SCREEN_NAME_LENGTH)
    photo_url: Optional[HttpUrl] = Field(None)
    status: Optional[AuthorStatus] = None
    is_closed: Optional[bool] = None
    is_verified: Optional[bool] = None
    followers_count: Optional[int] = Field(None, ge=0)
    last_activity: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    comments_count: Optional[int] = Field(None, ge=0)


class AuthorResponse(AuthorBase):
    """
    Схема ответа с данными автора.

    Включает все поля автора плюс системные поля.
    """
    id: int
    created_at: datetime
    updated_at: datetime


class AuthorWithCommentsResponse(AuthorResponse):
    """
    Схема автора с комментариями.

    Расширяет AuthorResponse списком комментариев.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    comments: List[Dict[str, Any]] = Field(default_factory=list, description="Комментарии автора")


class AuthorFilter(BaseModel):
    """
    Фильтр для запросов списка авторов.

    Позволяет фильтровать и сортировать результаты.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    status: Optional[AuthorStatus] = None
    is_verified: Optional[bool] = None
    is_closed: Optional[bool] = None
    limit: int = Field(DEFAULT_LIMIT, ge=MIN_LIMIT, le=MAX_LIMIT)
    offset: int = Field(DEFAULT_OFFSET, ge=MIN_OFFSET)
    order_by: str = Field("created_at", description="Поле для сортировки")
    order_direction: str = Field("desc", description="Направление сортировки")


class AuthorSearch(BaseModel):
    """
    Схема для поиска авторов.

    Поддерживает текстовый поиск с пагинацией.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    query: str = Field(..., min_length=MIN_QUERY_LENGTH, max_length=MAX_QUERY_LENGTH, description="Поисковый запрос")
    limit: int = Field(DEFAULT_LIMIT, ge=MIN_LIMIT, le=MAX_LIMIT)
    offset: int = Field(DEFAULT_OFFSET, ge=MIN_OFFSET)


class AuthorListResponse(BaseModel):
    """
    Ответ со списком авторов.

    Включает результаты поиска/фильтрации с метаданными пагинации.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    items: List[AuthorResponse]
    total: int
    limit: int
    offset: int


class AuthorBulkAction(BaseModel):
    """
    Схема для массовых операций над авторами.

    Поддерживает групповые действия: активация, приостановка, удаление.
    """
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    action: str = Field(..., description="Действие: activate, suspend, delete")
    author_ids: List[int] = Field(..., min_items=MIN_AUTHOR_IDS, description="ID авторов")
