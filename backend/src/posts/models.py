"""
SQLAlchemy модели для модуля Posts

Определяет репозиторий и специфические модели для работы с постами VK
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
    Boolean,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..models import Post as BasePost
from ..database import get_db_session
from ..exceptions import PostNotFoundError


class PostRepository:
    """
    Репозиторий для работы с постами VK

    Предоставляет интерфейс для CRUD операций с постами
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, post_id: int) -> Optional[BasePost]:
        """Получить пост по ID"""
        query = select(BasePost).where(BasePost.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_post_id: int) -> Optional[BasePost]:
        """Получить пост по VK ID"""
        query = select(BasePost).where(BasePost.vk_id == vk_post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id_and_group_id(
        self, vk_post_id: int, group_id: int
    ) -> Optional[BasePost]:
        """Получить пост по VK ID и ID группы"""
        query = select(BasePost).where(
            and_(BasePost.vk_id == vk_post_id, BasePost.group_id == group_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_group_id(
        self,
        group_id: int,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_parsed: Optional[bool] = None,
    ) -> List[BasePost]:
        """Получить посты по ID группы"""
        query = select(BasePost).where(BasePost.group_id == group_id)

        if search_text:
            query = query.where(BasePost.text.ilike(f"%{search_text}%"))

        if is_parsed is not None:
            query = query.where(BasePost.is_parsed == is_parsed)

        query = (
            query.order_by(desc(BasePost.published_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_posts(
        self,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_parsed: Optional[bool] = None,
    ) -> List[BasePost]:
        """Получить все посты с пагинацией"""
        query = select(BasePost)

        if search_text:
            query = query.where(BasePost.text.ilike(f"%{search_text}%"))

        if is_parsed is not None:
            query = query.where(BasePost.is_parsed == is_parsed)

        query = (
            query.order_by(desc(BasePost.published_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, post_data: Dict[str, Any]) -> BasePost:
        """Создать новый пост"""
        post = BasePost(**post_data)
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def upsert(self, post_data: Dict[str, Any]) -> BasePost:
        """
        Создать или обновить пост (upsert)

        Использует PostgreSQL INSERT ... ON CONFLICT для атомарного upsert.
        Если пост существует - обновляет его, иначе создает новый.
        """
        vk_id = post_data.get("vk_id")
        group_id = post_data.get("group_id")

        if not vk_id or not group_id:
            raise ValueError("vk_id и group_id обязательны для upsert")

        try:
            # Сначала пытаемся создать новый пост
            return await self.create(post_data)
        except IntegrityError as e:
            # Если это ошибка дублирования ключа, обновляем существующий пост
            if (
                "unique constraint" in str(e).lower()
                or "duplicate key" in str(e).lower()
            ):
                # Откатываем транзакцию после ошибки дублирования
                await self.db.rollback()

                # Получаем существующий пост
                existing_post = await self.get_by_vk_id_and_group_id(
                    vk_id, group_id
                )
                if not existing_post:
                    # Если пост не найден, это странно, но пробрасываем ошибку
                    raise e

                # Обновляем существующий пост
                for key, value in post_data.items():
                    if hasattr(existing_post, key) and key not in [
                        "id",
                        "created_at",
                    ]:
                        # Пропускаем поля, которые не должны обновляться при повторном парсинге
                        if key in ["is_parsed", "parsed_at"]:
                            continue
                        setattr(existing_post, key, value)

                # Обновляем время изменения (updated_at обновляется автоматически)
                await self.db.commit()
                await self.db.refresh(existing_post)
                return existing_post
            else:
                # Если это не ошибка дублирования, пробрасываем её
                raise e
        except SQLAlchemyError as e:
            # Откатываем транзакцию при любой ошибке SQLAlchemy
            await self.db.rollback()
            raise e
        except Exception as e:
            # Откатываем транзакцию при любой другой ошибке
            await self.db.rollback()
            raise e

    async def update(
        self, post_id: int, update_data: Dict[str, Any]
    ) -> BasePost:
        """Обновить пост"""
        post = await self.get_by_id(post_id)
        if not post:
            raise PostNotFoundError(post_id)

        for key, value in update_data.items():
            if hasattr(post, key):
                setattr(post, key, value)

        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete(self, post_id: int) -> bool:
        """Удалить пост"""
        post = await self.get_by_id(post_id)
        if not post:
            return False

        await self.db.delete(post)
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику постов"""
        # Общее количество
        total_query = select(func.count()).select_from(BasePost)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        # Среднее количество лайков
        avg_likes_query = select(func.avg(BasePost.likes_count)).select_from(
            BasePost
        )
        avg_likes_result = await self.db.execute(avg_likes_query)
        avg_likes = avg_likes_result.scalar() or 0.0

        # Количество распарсенных постов
        parsed_query = (
            select(func.count())
            .select_from(BasePost)
            .where(BasePost.is_parsed == True)
        )
        parsed_result = await self.db.execute(parsed_query)
        parsed = parsed_result.scalar() or 0

        return {
            "total_posts": total,
            "avg_likes_per_post": round(avg_likes, 2),
            "parsed_posts": parsed,
        }

    async def mark_as_parsed(self, post_id: int) -> bool:
        """Отметить пост как распарсенный"""
        from datetime import datetime

        update_data = {
            "is_parsed": True,
            "parsed_at": datetime.utcnow(),
        }
        try:
            await self.update(post_id, update_data)
            return True
        except PostNotFoundError:
            return False

    async def bulk_update(
        self, post_ids: List[int], update_data: Dict[str, Any]
    ) -> int:
        """Массовое обновление постов"""
        from sqlalchemy import update
        from datetime import datetime

        # Время обновления добавляется автоматически через onupdate

        query = (
            update(BasePost)
            .where(BasePost.id.in_(post_ids))
            .values(**update_data)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

    async def count_by_group(
        self,
        group_id: int,
        search_text: Optional[str] = None,
        is_parsed: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество постов в группе"""
        query = select(func.count(BasePost.id)).where(
            BasePost.group_id == group_id
        )

        if search_text:
            query = query.where(BasePost.text.ilike(f"%{search_text}%"))

        if is_parsed is not None:
            query = query.where(BasePost.is_parsed == is_parsed)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_all(
        self,
        search_text: Optional[str] = None,
        is_parsed: Optional[bool] = None,
    ) -> int:
        """Подсчитать общее количество постов"""
        query = select(func.count(BasePost.id))

        if search_text:
            query = query.where(BasePost.text.ilike(f"%{search_text}%"))

        if is_parsed is not None:
            query = query.where(BasePost.is_parsed == is_parsed)

        result = await self.db.execute(query)
        return result.scalar() or 0


# Функции для создания репозитория
async def get_post_repository(
    db: AsyncSession,
) -> PostRepository:
    """Создать репозиторий постов"""
    return PostRepository(db)


# Экспорт
__all__ = [
    "PostRepository",
    "get_post_repository",
]
