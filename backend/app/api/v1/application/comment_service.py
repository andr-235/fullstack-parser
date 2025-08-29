"""
Application Service для комментариев (DDD)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..domain.comment import Comment, CommentContent, CommentStatus
from ..domain.keyword import Keyword
from .base import ApplicationService


class CommentApplicationService(ApplicationService):
    """Application Service для работы с комментариями"""

    def __init__(self, comment_repository, keyword_repository):
        self.comment_repository = comment_repository
        self.keyword_repository = keyword_repository

    async def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Получить комментарий по ID"""
        return await self.comment_repository.find_by_id(comment_id)

    async def get_comments_by_group(
        self,
        group_id: int,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False,
    ) -> List[Comment]:
        """Получить комментарии группы"""
        # Здесь будет логика фильтрации и пагинации
        comments = await self.comment_repository.find_by_group_id(group_id)

        if not include_archived:
            comments = [c for c in comments if not c.is_archived]

        return comments[offset : offset + limit]

    async def search_comments(
        self,
        query: str,
        group_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Comment]:
        """Поиск комментариев по тексту"""
        # Здесь будет логика поиска
        all_comments = await self.comment_repository.find_all()

        # Фильтрация по группе
        if group_id:
            all_comments = [c for c in all_comments if c.group_id == group_id]

        # Фильтрация по тексту
        filtered_comments = []
        for comment in all_comments:
            if query.lower() in comment.content.text.lower():
                filtered_comments.append(comment)

        return filtered_comments[offset : offset + limit]

    async def mark_comment_as_viewed(self, comment_id: int) -> bool:
        """Отметить комментарий как просмотренный"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.mark_as_viewed()
        await self.comment_repository.save(comment)
        return True

    async def mark_comment_as_processed(self, comment_id: int) -> bool:
        """Отметить комментарий как обработанный"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.mark_as_processed()
        await self.comment_repository.save(comment)
        return True

    async def archive_comment(self, comment_id: int) -> bool:
        """Архивировать комментарий"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.archive()
        await self.comment_repository.save(comment)
        return True

    async def unarchive_comment(self, comment_id: int) -> bool:
        """Разархивировать комментарий"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.unarchive()
        await self.comment_repository.save(comment)
        return True

    async def analyze_comment_with_keywords(
        self, comment_id: int
    ) -> Dict[str, Any]:
        """Анализировать комментарий на совпадения с ключевыми словами"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return {"error": "Comment not found"}

        keywords = await self.keyword_repository.find_active_keywords()
        matches = []

        for keyword in keywords:
            if keyword.word.lower() in comment.content.text.lower():
                comment.add_keyword_match(keyword.id, keyword.word)
                matches.append(
                    {
                        "keyword_id": keyword.id,
                        "keyword_word": keyword.word,
                        "keyword_category": keyword.category_name,
                    }
                )

        if matches:
            await self.comment_repository.save(comment)

        return {
            "comment_id": comment.id,
            "matches_found": len(matches),
            "matches": matches,
        }

    async def get_comment_statistics(
        self, group_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Получить статистику по комментариям"""
        comments = await self.comment_repository.find_all()

        if group_id:
            comments = [c for c in comments if c.group_id == group_id]

        total_comments = len(comments)
        viewed_comments = len([c for c in comments if c.is_viewed])
        processed_comments = len([c for c in comments if c.is_processed])
        archived_comments = len([c for c in comments if c.is_archived])

        return {
            "total_comments": total_comments,
            "viewed_comments": viewed_comments,
            "processed_comments": processed_comments,
            "archived_comments": archived_comments,
            "unprocessed_comments": total_comments - processed_comments,
        }
