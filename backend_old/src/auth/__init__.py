"""
Модуль аутентификации

Предоставляет функциональность аутентификации и управления пользователями
"""

from .config import AuthConfig
from .dependencies import get_current_active_user, get_current_user
from .exceptions import AuthException, UserNotFoundError, InvalidCredentialsError
from .router import router
from .schemas import LoginRequest, RegisterRequest, LoginResponse, RegisterResponse
from .service import AuthService

__all__ = [
    "router",
    "get_current_user",
    "get_current_active_user",
    "AuthService",
    "AuthConfig",
    "AuthException",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "LoginRequest",
    "RegisterRequest",
    "LoginResponse",
    "RegisterResponse",
]
