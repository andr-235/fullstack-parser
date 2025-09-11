"""
Модуль Comments

Предоставляет API для работы с комментариями VK
"""

from .router import router
from .service import CommentService
from .repository import CommentRepository
from .handlers import CommentHandlers
from .models import Comment, CommentKeywordMatch, CommentAnalysis
from .schemas import (
    CommentResponse,
    CommentListResponse,
    CommentCreate,
    CommentUpdate,
    CommentStats,
    CommentBulkAction,
    CommentBulkResponse,
)
from .exceptions import (
    CommentError,
    CommentNotFoundError,
    CommentValidationError,
    CommentDuplicateError,
    CommentPermissionError,
    CommentServiceError,
)

# Экспорт основных компонентов
__all__ = [
    # Роутер
    "router",
    # Сервисы
    "CommentService",
    "CommentRepository",
    "CommentHandlers",
    # Модели
    "Comment",
    "CommentKeywordMatch",
    "CommentAnalysis",
    # Схемы
    "CommentResponse",
    "CommentListResponse",
    "CommentCreate",
    "CommentUpdate",
    "CommentStats",
    "CommentBulkAction",
    "CommentBulkResponse",
    # Исключения
    "CommentError",
    "CommentNotFoundError",
    "CommentValidationError",
    "CommentDuplicateError",
    "CommentPermissionError",
    "CommentServiceError",
]
