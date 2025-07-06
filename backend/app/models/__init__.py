"""Initializes the models package."""

# Import all models here to ensure they are registered with SQLAlchemy's metadata
from app.models.base import Base, BaseModel
from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost

__all__ = [
    "BaseModel",
    "VKGroup",
    "VKPost",
    "VKComment",
    "Keyword",
    "CommentKeywordMatch",
]
