"""
Repositories модуля User
"""

from .sqlalchemy_user_repository import SQLAlchemyUserRepository
from .cached_user_repository import CachedUserRepository

__all__ = [
    "SQLAlchemyUserRepository",
    "CachedUserRepository",
]
