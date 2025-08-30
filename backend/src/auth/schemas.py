"""
Pydantic схемы для модуля Auth

Определяет входные и выходные модели данных для API аутентификации
"""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from ..pagination import PaginatedResponse


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="Полное имя пользователя")
    is_active: bool = Field(
        default=True, description="Активен ли пользователь"
    )
    is_superuser: bool = Field(
        default=False, description="Является ли суперпользователем"
    )


class UserCreate(UserBase):
    """Схема для создания пользователя"""

    password: str = Field(..., min_length=8, description="Пароль пользователя")


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""

    email: Optional[EmailStr] = Field(None, description="Новый email")
    full_name: Optional[str] = Field(None, description="Новое полное имя")
    is_active: Optional[bool] = Field(
        None, description="Новый статус активности"
    )
    password: Optional[str] = Field(
        None, min_length=8, description="Новый пароль"
    )


class UserResponse(UserBase):
    """Схема ответа с информацией о пользователе"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID пользователя в базе данных")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(
        ..., description="Время последнего обновления"
    )


class UserListResponse(PaginatedResponse[UserResponse]):
    """Схема ответа со списком пользователей"""

    pass


class LoginRequest(BaseModel):
    """Запрос на вход в систему"""

    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")


class TokenResponse(BaseModel):
    """Ответ с токенами аутентификации"""

    access_token: str = Field(..., description="JWT access токен")
    refresh_token: str = Field(..., description="JWT refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    user: UserResponse = Field(..., description="Информация о пользователе")


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""

    refresh_token: str = Field(..., description="Refresh токен")


class TokenValidationResponse(BaseModel):
    """Ответ валидации токена"""

    valid: bool = Field(..., description="Валиден ли токен")
    user: Optional[UserResponse] = Field(
        None, description="Информация о пользователе"
    )
    expires_at: Optional[datetime] = Field(
        None, description="Время истечения токена"
    )


class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля"""

    email: EmailStr = Field(..., description="Email пользователя")


class PasswordResetConfirm(BaseModel):
    """Подтверждение сброса пароля"""

    token: str = Field(..., description="Токен сброса пароля")
    new_password: str = Field(..., min_length=8, description="Новый пароль")


class PasswordChange(BaseModel):
    """Изменение пароля"""

    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")


class UserStats(BaseModel):
    """Статистика пользователей"""

    total_users: int = Field(..., description="Общее количество пользователей")
    active_users: int = Field(
        ..., description="Количество активных пользователей"
    )
    superusers: int = Field(..., description="Количество суперпользователей")
    new_users_today: int = Field(
        ..., description="Новых пользователей сегодня"
    )
    new_users_week: int = Field(
        ..., description="Новых пользователей за неделю"
    )


class AuthConfig(BaseModel):
    """Конфигурация аутентификации"""

    jwt_algorithm: str = Field(..., description="Алгоритм JWT")
    access_token_expire_minutes: int = Field(
        ..., description="Время жизни access токена"
    )
    refresh_token_expire_days: int = Field(
        ..., description="Время жизни refresh токена"
    )
    password_min_length: int = Field(
        ..., description="Минимальная длина пароля"
    )
    max_login_attempts: int = Field(..., description="Максимум попыток входа")
    lockout_duration_minutes: int = Field(
        ..., description="Длительность блокировки"
    )


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""

    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="Полное имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя")


class RegisterResponse(BaseModel):
    """Ответ на регистрацию"""

    user: UserResponse = Field(..., description="Созданный пользователь")
    message: str = Field(..., description="Сообщение об успешной регистрации")


class EmailVerificationRequest(BaseModel):
    """Запрос на верификацию email"""

    token: str = Field(..., description="Токен верификации")


class ProfileUpdate(BaseModel):
    """Обновление профиля пользователя"""

    full_name: Optional[str] = Field(None, description="Новое полное имя")
    email: Optional[EmailStr] = Field(None, description="Новый email")


# Экспорт всех схем
__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "TokenValidationResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChange",
    "UserStats",
    "AuthConfig",
    "RegisterRequest",
    "RegisterResponse",
    "EmailVerificationRequest",
    "ProfileUpdate",
]
