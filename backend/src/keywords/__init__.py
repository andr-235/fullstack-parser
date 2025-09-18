"""
Модуль Keywords - управление ключевыми словами

Новая архитектура на основе Clean Architecture:
- domain: бизнес-логика и сущности
- infrastructure: инфраструктурные компоненты (БД, внешние сервисы)
- application: API слой (роутеры, схемы)
- shared: общие компоненты (константы, исключения)
"""

# Domain слой
from .domain.entities.keyword import Keyword
from .domain.services.keyword_service import KeywordService
from .domain.interfaces.keyword_service_interface import KeywordServiceInterface
from .domain.interfaces.keyword_repository_interface import KeywordRepositoryInterface

# Infrastructure слой
from .infrastructure.repositories.keyword_repository import KeywordRepository
from .infrastructure.models.keyword_model import KeywordModel

# Presentation слой
from .presentation.api.keyword_router import router
from .presentation.schemas.keyword_schemas import (
    KeywordCreate,
    KeywordResponse,
    KeywordsListResponse,
    KeywordStats,
    KeywordUpdate,
)

# Shared слой
from .shared.constants import (
    DEFAULT_LIMIT,
    MAX_KEYWORD_LENGTH,
    MIN_PRIORITY,
    MAX_PRIORITY,
)
from .shared.exceptions import (
    KeywordNotFoundError,
    KeywordAlreadyExistsError,
    CannotActivateArchivedKeywordError,
    InvalidKeywordDataError,
)

__all__ = [
    # Domain
    "Keyword",
    "KeywordService",
    "KeywordServiceInterface",
    "KeywordRepositoryInterface",

    # Infrastructure
    "KeywordRepository",
    "KeywordModel",

    # Application
    "router",
    "KeywordCreate",
    "KeywordUpdate",
    "KeywordResponse",
    "KeywordsListResponse",
    "KeywordStats",

    # Shared
    "DEFAULT_LIMIT",
    "MAX_KEYWORD_LENGTH",
    "MIN_PRIORITY",
    "MAX_PRIORITY",
    "KeywordNotFoundError",
    "KeywordAlreadyExistsError",
    "CannotActivateArchivedKeywordError",
    "InvalidKeywordDataError",
]