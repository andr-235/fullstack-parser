"""
Модуль аутентификации

Предоставляет функциональность аутентификации и управления пользователями
"""

from .config import AuthConfig
from .dependencies import get_current_active_user, get_current_user
from .exceptions import AuthError, UserNotFoundError, InvalidCredentialsError
from .router import router
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from .service import AuthService

__all__ = [
    "router",
    "get_current_user",
    "get_current_active_user",
    "AuthService",
    "AuthConfig",
    "AuthError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
]
