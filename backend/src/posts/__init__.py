"""
Posts module

Упрощенный модуль для работы с постами VK
"""

from .models import Post, PostRepository, get_post_repository
from .schemas import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostFilter,
    PostListResponse,
    PostStats,
    PostBulkUpdate
)
from .service import PostService
from .router import router as posts_router

__all__ = [
    # Models
    "Post",
    "PostRepository",
    "get_post_repository",
    
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