"""Initializes the models package."""

# Import all models here to ensure they are registered with SQLAlchemy's metadata
from app.models.base import Base, BaseModel
from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.error_entry import ErrorEntry
from app.models.error_report import ErrorReport
from app.models.keyword import Keyword
from app.models.user import User
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "VKGroup",
    "VKPost",
    "VKComment",
    "Keyword",
    "CommentKeywordMatch",
    "ErrorReport",
    "ErrorEntry",
]
