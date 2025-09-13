"""
Модуль для работы с авторами VK - рефакторинг

Упрощенная архитектура:
- models: SQLAlchemy модели и Pydantic схемы
- services: бизнес-логика
- api: FastAPI роутеры
"""

from .models import AuthorModel
from .schemas import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    AuthorListResponse,
    AuthorFilter,
    AuthorSearch,
    AuthorBulkAction,
    AuthorStatus,
)

from .services import AuthorService
from .api import router, health_check

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