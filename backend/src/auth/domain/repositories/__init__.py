"""
Интерфейсы репозиториев модуля Auth

Содержит интерфейсы репозиториев для доменного слоя
"""

from .user_repository import UserRepository

__all__ = [
    "UserRepository",
]
