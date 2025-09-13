"""
Модуль для работы с авторами VK - рефакторинг

Упрощенная архитектура:
- models: SQLAlchemy модели и Pydantic схемы
- services: бизнес-логика
- api: FastAPI роутеры
"""

from .api import health_check, router
from .models import AuthorModel
from .schemas import (
    AuthorBulkAction,
    AuthorCreate,
    AuthorFilter,
    AuthorListResponse,
    AuthorResponse,
    AuthorSearch,
    AuthorStatus,
    AuthorUpdate,
)
from .services import AuthorService

__all__ = [
    # Models
    "AuthorModel",
    "AuthorCreate",
    "AuthorUpdate",
    "AuthorResponse",
    "AuthorListResponse",
    "AuthorFilter",
    "AuthorSearch",
    "AuthorBulkAction",
    "AuthorStatus",

    # Services
    "AuthorService",

    # API
    "router",
    "health_check",
]
