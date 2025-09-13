"""
API схемы для пользователей

Содержит Pydantic схемы для работы с пользователями через API
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from user.domain.value_objects.user_status import UserStatus


class UserCreateRequest(BaseModel):
    """Схема для создания пользователя"""
    
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль (минимум 8 символов)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Полное имя")
    is_superuser: bool = Field(default=False, description="Является ли суперпользователем")


class UserUpdateRequest(BaseModel):
    """Схема для обновления пользователя"""
    
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Полное имя")
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    status: Optional[UserStatus] = Field(None, description="Статус пользователя")
    is_superuser: Optional[bool] = Field(None, description="Является ли суперпользователем")


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    
    id: int = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="Полное имя")
    status: UserStatus = Field(..., description="Статус пользователя")
    is_superuser: bool = Field(..., description="Является ли суперпользователем")
    email_verified: bool = Field(..., description="Подтвержден ли email")
    last_login: Optional[datetime] = Field(None, description="Последний вход")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Схема ответа со списком пользователей"""
    
    users: List[UserResponse] = Field(..., description="Список пользователей")
    total: int = Field(..., description="Общее количество пользователей")
    limit: int = Field(..., description="Лимит записей")
    offset: int = Field(..., description="Смещение")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")


class UserStatsResponse(BaseModel):
    """Схема ответа со статистикой пользователей"""
    
    total_users: int = Field(..., description="Общее количество пользователей")
    active_users: int = Field(..., description="Активных пользователей")
    inactive_users: int = Field(..., description="Неактивных пользователей")
    locked_users: int = Field(..., description="Заблокированных пользователей")
    pending_verification: int = Field(..., description="Ожидающих подтверждения")
    superusers: int = Field(..., description="Суперпользователей")
