"""
Pydantic схемы для модуля Groups
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from shared.presentation.responses.base_responses import PaginatedResponse


class GroupCreate(BaseModel):
    """Схема для создания группы"""
    vk_id: int = Field(..., description="ID группы в VK")
    screen_name: str = Field(..., description="Короткое имя группы")
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")


class GroupUpdate(BaseModel):
    """Схема для обновления группы"""
    name: Optional[str] = Field(None, description="Новое название группы")
    screen_name: Optional[str] = Field(None, description="Новое короткое имя")
    description: Optional[str] = Field(None, description="Новое описание")
    is_active: Optional[bool] = Field(None, description="Активировать/деактивировать группу")


class GroupResponse(BaseModel):
    """Схема ответа с информацией о группе"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID в базе данных")
    vk_id: int = Field(..., description="ID группы в VK")
    screen_name: str = Field(..., description="Короткое имя группы")
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")
    is_active: bool = Field(default=True, description="Активна ли группа")
    members_count: int = Field(default=0, description="Количество участников")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")


class GroupListResponse(PaginatedResponse[GroupResponse]):
    """Схема ответа со списком групп"""
    pass


class GroupBulkAction(BaseModel):
    """Массовые действия с группами"""
    group_ids: List[int] = Field(..., description="Список ID групп")
    action: str = Field(..., description="Действие: activate, deactivate")


class GroupBulkResponse(BaseModel):
    """Ответ на массовое действие"""
    success_count: int = Field(..., description="Количество успешных операций")
    error_count: int = Field(..., description="Количество ошибок")


__all__ = [
    "GroupCreate",
    "GroupUpdate", 
    "GroupResponse",
    "GroupListResponse",
    "GroupBulkAction",
    "GroupBulkResponse",
]
