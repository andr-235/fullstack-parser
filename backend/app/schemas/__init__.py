# Pydantic схемы для VK Comments Parser

from .base import (
    BaseSchema,
    IDMixin,
    PaginatedResponse,
    PaginationParams,
    StatusResponse,
    TimestampMixin,
)
from .keyword import (
    KeywordBase,
    KeywordCreate,
    KeywordResponse,
    KeywordStats,
    KeywordUpdate,
)
from .parser import (
    DashboardStats,
    GlobalStats,
    ParseStats,
    ParseTaskCreate,
    ParseTaskResponse,
)
from .vk_comment import (
    CommentSearchParams,
    CommentWithKeywords,
    VKCommentBase,
    VKCommentResponse,
)
from .vk_group import (
    VKGroupBase,
    VKGroupCreate,
    VKGroupRead,
    VKGroupStats,
    VKGroupUpdate,
)

__all__ = [
    # Base
    "BaseSchema",
    "TimestampMixin",
    "IDMixin",
    "PaginationParams",
    "PaginatedResponse",
    "StatusResponse",
    # VK Groups
    "VKGroupBase",
    "VKGroupCreate",
    "VKGroupUpdate",
    "VKGroupRead",
    "VKGroupStats",
    # Keywords
    "KeywordBase",
    "KeywordCreate",
    "KeywordUpdate",
    "KeywordResponse",
    "KeywordStats",
    # Comments
    "VKCommentBase",
    "VKCommentResponse",
    "CommentWithKeywords",
    "CommentSearchParams",
    # Parser
    "ParseTaskCreate",
    "ParseTaskResponse",
    "ParseStats",
    "GlobalStats",
    "DashboardStats",
]
