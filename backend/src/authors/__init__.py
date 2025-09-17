"""
Модуль для работы с авторами VK - рефакторинг

Упрощенная архитектура:
- models: SQLAlchemy модели и Pydantic схемы
- services: бизнес-логика
- api: FastAPI роутеры
"""

from .api import health_check, router
from .exceptions import (
    AuthorAlreadyExistsError,
    AuthorError,
    AuthorNotFoundError,
    AuthorValidationError,
)
from .models import AuthorModel
from .repository import AuthorRepository
from .schemas import (
    AuthorCreate,
    AuthorResponse,
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
    "AuthorStatus",

    # Repository
    "AuthorRepository",

    # Services
    "AuthorService",

    # Exceptions
    "AuthorError",
    "AuthorNotFoundError",
    "AuthorAlreadyExistsError",
    "AuthorValidationError",

    # API
    "router",
    "health_check",
]
