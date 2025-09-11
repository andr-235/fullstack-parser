"""
Value Objects модуля Auth

Содержит объекты-значения для аутентификации
"""

from .email import Email
from .password import Password
from .user_id import UserId

__all__ = [
    "Email",
    "Password", 
    "UserId",
]
