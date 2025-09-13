"""
Pydantic схемы для модуля авторов
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuthorStatus(str, Enum):
    """Статус автора"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class AuthorBase(BaseModel):
    """Базовая схема автора"""
    vk_id: int = Field(gt=0, description="VK ID автора")
    first_name: Optional[str] = Field(None, max_length=255, description="Имя")
    last_name: Optional[str] = Field(None, max_length=255, description="Фамилия")
    screen_name: Optional[str] = Field(None, max_length=100, description="Screen name")
    photo_url: Optional[str] = Field(None, max_length=500, description="URL фото")
    status: AuthorStatus = Field(AuthorStatus.ACTIVE, description="Статус")
    is_closed: bool = Field(False, description="Закрытый профиль")
    is_verified: bool = Field(False, description="Верифицированный")
    followers_count: int = Field(0, ge=0, description="Количество подписчиков")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
    metadata: Optional[dict] = Field(None, description="Метаданные")
    comments_count: int = Field(0, ge=0, description="Количество комментариев")


class AuthorCreate(AuthorBase):
    """Схема создания автора"""

    @field_validator('screen_name')
    @classmethod
    def validate_screen_name(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Screen name must contain only letters, numbers, _ and -')
        return v

    @field_validator('vk_id')
    @classmethod
    def validate_vk_id(cls, v):
        if v <= 0:
            raise ValueError('VK ID must be positive')
        return v


class AuthorUpdate(BaseModel):
    """Схема обновления автора"""
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    screen_name: Optional[str] = Field(None, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=500)
    status: Optional[AuthorStatus] = None
    is_closed: Optional[bool] = None
    is_verified: Optional[bool] = None
    followers_count: Optional[int] = Field(None, ge=0)
    last_activity: Optional[datetime] = None
    metadata: Optional[dict] = None
    comments_count: Optional[int] = Field(None, ge=0)


class AuthorResponse(AuthorBase):
    """Схема ответа с автором"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthorWithCommentsResponse(AuthorResponse):
    """Схема автора с комментариями"""
    comments: List[dict] = Field(default_factory=list, description="Комментарии автора")


class AuthorFilter(BaseModel):
    """Фильтр для списка авторов"""
    status: Optional[AuthorStatus] = None
    is_verified: Optional[bool] = None
    is_closed: Optional[bool] = None
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    order_by: str = Field("created_at", description="Поле для сортировки")
    order_direction: str = Field("desc", description="Направление сортировки")


class AuthorSearch(BaseModel):
    """Поиск авторов"""
    query: str = Field(..., min_length=1, max_length=100, description="Поисковый запрос")
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class AuthorListResponse(BaseModel):
    """Ответ со списком авторов"""
    items: List[AuthorResponse]
    total: int
    limit: int
    offset: int


class AuthorBulkAction(BaseModel):
    """Массовое действие"""
    action: str = Field(..., description="Действие: activate, suspend, delete")
    author_ids: List[int] = Field(..., min_items=1, description="ID авторов")
