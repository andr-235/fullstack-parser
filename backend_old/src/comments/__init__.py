"""
Модуль Comments

Простой и эффективный модуль для работы с комментариями VK
"""

from comments.models import Comment, CommentKeywordMatch
from comments.repository import CommentRepository
from comments.router import router
from comments.schemas import (
    BatchKeywordAnalysisRequest,
    BatchKeywordAnalysisResponse,
    CommentCreate,
    CommentFilter,
    CommentListResponse,
    CommentResponse,
    CommentStats,
    CommentUpdate,
    KeywordAnalysisRequest,
    KeywordAnalysisResponse,
    KeywordMatch,
    KeywordSearchRequest,
    KeywordSearchResponse,
    KeywordStatisticsResponse,
)
from comments.service import CommentService

__all__ = [
    # Роутер
    "router",
    # Сервисы
    "CommentService",
    "CommentRepository",
    # Модели
    "Comment",
    "CommentKeywordMatch",
    # Схемы
    "CommentResponse", "CommentListResponse", "CommentCreate", "CommentUpdate",
    "CommentFilter", "CommentStats", "KeywordMatch", "KeywordAnalysisRequest",
    "KeywordAnalysisResponse", "BatchKeywordAnalysisRequest", "BatchKeywordAnalysisResponse",
    "KeywordSearchRequest", "KeywordSearchResponse", "KeywordStatisticsResponse"
]
