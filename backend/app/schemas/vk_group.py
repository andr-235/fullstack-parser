"""
Pydantic схемы для VK групп
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampMixin, IDMixin


class VKGroupBase(BaseModel):
    """Базовая схема VK группы"""
    screen_name: str = Field(..., description="Короткое имя группы (@group_name)")
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")
    is_active: bool = Field(default=True, description="Активен ли мониторинг группы")
    max_posts_to_check: int = Field(default=100, description="Максимум постов для проверки")


class VKGroupCreate(VKGroupBase):
    """Схема для создания VK группы"""
    vk_id_or_screen_name: str = Field(..., description="ID группы или короткое имя для поиска в VK")


class VKGroupUpdate(BaseModel):
    """Схема для обновления VK группы"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    max_posts_to_check: Optional[int] = None


class VKGroupResponse(VKGroupBase, IDMixin, TimestampMixin, BaseSchema):
    """Схема ответа VK группы"""
    vk_id: int = Field(..., description="ID группы в ВК")
    last_parsed_at: Optional[datetime] = Field(None, description="Когда последний раз парсили группу")
    total_posts_parsed: int = Field(default=0, description="Общее количество обработанных постов")
    total_comments_found: int = Field(default=0, description="Общее количество найденных комментариев")
    members_count: Optional[int] = Field(None, description="Количество участников")
    is_closed: bool = Field(default=False, description="Закрытая ли группа")
    photo_url: Optional[str] = Field(None, description="URL аватара группы")


class VKGroupStats(BaseModel):
    """Статистика по группе"""
    group_id: int
    total_posts: int
    total_comments: int
    comments_with_keywords: int
    last_activity: Optional[datetime]
    top_keywords: list[str] 