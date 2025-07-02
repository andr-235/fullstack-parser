# Pydantic схемы для VK Comments Parser

from .base import BaseSchema, TimestampMixin, IDMixin, PaginationParams, PaginatedResponse, StatusResponse
from .vk_group import VKGroupBase, VKGroupCreate, VKGroupUpdate, VKGroupResponse, VKGroupStats
from .keyword import KeywordBase, KeywordCreate, KeywordUpdate, KeywordResponse, KeywordStats
from .vk_comment import VKCommentBase, VKCommentResponse, CommentWithKeywords, CommentSearchParams
from .parser import ParseTaskCreate, ParseTaskResponse, ParseStats, GlobalStats, DashboardStats

__all__ = [
    # Base
    "BaseSchema", "TimestampMixin", "IDMixin", "PaginationParams", "PaginatedResponse", "StatusResponse",
    # VK Groups
    "VKGroupBase", "VKGroupCreate", "VKGroupUpdate", "VKGroupResponse", "VKGroupStats",
    # Keywords
    "KeywordBase", "KeywordCreate", "KeywordUpdate", "KeywordResponse", "KeywordStats",
    # Comments
    "VKCommentBase", "VKCommentResponse", "CommentWithKeywords", "CommentSearchParams",
    # Parser
    "ParseTaskCreate", "ParseTaskResponse", "ParseStats", "GlobalStats", "DashboardStats"
] 