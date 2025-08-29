"""
Domain сущности для комментариев (DDD)
"""

from datetime import datetime
from typing import List, Optional
from .base import Entity, ValueObject


class CommentStatus(ValueObject):
    """Статус комментария"""

    def __init__(
        self,
        is_viewed: bool = False,
        is_processed: bool = False,
        is_archived: bool = False,
    ):
        self.is_viewed = is_viewed
        self.is_processed = is_processed
        self.is_archived = is_archived


class CommentContent(ValueObject):
    """Содержимое комментария"""

    def __init__(
        self,
        text: str,
        author_name: Optional[str] = None,
        author_id: Optional[int] = None,
    ):
        self.text = text
        self.author_name = author_name
        self.author_id = author_id


class Comment(Entity):
    """Доменная сущность комментария"""

    def __init__(
        self,
        id: Optional[int] = None,
        group_id: int = None,
        content: CommentContent = None,
        published_at: Optional[datetime] = None,
        vk_comment_id: Optional[int] = None,
        post_id: Optional[int] = None,
    ):
        super().__init__(id)
        self.group_id = group_id
        self.content = content
        self.published_at = published_at or datetime.utcnow()
        self.vk_comment_id = vk_comment_id
        self.post_id = post_id
        self.status = CommentStatus()
        self.keyword_matches: List["KeywordMatch"] = []

    def mark_as_viewed(self) -> None:
        """Отметить комментарий как просмотренный"""
        self.status = CommentStatus(
            is_viewed=True,
            is_processed=self.status.is_processed,
            is_archived=self.status.is_archived,
        )
        self.update()

    def mark_as_processed(self) -> None:
        """Отметить комментарий как обработанный"""
        self.status = CommentStatus(
            is_viewed=self.status.is_viewed,
            is_processed=True,
            is_archived=self.status.is_archived,
        )
        self.update()

    def archive(self) -> None:
        """Архивировать комментарий"""
        self.status = CommentStatus(
            is_viewed=self.status.is_viewed,
            is_processed=self.status.is_processed,
            is_archived=True,
        )
        self.update()

    def unarchive(self) -> None:
        """Разархивировать комментарий"""
        self.status = CommentStatus(
            is_viewed=self.status.is_viewed,
            is_processed=self.status.is_processed,
            is_archived=False,
        )
        self.update()

    def add_keyword_match(self, keyword_id: int, match_text: str) -> None:
        """Добавить совпадение с ключевым словом"""
        match = KeywordMatch(
            comment_id=self.id, keyword_id=keyword_id, match_text=match_text
        )
        self.keyword_matches.append(match)
        self.update()

    @property
    def is_viewed(self) -> bool:
        return self.status.is_viewed

    @property
    def is_processed(self) -> bool:
        return self.status.is_processed

    @property
    def is_archived(self) -> bool:
        return self.status.is_archived


class KeywordMatch(ValueObject):
    """Совпадение комментария с ключевым словом"""

    def __init__(self, comment_id: int, keyword_id: int, match_text: str):
        self.comment_id = comment_id
        self.keyword_id = keyword_id
        self.match_text = match_text
