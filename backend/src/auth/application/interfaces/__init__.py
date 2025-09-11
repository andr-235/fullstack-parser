"""
Интерфейсы для модуля Auth

Содержит все интерфейсы для слоя приложения
"""

from .user_repository import UserRepositoryInterface
from .password_service import PasswordServiceInterface

__all__ = [
    "UserRepositoryInterface",
    "PasswordServiceInterface",
]
