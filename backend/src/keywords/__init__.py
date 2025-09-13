"""
Модуль Keywords - управление ключевыми словами
"""

from .models import Keyword, KeywordsRepository
from .router import router
from .schemas import (
    KeywordCreate,
    KeywordResponse,
    KeywordsListResponse,
    KeywordStats,
    KeywordUpdate,
)
from .service import KeywordsService

__all__ = [
    "Keyword",
    "KeywordsRepository",
    "KeywordsService",
    "KeywordCreate",
    "KeywordUpdate",
    "KeywordResponse",
    "KeywordsListResponse",
    "KeywordStats",
    "router",
]
