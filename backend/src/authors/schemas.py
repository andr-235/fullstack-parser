"""
Pydantic схемы для модуля авторов VK

Современные схемы с валидацией и типизацией согласно best practices 2025
"""

from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import PositiveInt


class AuthorBase(BaseModel):
    """Базовая схема автора."""
    
    vk_id: PositiveInt = Field(
        description="VK ID автора",
        examples=[123456789]
    )
    first_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Имя автора",
        examples=["Иван"]
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Фамилия автора",
        examples=["Иванов"]
    )
    screen_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Screen name автора",
        examples=["ivan_ivanov"]
    )
    photo_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL фото автора",
        examples=["https://vk.com/images/camera_200.png"]
    )

    @field_validator('photo_url')
    @classmethod
    def validate_photo_url(cls, v: Optional[str]) -> Optional[str]:
        """Валидация URL фото."""
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('Photo URL must start with http:// or https://')
        return v

    model_config = ConfigDict(
        str_max_length=500,
        validate_assignment=True,
        from_attributes=True
    )


class AuthorCreate(AuthorBase):
    """Схема для создания автора."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "vk_id": 123456789,
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "screen_name": "ivan_ivanov",
                    "photo_url": "https://vk.com/images/camera_200.png"
                }
            ]
        }
    )


class AuthorUpdate(BaseModel):
    """Схема для обновления автора."""
    
    first_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Имя автора"
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Фамилия автора"
    )
    screen_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Screen name автора"
    )
    photo_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL фото автора"
    )

    @field_validator('photo_url')
    @classmethod
    def validate_photo_url(cls, v: Optional[str]) -> Optional[str]:
        """Валидация URL фото."""
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('Photo URL must start with http:// or https://')
        return v

    model_config = ConfigDict(
        str_max_length=500,
        validate_assignment=True,
        from_attributes=True
    )


class AuthorResponse(AuthorBase):
    """Схема ответа с данными автора."""
    
    id: int = Field(description="Внутренний ID автора")
    created_at: datetime = Field(description="Дата создания записи")
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Дата последнего обновления"
    )
    comments_count: int = Field(
        default=0,
        description="Количество комментариев автора"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "vk_id": 123456789,
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "screen_name": "ivan_ivanov",
                    "photo_url": "https://vk.com/images/camera_200.png",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z",
                    "comments_count": 15
                }
            ]
        }
    )


class AuthorListResponse(BaseModel):
    """Схема ответа со списком авторов."""
    
    authors: list[AuthorResponse] = Field(description="Список авторов")
    total: int = Field(description="Общее количество авторов")
    limit: int = Field(description="Лимит записей")
    offset: int = Field(description="Смещение")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "authors": [
                        {
                            "id": 1,
                            "vk_id": 123456789,
                            "first_name": "Иван",
                            "last_name": "Иванов",
                            "screen_name": "ivan_ivanov",
                            "photo_url": "https://vk.com/images/camera_200.png",
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-01T12:00:00Z",
                            "comments_count": 15
                        }
                    ],
                    "total": 1,
                    "limit": 100,
                    "offset": 0
                }
            ]
        }
    )


class AuthorUpsertRequest(AuthorBase):
    """Схема для upsert операции автора."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "vk_id": 123456789,
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "screen_name": "ivan_ivanov",
                    "photo_url": "https://vk.com/images/camera_200.png"
                }
            ]
        }
    )


class AuthorGetOrCreateRequest(BaseModel):
    """Схема для get_or_create операции."""
    
    vk_id: PositiveInt = Field(description="VK ID автора")
    author_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Имя автора"
    )
    author_screen_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Screen name автора"
    )
    author_photo_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL фото автора"
    )

    @field_validator('author_photo_url')
    @classmethod
    def validate_photo_url(cls, v: Optional[str]) -> Optional[str]:
        """Валидация URL фото."""
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('Photo URL must start with http:// or https://')
        return v

    model_config = ConfigDict(
        str_max_length=500,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "vk_id": 123456789,
                    "author_name": "Иван",
                    "author_screen_name": "ivan_ivanov",
                    "author_photo_url": "https://vk.com/images/camera_200.png"
                }
            ]
        }
    )
