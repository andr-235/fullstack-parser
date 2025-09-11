"""
Domain слой модуля авторов

Содержит бизнес-логику, исключения и интерфейсы репозиториев
"""

from .exceptions import AuthorNotFoundError, AuthorValidationError
from .interfaces import AuthorRepositoryInterface
from .entities import AuthorEntity

__all__ = [
    "AuthorNotFoundError",
    "AuthorValidationError", 
    "AuthorRepositoryInterface",
    "AuthorEntity"
]
