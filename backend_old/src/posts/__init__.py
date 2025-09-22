"""
Posts module

Упрощенный модуль для работы с постами VK
"""

from .models import Post, PostRepository
from .router import router as posts_router
from .schemas import (
    PostBulkUpdate,
    PostCreate,
    PostFilter,
    PostListResponse,
    PostResponse,
    PostStats,
    PostUpdate,
)
from .service import PostService

__all__ = [
    # Models
    "Post",
    "PostRepository",

    # Schemas
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "PostFilter",
    "PostListResponse",
    "PostStats",
    "PostBulkUpdate",

    # Service
    "PostService",

    # Router
    "posts_router",
]
