"""
DTO для пользователей

Содержит Data Transfer Objects для операций с пользователями
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

from user.domain.value_objects.user_status import UserStatus


class CreateUserRequestDTO(BaseModel):
    """DTO для создания пользователя"""
    
    email: EmailStr
    password: str
    full_name: str
    is_superuser: bool = False


class UpdateUserRequestDTO(BaseModel):
    """DTO для обновления пользователя"""
    
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[UserStatus] = None
    is_superuser: Optional[bool] = None


class UserResponseDTO(BaseModel):
    """DTO для ответа с данными пользователя"""
    
    id: int
    email: str
    full_name: str
    status: UserStatus
    is_superuser: bool
    email_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserListRequestDTO(BaseModel):
    """DTO для запроса списка пользователей"""
    
    limit: int = 50
    offset: int = 0
    status: Optional[UserStatus] = None
    search: Optional[str] = None


class UserListResponseDTO(BaseModel):
    """DTO для ответа со списком пользователей"""
    
    users: List[UserResponseDTO]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class UserStatsResponseDTO(BaseModel):
    """DTO для ответа со статистикой пользователей"""
    
    total_users: int
    active_users: int
    inactive_users: int
    locked_users: int
    pending_verification: int
    superusers: int
