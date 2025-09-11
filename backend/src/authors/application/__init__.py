"""
Application слой модуля авторов

Содержит use cases и сервисы приложения
"""

from .services import AuthorService
from .use_cases import (
    CreateAuthorUseCase,
    GetAuthorUseCase,
    UpdateAuthorUseCase,
    DeleteAuthorUseCase,
    ListAuthorsUseCase,
    UpsertAuthorUseCase,
    GetOrCreateAuthorUseCase
)

__all__ = [
    "AuthorService",
    "CreateAuthorUseCase",
    "GetAuthorUseCase", 
    "UpdateAuthorUseCase",
    "DeleteAuthorUseCase",
    "ListAuthorsUseCase",
    "UpsertAuthorUseCase",
    "GetOrCreateAuthorUseCase"
]
