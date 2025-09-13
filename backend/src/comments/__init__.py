"""
Модуль Comments

Простой и эффективный модуль для работы с комментариями VK
"""

from comments.router import router
from comments.service import CommentService
from comments.repository import CommentRepository
from comments.models import Comment, CommentKeywordMatch
from comments.schemas import (
    CommentResponse, CommentListResponse, CommentCreate, CommentUpdate,
    CommentFilter, CommentStats, KeywordMatch, KeywordAnalysisRequest,
    KeywordAnalysisResponse, BatchKeywordAnalysisRequest, BatchKeywordAnalysisResponse,
    KeywordSearchRequest, KeywordSearchResponse, KeywordStatisticsResponse
)

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