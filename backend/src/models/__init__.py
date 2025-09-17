"""
Импорт всех моделей для правильной инициализации SQLAlchemy relationships
"""

# Импортируем все модели в правильном порядке
from authors.models import AuthorModel
from comments.models import Comment, CommentKeywordMatch
from posts.models import Post
from src.user.models import User
from groups.models import Group
from keywords.models import Keyword

__all__ = [
    "AuthorModel",
    "Comment", 
    "CommentKeywordMatch",
    "Post",
    "User",
    "Group",
    "Keyword",
]
