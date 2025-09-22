"""
API схемы для аутентификации
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Схема ответа при успешном входе"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Схема ответа при обновлении токена"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    """Схема для смены пароля"""
    current_password: str
    new_password: str = Field(..., min_length=8)


class ResetPasswordRequest(BaseModel):
    """Схема для сброса пароля"""
    email: EmailStr


class ResetPasswordConfirmRequest(BaseModel):
    """Схема для подтверждения сброса пароля"""
    token: str
    new_password: str = Field(..., min_length=8)


class LogoutRequest(BaseModel):
    """Схема для выхода из системы"""
    refresh_token: Optional[str] = None


class RegisterRequest(BaseModel):
    """Схема для регистрации"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)


class RegisterResponse(BaseModel):
    """Схема ответа при успешной регистрации"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class SuccessResponse(BaseModel):
    """Схема успешного ответа"""
    success: bool = True
    message: str
