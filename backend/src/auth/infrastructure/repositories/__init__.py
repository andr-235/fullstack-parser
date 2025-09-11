"""
Репозитории модуля Auth

Содержит реализации репозиториев для инфраструктурного слоя
"""

from .sqlalchemy_user_repository import SQLAlchemyUserRepository

__all__ = [
    "SQLAlchemyUserRepository",
]
