"""
Репозиторий для работы с комментариями
"""

from typing import List, Optional

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from comments.models import Comment, CommentKeywordMatch
from comments.schemas import CommentCreate, CommentFilter, CommentUpdate


class CommentRepository:
    """Репозиторий для работы с комментариями"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, comment_id: int, include_author: bool = False) -> Optional[Comment]:
        """Получить комментарий по ID"""
        query = select(Comment).where(Comment.id == comment_id)

        if include_author:
            query = query.options(
                selectinload(Comment.keyword_matches),
                joinedload(Comment.author)
            )
        else:
            query = query.options(selectinload(Comment.keyword_matches))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_id: int) -> Optional[Comment]:
        """Получить комментарий по VK ID"""
        query = (
            select(Comment)
            .options(selectinload(Comment.keyword_matches))
            .where(Comment.vk_id == vk_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_list(
        self,
        filters: Optional[CommentFilter] = None,
        limit: int = 20,
        offset: int = 0,
        include_author: bool = False,
    ) -> List[Comment]:
        """Получить список комментариев с фильтрацией"""
        query = select(Comment)

        if include_author:
            query = query.options(
                selectinload(Comment.keyword_matches),
                joinedload(Comment.author)
            )
        else:
            query = query.options(selectinload(Comment.keyword_matches))

        if filters:
            query = self._apply_filters(query, filters)

        query = query.order_by(Comment.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    def _apply_filters(self, query, filters: CommentFilter):
        """Применить фильтры к запросу"""
        if filters.group_id is not None:
            query = query.where(Comment.group_id == filters.group_id)

        if filters.post_id is not None:
            query = query.where(Comment.post_id == filters.post_id)

        if filters.author_id is not None:
            query = query.where(Comment.author_id == filters.author_id)

        if filters.search_text:
            query = query.where(Comment.text.ilike(f"%{filters.search_text}%"))

        if filters.is_deleted is not None:
            query = query.where(Comment.is_deleted == filters.is_deleted)

        return query

    async def create(self, comment_data: CommentCreate) -> Comment:
        """Создать новый комментарий"""
        comment = Comment(
            vk_id=comment_data.vk_id,
            group_id=comment_data.group_id,
            post_id=comment_data.post_id,
            author_id=comment_data.author_id,
            text=comment_data.text,
        )

        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def update(self, comment_id: int, update_data: CommentUpdate) -> Optional[Comment]:
        """Обновить комментарий"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(comment, field, value)

        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False

        comment.is_deleted = True
        await self.db.commit()
        return True

    async def count(self, filters: Optional[CommentFilter] = None) -> int:
        """Подсчитать количество комментариев"""
        query = select(func.count(Comment.id))

        if filters:
            query = self._apply_filters(query, filters)

        result = await self.db.execute(query)
        return result.scalar()

    async def get_stats(self) -> dict:
        """Получить статистику комментариев"""
        # Общее количество
        total_query = select(func.count(Comment.id))
        total_result = await self.db.execute(total_query)
        total_comments = total_result.scalar()

        # По группам
        groups_query = (
            select(Comment.group_id, func.count(Comment.id))
            .group_by(Comment.group_id)
        )
        groups_result = await self.db.execute(groups_query)
        comments_by_group = dict(groups_result.all())

        # По авторам
        authors_query = (
            select(Comment.author_id, func.count(Comment.id))
            .group_by(Comment.author_id)
        )
        authors_result = await self.db.execute(authors_query)
        comments_by_author = dict(authors_result.all())

        # Среднее по группам
        avg_per_group = (
            total_comments / len(comments_by_group)
            if comments_by_group else 0
        )

        return {
            "total_comments": total_comments,
            "comments_by_group": comments_by_group,
            "comments_by_author": comments_by_author,
            "avg_comments_per_group": round(avg_per_group, 2),
        }

    async def search_by_keywords(
        self,
        keywords: List[str],
        limit: int = 20,
        offset: int = 0
    ) -> List[Comment]:
        """Поиск комментариев по ключевым словам"""
        if not keywords:
            return []

        query = (
            select(Comment)
            .join(CommentKeywordMatch, Comment.id == CommentKeywordMatch.comment_id)
            .where(CommentKeywordMatch.keyword.in_(keywords))
            .options(
                selectinload(Comment.keyword_matches),
                joinedload(Comment.author)
            )
            .distinct()
            .order_by(Comment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_by_keywords(self, keywords: List[str]) -> int:
        """Подсчитать количество комментариев по ключевым словам"""
        if not keywords:
            return 0

        query = (
            select(func.count(Comment.id.distinct()))
            .join(CommentKeywordMatch, Comment.id == CommentKeywordMatch.comment_id)
            .where(CommentKeywordMatch.keyword.in_(keywords))
        )

        result = await self.db.execute(query)
        return result.scalar()

    async def get_keyword_match(
        self,
        comment_id: int,
        keyword: str
    ) -> Optional[CommentKeywordMatch]:
        """Получить связь комментария с ключевым словом"""
        query = (
            select(CommentKeywordMatch)
            .where(
                and_(
                    CommentKeywordMatch.comment_id == comment_id,
                    CommentKeywordMatch.keyword == keyword
                )
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_keyword_match(
        self,
        comment_id: int,
        keyword: str,
        confidence: int
    ) -> CommentKeywordMatch:
        """Создать связь комментария с ключевым словом"""
        match = CommentKeywordMatch(
            comment_id=comment_id,
            keyword=keyword,
            confidence=confidence
        )

        self.db.add(match)
        await self.db.commit()
        await self.db.refresh(match)
        return match

    async def update_keyword_match(
        self,
        comment_id: int,
        keyword: str,
        confidence: int
    ) -> bool:
        """Обновить уверенность связи комментария с ключевым словом"""
        match = await self.get_keyword_match(comment_id, keyword)
        if not match:
            return False

        match.confidence = confidence
        await self.db.commit()
        return True

    async def delete_keyword_matches(self, comment_id: int) -> bool:
        """Удалить все связи комментария с ключевыми словами"""
        query = delete(CommentKeywordMatch).where(
            CommentKeywordMatch.comment_id == comment_id
        )

        await self.db.execute(query)
        await self.db.commit()
        return True
