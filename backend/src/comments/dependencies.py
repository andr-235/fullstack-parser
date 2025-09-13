"""
Зависимости для модуля Comments
"""

from comments.repository import CommentRepository
from comments.service import CommentService


def get_comments_repository(db = None) -> CommentRepository:
    """Получить репозиторий комментариев"""
    return CommentRepository(db)


def get_comments_service(repository: CommentRepository = None) -> CommentService:
    """Получить сервис комментариев"""
    return CommentService(repository)
