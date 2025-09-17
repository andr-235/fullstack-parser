"""
Зависимости для модуля Comments
"""

from typing import Optional

from comments.repository import CommentRepository
from comments.service import CommentService


def get_comments_repository(db: Optional[object] = None) -> CommentRepository:
    """Получить репозиторий комментариев"""
    return CommentRepository(db)


def get_comments_service(repository: Optional[CommentRepository] = None) -> CommentService:
    """Получить сервис комментариев"""
    return CommentService(repository)
