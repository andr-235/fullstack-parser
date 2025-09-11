"""
Use Cases для модуля Auth

Содержит все use cases для аутентификации и управления пользователями
"""

from .register_user import RegisterUserUseCase

__all__ = [
    "RegisterUserUseCase",
]
