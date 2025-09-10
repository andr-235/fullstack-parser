"""
SQLAlchemy модели для модуля Comments

Определяет репозиторий и специфические модели для работы с комментариями
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import (
    select,
    and_,
    or_,
    desc,
    func,
    String,
    Text,
    Integer,
    DateTime,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Comment as BaseComment
from ..database import get_db_session
from ..exceptions import CommentNotFoundError


class CommentRepository:
    """
    Репозиторий для работы с комментариями

    Предоставляет интерфейс для CRUD операций с комментариями
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, comment_id: int) -> Optional[BaseComment]:
        """Получить комментарий по ID"""
        query = select(BaseComment).where(BaseComment.id == comment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_comment_id: str) -> Optional[BaseComment]:
        """Получить комментарий по VK ID"""
        query = select(BaseComment).where(BaseComment.vk_id == vk_comment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_group_id(
        self,
        group_id: str,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить комментарии по ID группы"""
        group_id_int = int(group_id) if group_id.isdigit() else 0

        # Получаем комментарии по group_vk_id
        query = select(BaseComment).where(
            BaseComment.group_vk_id == group_id_int
        )

        if search_text:
            query = query.where(BaseComment.text.ilike(f"%{search_text}%"))

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        query = (
            query.order_by(desc(BaseComment.published_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_post_id(
        self,
        post_id: str,
        limit: int = 100,
        offset: int = 0,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить комментарии к посту"""
        query = select(BaseComment).where(BaseComment.post_id == post_id)

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        query = (
            query.order_by(BaseComment.published_at)
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_comments(
        self,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить все комментарии с пагинацией"""
        query = select(BaseComment)

        if search_text:
            query = query.where(BaseComment.text.ilike(f"%{search_text}%"))

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        query = (
            query.order_by(desc(BaseComment.published_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, comment_data: Dict[str, Any]) -> BaseComment:
        """Создать новый комментарий"""
        comment = BaseComment(**comment_data)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def update(
        self, comment_id: int, update_data: Dict[str, Any]
    ) -> BaseComment:
        """Обновить комментарий"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(comment_id)

        for key, value in update_data.items():
            if hasattr(comment, key):
                setattr(comment, key, value)

        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False

        await self.db.delete(comment)
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику комментариев"""
        # Общее количество
        total_query = select(func.count()).select_from(BaseComment)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        # Среднее количество лайков
        avg_likes_query = select(
            func.avg(BaseComment.likes_count)
        ).select_from(BaseComment)
        avg_likes_result = await self.db.execute(avg_likes_query)
        avg_likes = avg_likes_result.scalar() or 0.0

        return {
            "total_comments": total,
            "avg_likes_per_comment": round(avg_likes, 2),
        }

    async def mark_as_viewed(self, comment_id: int) -> bool:
        """Отметить комментарий как просмотренный"""
        from datetime import datetime

        update_data = {
            "processed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        try:
            await self.update(comment_id, update_data)
            return True
        except CommentNotFoundError:
            return False

    async def bulk_update(
        self, comment_ids: List[int], update_data: Dict[str, Any]
    ) -> int:
        """Массовое обновление комментариев"""
        from sqlalchemy import update
        from datetime import datetime

        # Добавляем время обновления
        update_data["updated_at"] = datetime.utcnow()

        query = (
            update(BaseComment)
            .where(BaseComment.id.in_(comment_ids))
            .values(**update_data)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

    async def count_by_group(
        self,
        group_id: str,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев в группе"""
        group_id_int = int(group_id) if group_id.isdigit() else 0

        query = select(func.count(BaseComment.id)).where(
            BaseComment.group_vk_id == group_id_int
        )

        if search_text:
            query = query.where(BaseComment.text.ilike(f"%{search_text}%"))

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_by_post(
        self,
        post_id: str,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев к посту"""
        query = select(func.count(BaseComment.id)).where(
            BaseComment.post_id == post_id
        )

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_all(
        self,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать общее количество комментариев"""
        query = select(func.count(BaseComment.id))

        if search_text:
            query = query.where(BaseComment.text.ilike(f"%{search_text}%"))

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        result = await self.db.execute(query)
        return result.scalar() or 0


# Функции для создания репозитория
async def get_comment_repository(
    db: AsyncSession,
) -> CommentRepository:
    """Создать репозиторий комментариев"""
    return CommentRepository(db)


# Экспорт
__all__ = [
    "CommentRepository",
    "get_comment_repository",
]
