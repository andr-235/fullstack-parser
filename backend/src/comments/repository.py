"""
Репозиторий для модуля Comments

Реализует слой доступа к данным для комментариев
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
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from .models import Comment as BaseComment
from ..exceptions import CommentNotFoundError
from .interfaces import CommentRepositoryInterface


class CommentRepository(CommentRepositoryInterface):
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
        has_keywords: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить комментарии по ID группы"""
        group_id_int = int(group_id) if group_id.isdigit() else 0

        # Получаем комментарии по group_vk_id
        from sqlalchemy.orm import joinedload
        from .models import CommentKeywordMatch

        query = (
            select(BaseComment)
            .options(joinedload("keyword_matches").joinedload("keyword"))
            .where(BaseComment.group_vk_id == group_id_int)
        )

        if search_text:
            query = query.where(BaseComment.text.ilike(f"%{search_text}%"))

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        if has_keywords is not None:
            if has_keywords:
                # Показывать только комментарии с ключевыми словами
                # Используем EXISTS для проверки наличия связанных записей
                from .models import CommentKeywordMatch

                subquery = select(CommentKeywordMatch.comment_id).where(
                    CommentKeywordMatch.comment_id == BaseComment.id
                )
                query = query.where(subquery.exists())
            else:
                # Показывать только комментарии без ключевых слов
                from .models import CommentKeywordMatch

                subquery = select(CommentKeywordMatch.comment_id).where(
                    CommentKeywordMatch.comment_id == BaseComment.id
                )
                query = query.where(~subquery.exists())

        query = (
            query.order_by(desc(BaseComment.published_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

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
        return list(result.scalars().unique().all())

    async def get_all_comments(
        self,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить все комментарии с пагинацией"""
        from sqlalchemy.orm import selectinload
        from .models import CommentKeywordMatch

        query = select(BaseComment).options(
            selectinload(BaseComment.keyword_matches).selectinload(
                CommentKeywordMatch.keyword
            )
        )

        if search_text:
            query = query.where(BaseComment.text.ilike(f"%{search_text}%"))

        if is_viewed is not None:
            query = query.where(BaseComment.is_viewed == is_viewed)

        if is_archived is not None:
            query = query.where(BaseComment.is_archived == is_archived)

        if has_keywords is not None:
            if has_keywords:
                # Показывать только комментарии с ключевыми словами
                # Используем EXISTS для проверки наличия связанных записей
                from .models import CommentKeywordMatch

                subquery = select(CommentKeywordMatch.comment_id).where(
                    CommentKeywordMatch.comment_id == BaseComment.id
                )
                query = query.where(subquery.exists())
            else:
                # Показывать только комментарии без ключевых слов
                from .models import CommentKeywordMatch

                subquery = select(CommentKeywordMatch.comment_id).where(
                    CommentKeywordMatch.comment_id == BaseComment.id
                )
                query = query.where(~subquery.exists())

        query = (
            query.order_by(desc(BaseComment.published_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def create(self, comment_data: Dict[str, Any]) -> BaseComment:
        """Создать новый комментарий"""
        # Комментарии не должны создавать посты - это неправильная логика

        # Создаем автора перед созданием комментария
        author_id = comment_data.get("author_id")
        if author_id:
            from ..authors.application.services import AuthorService
            from ..authors.infrastructure.repositories import AuthorRepository

            author_repo = AuthorRepository(self.db)
            author_service = AuthorService(author_repo)
            author_name = comment_data.get("author_name")
            author_screen_name = comment_data.get("author_screen_name")
            author_photo_url = comment_data.get("author_photo_url")

            # Создаем автора и получаем его ID
            author_data = await author_service.get_or_create_author(
                vk_id=author_id,
                author_name=(
                    author_name if isinstance(author_name, str) else None
                ),
                author_screen_name=(
                    author_screen_name
                    if isinstance(author_screen_name, str)
                    else None
                ),
                author_photo_url=(
                    author_photo_url
                    if isinstance(author_photo_url, str)
                    else None
                ),
            )
            # Обновляем author_id на внутренний ID автора
            if "id" in author_data:
                comment_data["author_id"] = author_data["id"]

        try:
            comment = BaseComment(**comment_data)
            self.db.add(comment)
            await self.db.commit()
            await self.db.refresh(comment)
            return comment
        except Exception as e:
            await self.db.rollback()
            raise e

    async def upsert(self, comment_data: Dict[str, Any]) -> BaseComment:
        """
        Создать или обновить комментарий (upsert)

        Проверяет существование комментария по vk_id.
        Если комментарий существует - обновляет его, иначе создает новый.
        """
        vk_id = comment_data.get("vk_id")

        if not vk_id:
            raise ValueError("vk_id обязателен для upsert")

        # Проверяем существование комментария
        existing_comment = await self.get_by_vk_id(vk_id)

        if existing_comment:
            # Обрабатываем author_id отдельно, если он есть в comment_data
            if "author_id" in comment_data:
                author_id = comment_data.pop("author_id")
                if author_id:
                    from ..authors.application.services import AuthorService
                    from ..authors.infrastructure.repositories import AuthorRepository

                    author_repo = AuthorRepository(self.db)
                    author_service = AuthorService(author_repo)

                    # Получаем или создаем автора
                    author_data = await author_service.get_or_create_author(
                        vk_id=author_id,
                        author_name=comment_data.get("author_name"),
                        author_screen_name=comment_data.get(
                            "author_screen_name"
                        ),
                        author_photo_url=comment_data.get("author_photo_url"),
                    )
                    # Устанавливаем внутренний ID автора
                    if "id" in author_data:
                        comment_data["author_id"] = author_data["id"]

            # Обновляем существующий комментарий
            for key, value in comment_data.items():
                if hasattr(existing_comment, key) and key not in [
                    "id",
                    "created_at",
                ]:
                    setattr(existing_comment, key, value)

            # Обновляем время изменения
            setattr(existing_comment, "updated_at", datetime.utcnow())

            try:
                await self.db.commit()
                await self.db.refresh(existing_comment)
                return existing_comment
            except Exception as e:
                await self.db.rollback()
                raise e
        else:
            # Создаем новый комментарий (создание автора уже включено в create)
            return await self.create(comment_data)

    async def update(
        self, comment_id: int, update_data: Dict[str, Any]
    ) -> BaseComment:
        """Обновить комментарий"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(comment_id)

        # Обрабатываем author_id отдельно, если он есть в update_data
        if "author_id" in update_data:
            author_id = update_data.pop("author_id")
            if author_id:
                from ..authors.application.services import AuthorService
                from ..authors.infrastructure.repositories import AuthorRepository

                author_repo = AuthorRepository(self.db)
                author_service = AuthorService(author_repo)

                # Получаем или создаем автора
                author_data = await author_service.get_or_create_author(
                    vk_id=author_id,
                    author_name=update_data.get("author_name"),
                    author_screen_name=update_data.get("author_screen_name"),
                    author_photo_url=update_data.get("author_photo_url"),
                )
                # Устанавливаем внутренний ID автора
                if "id" in author_data:
                    update_data["author_id"] = author_data["id"]

        for key, value in update_data.items():
            if hasattr(comment, key):
                setattr(comment, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(comment)
            return comment
        except Exception as e:
            await self.db.rollback()
            raise e

    async def delete(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False

        try:
            await self.db.delete(comment)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise e

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
