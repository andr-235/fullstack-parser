"""
Модуль для работы с авторами VK

Современная архитектура с разделением на слои:
- Domain: бизнес-логика и сущности
- Application: use cases и сервисы
- Infrastructure: репозитории, кэш, очереди задач
- Presentation: FastAPI роутеры и схемы
"""

from .domain import AuthorNotFoundError, AuthorValidationError, AuthorEntity
from .application import AuthorService
from .infrastructure import Author, AuthorRepository, AuthorRedisCache, AuthorCeleryTaskQueue
from .schemas import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    AuthorListResponse,
    AuthorUpsertRequest,
    AuthorGetOrCreateRequest
)
from .dependencies import (
    get_author_repository_dependency as get_author_repository,
    get_author_service_dependency as get_author_service,
    get_author_cache_dependency as get_author_cache,
    get_author_task_queue_dependency as get_author_task_queue,
)
from .presentation import authors_router

__all__ = [
    # Domain
    "AuthorNotFoundError",
    "AuthorValidationError", 
    "AuthorEntity",
    
    # Application
    "AuthorService",
    
    # Infrastructure
    "Author",
    "AuthorRepository",
    "AuthorRedisCache",
    "AuthorCeleryTaskQueue",
    
    # Schemas
    "AuthorCreate",
    "AuthorUpdate",
    "AuthorResponse",
    "AuthorListResponse",
    "AuthorUpsertRequest",
    "AuthorGetOrCreateRequest",
    
    # Dependencies
    "get_author_repository",
    "get_author_service",
    "get_author_cache",
    "get_author_task_queue",
    
    # Presentation
    "authors_router",
]
