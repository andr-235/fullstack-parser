"""
Модуль аутентификации

Предоставляет функциональность аутентификации и управления пользователями
"""

from .router import router
from .dependencies import get_current_user, get_current_active_user
from .services import AuthService

__all__ = [
    "router",
    "get_current_user", 
    "get_current_active_user",
    "AuthService",
]