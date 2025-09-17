"""
Репозиторий для работы с комментариями
"""

from typing import List, Optional

from sqlalchemy import and_, delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from comments.models import Comment, CommentKeywordMatch
from comments.schemas import (
    CommentCreate,
    CommentFilter,
    CommentUpdate,
    DEFAULT_KEYWORD_CONFIDENCE,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    DEFAULT_OFFSET,
    MAX_KEYWORDS_LIST,
    MIN_KEYWORDS_LIST,
    MIN_WORD_LENGTH,
)

# Импортируем константы из schemas для избежания дублирования


class CommentRepository:
    """Репозиторий для работы с комментариями"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, comment_id: int, include_author: bool = False) -> Optional[Comment]:
        """
        Получить комментарий по ID.

        Args:
            comment_id: ID комментария
            include_author: Включать ли информацию об авторе

        Returns:
            Комментарий или None, если не найден
        """
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
        """
        Получить комментарий по VK ID.

        Args:
            vk_id: VK ID комментария

        Returns:
            Комментарий или None, если не найден
        """
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
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        include_author: bool = False,
    ) -> List[Comment]:
        """
        Получить список комментариев с фильтрацией.

        Args:
            filters: Фильтры для применения
            limit: Максимальное количество комментариев
            offset: Смещение для пагинации
            include_author: Включать ли информацию об авторе

        Returns:
            Список комментариев
        """
        # Параметры уже валидированы в schemas

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
        """
        Применить фильтры к запросу.

        Args:
            query: SQLAlchemy запрос
            filters: Фильтры для применения

        Returns:
            Запрос с примененными фильтрами
        """
        if filters.group_id is not None:
            query = query.where(Comment.group_id == filters.group_id)

        if filters.post_id is not None:
            query = query.where(Comment.post_id == filters.post_id)

        if filters.author_id is not None:
            query = query.where(Comment.author_id == filters.author_id)

        if filters.search_text:
            # Используем параметризованный запрос для безопасности
            search_pattern = f"%{filters.search_text}%"
            query = query.where(Comment.text.ilike(search_pattern))

        if filters.is_deleted is not None:
            query = query.where(Comment.is_deleted == filters.is_deleted)

        return query

    async def create(self, comment_data: CommentCreate) -> Comment:
        """
        Создать новый комментарий.

        Args:
            comment_data: Данные для создания комментария

        Returns:
            Созданный комментарий
        """
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
        """
        Обновить комментарий.

        Args:
            comment_id: ID комментария для обновления
            update_data: Данные для обновления

        Returns:
            Обновленный комментарий или None, если не найден
        """
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
        """
        Удалить комментарий (мягкое удаление).

        Args:
            comment_id: ID комментария для удаления

        Returns:
            True, если комментарий найден и удален, False в противном случае
        """
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
        """
        Получить статистику комментариев.

        Returns:
            Словарь со статистикой:
            - total_comments: общее количество комментариев
            - comments_by_group: комментарии по группам
            - comments_by_author: комментарии по авторам
            - avg_comments_per_group: среднее количество комментариев на группу
        """
        # Оптимизированный запрос: получаем общую статистику и группировки за один раз
        # Используем UNION для комбинирования результатов
        total_query = select(
            func.count(Comment.id).label("total_comments"),
            func.count(func.distinct(Comment.group_id)).label("total_groups"),
            func.count(func.distinct(Comment.author_id)).label("total_authors"),
            func.literal(None).label("group_id"),
            func.literal(None).label("author_id"),
            func.literal(0).label("count")
        )

        groups_query = select(
            func.literal(0).label("total_comments"),
            func.literal(0).label("total_groups"),
            func.literal(0).label("total_authors"),
            Comment.group_id,
            func.literal(None).label("author_id"),
            func.count(Comment.id).label("count")
        ).group_by(Comment.group_id)

        authors_query = select(
            func.literal(0).label("total_comments"),
            func.literal(0).label("total_groups"),
            func.literal(0).label("total_authors"),
            func.literal(None).label("group_id"),
            Comment.author_id,
            func.count(Comment.id).label("count")
        ).group_by(Comment.author_id)

        # Комбинируем запросы
        combined_query = total_query.union_all(groups_query, authors_query)

        result = await self.db.execute(combined_query)
        rows = result.all()

        # Обрабатываем результаты
        total_comments = 0
        total_groups = 0
        total_authors = 0
        comments_by_group = {}
        comments_by_author = {}

        for row in rows:
            if row.total_comments > 0:
                total_comments = row.total_comments
                total_groups = row.total_groups
                total_authors = row.total_authors
            if row.group_id is not None:
                comments_by_group[row.group_id] = row.count
            if row.author_id is not None:
                comments_by_author[row.author_id] = row.count

        # Среднее по группам
        avg_per_group = (
            total_comments / total_groups
            if total_groups > 0 else 0
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
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET
    ) -> List[Comment]:
        """
        Поиск комментариев по ключевым словам.

        Args:
            keywords: Список ключевых слов для поиска
            limit: Максимальное количество комментариев
            offset: Смещение для пагинации

        Returns:
            Список найденных комментариев
        """
        # Параметры уже валидированы в schemas

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

    async def get_total_count(self) -> int:
        """Получить общее количество комментариев"""
        from sqlalchemy import func
        query = select(func.count(Comment.id))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_count_by_period(self, days: int) -> int:
        """Получить количество комментариев за период"""
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        query = select(func.count(Comment.id)).where(Comment.created_at >= since_date)
        result = await self.db.execute(query)
        return result.scalar() or 0
