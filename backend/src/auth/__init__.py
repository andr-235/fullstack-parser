"""
Модуль аутентификации

Предоставляет функциональность аутентификации и управления пользователями
"""

from .dependencies import get_current_active_user, get_current_user
from .router import router
from .services import AuthService, AuthServiceInterface

__all__ = [
    "router",
    "get_current_user",
    "get_current_active_user",
    "AuthService",
    "AuthServiceInterface",
]
