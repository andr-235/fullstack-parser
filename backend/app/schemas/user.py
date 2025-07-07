"""
Pydantic схемы для Пользователей
"""

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# Базовая схема пользователя
class UserBase(BaseSchema):
    """Базовые поля пользователя."""

    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str | None = Field(None, description="Полное имя")
    is_active: bool = Field(default=True, description="Активен ли пользователь")
    is_superuser: bool = Field(
        default=False, description="Является ли суперпользователем"
    )


# Схема для создания пользователя
class UserCreate(UserBase):
    """Схема для создания нового пользователя."""

    password: str = Field(..., min_length=8, description="Пароль пользователя")


# Схема для обновления пользователя
class UserUpdate(BaseSchema):
    """Схема для обновления данных пользователя."""

    email: EmailStr | None = Field(None, description="Email пользователя")
    full_name: str | None = Field(None, description="Полное имя")
    password: str | None = Field(None, min_length=8, description="Новый пароль")
    is_active: bool | None = Field(None, description="Активен ли пользователь")
    is_superuser: bool | None = Field(
        None, description="Является ли суперпользователем"
    )


# Схема для чтения данных пользователя
class UserRead(UserBase, IDMixin, TimestampMixin):
    """Схема для возврата данных пользователя через API."""

    pass


# Внутренняя схема для работы с данными из БД
class UserInDB(UserRead):
    """Полная схема пользователя, включая хешированный пароль."""

    hashed_password: str
