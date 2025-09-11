"""
DTO для модуля Auth

Содержит все Data Transfer Objects для аутентификации
"""

from .user_dto import UserDTO
from .register_user_dto import RegisterUserDTO

__all__ = [
    "UserDTO",
    "RegisterUserDTO",
]
