"""
Репозиторий авторов - инфраструктурный слой

Реализация интерфейса репозитория с использованием SQLAlchemy 2.0 async
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from ..domain.entities import AuthorEntity
from ..domain.interfaces import AuthorRepositoryInterface
from ..domain.exceptions import AuthorNotFoundError
from .models import Author

logger = logging.getLogger(__name__)


class AuthorRepository(AuthorRepositoryInterface):
    """Репозиторий для работы с авторами VK."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_vk_id(self, vk_id: int) -> Optional[AuthorEntity]:
        """Получить автора по VK ID."""
        try:
            from sqlalchemy.orm import selectinload
            stmt = select(Author).options(selectinload(Author.comments)).where(Author.vk_id == vk_id)
            result = await self.db.execute(stmt)
            author_orm = result.scalar_one_or_none()
            
            if not author_orm:
                return None
                
            return self._orm_to_entity(author_orm)
        except Exception as e:
            logger.error(f"Error getting author by VK ID {vk_id}: {e}")
            raise

    async def get_by_id(self, author_id: int) -> Optional[AuthorEntity]:
        """Получить автора по внутреннему ID."""
        try:
            from sqlalchemy.orm import selectinload
            stmt = select(Author).options(selectinload(Author.comments)).where(Author.id == author_id)
            result = await self.db.execute(stmt)
            author_orm = result.scalar_one_or_none()
            
            if not author_orm:
                return None
                
            return self._orm_to_entity(author_orm)
        except Exception as e:
            logger.error(f"Error getting author by ID {author_id}: {e}")
            raise

    async def create(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать нового автора."""
        try:
            author_orm = Author(
                vk_id=author_data["vk_id"],
                first_name=author_data.get("first_name"),
                last_name=author_data.get("last_name"),
                screen_name=author_data.get("screen_name"),
                photo_url=author_data.get("photo_url"),
            )

            self.db.add(author_orm)
            await self.db.commit()
            await self.db.refresh(author_orm)
            
            return self._orm_to_entity(author_orm)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating author: {e}")
            raise

    async def update(self, vk_id: int, update_data: Dict[str, Any]) -> AuthorEntity:
        """Обновить автора."""
        try:
            # Получаем автора
            author_orm = await self.get_by_vk_id_orm(vk_id)
            if not author_orm:
                raise AuthorNotFoundError(vk_id)

            # Обновляем поля
            for key, value in update_data.items():
                if hasattr(author_orm, key) and key not in ["id", "created_at"]:
                    setattr(author_orm, key, value)

            # Обновляем время изменения
            author_orm.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(author_orm)
            
            return self._orm_to_entity(author_orm)
        except AuthorNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating author {vk_id}: {e}")
            raise

    async def upsert(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать или обновить автора."""
        try:
            vk_id = author_data["vk_id"]
            
            # Проверяем существование автора
            existing_author = await self.get_by_vk_id_orm(vk_id)
            
            if existing_author:
                # Обновляем существующего автора
                for key, value in author_data.items():
                    if hasattr(existing_author, key) and key not in ["id", "created_at"]:
                        setattr(existing_author, key, value)
                
                existing_author.updated_at = datetime.utcnow()
                await self.db.commit()
                await self.db.refresh(existing_author)
                return self._orm_to_entity(existing_author)
            else:
                # Создаем нового автора
                return await self.create(author_data)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error upserting author: {e}")
            raise

    async def get_or_create(
        self,
        vk_id: int,
        author_name: Optional[str] = None,
        author_screen_name: Optional[str] = None,
        author_photo_url: Optional[str] = None,
    ) -> AuthorEntity:
        """Получить автора или создать его, если не существует."""
        try:
            # Сначала пытаемся найти существующего автора
            author = await self.get_by_vk_id(vk_id)
            if author:
                return author

            # Если автора нет, создаем нового
            author_data = {
                "vk_id": vk_id,
                "first_name": author_name or str(vk_id),
                "last_name": None,
                "screen_name": author_screen_name,
                "photo_url": author_photo_url,
            }

            return await self.create(author_data)
        except Exception as e:
            logger.error(f"Error getting or creating author {vk_id}: {e}")
            raise

    async def delete(self, vk_id: int) -> bool:
        """Удалить автора."""
        try:
            author_orm = await self.get_by_vk_id_orm(vk_id)
            if not author_orm:
                return False

            await self.db.delete(author_orm)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting author {vk_id}: {e}")
            raise

    async def list_authors(self, limit: int = 100, offset: int = 0) -> List[AuthorEntity]:
        """Получить список авторов."""
        try:
            from sqlalchemy.orm import selectinload
            stmt = (
                select(Author)
                .options(selectinload(Author.comments))
                .limit(limit)
                .offset(offset)
                .order_by(Author.vk_id)
            )
            result = await self.db.execute(stmt)
            authors_orm = result.scalars().all()
            
            return [self._orm_to_entity(author_orm) for author_orm in authors_orm]
        except Exception as e:
            logger.error(f"Error listing authors: {e}")
            raise

    async def count_authors(self) -> int:
        """Получить общее количество авторов."""
        try:
            stmt = select(func.count(Author.id))
            result = await self.db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error counting authors: {e}")
            raise

    async def exists_by_vk_id(self, vk_id: int) -> bool:
        """Проверить существование автора по VK ID."""
        try:
            stmt = select(Author.id).where(Author.vk_id == vk_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking author existence {vk_id}: {e}")
            raise

    async def get_author_comments_count(self, vk_id: int) -> int:
        """Получить количество комментариев автора."""
        try:
            from sqlalchemy import func
            from ...comments.models import Comment
            
            stmt = (
                select(func.count(Comment.id))
                .join(Author, Comment.author_id == Author.id)
                .where(Author.vk_id == vk_id)
            )
            result = await self.db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting comments count for author {vk_id}: {e}")
            raise

    async def get_authors_with_comments_stats(
        self, 
        limit: int = 100, 
        offset: int = 0,
        min_comments: int = 0
    ) -> List[AuthorEntity]:
        """Получить авторов со статистикой комментариев."""
        try:
            from sqlalchemy.orm import selectinload
            from sqlalchemy import func
            from ...comments.models import Comment
            
            # Подзапрос для подсчета комментариев
            comments_subquery = (
                select(
                    Comment.author_id,
                    func.count(Comment.id).label('comments_count')
                )
                .group_by(Comment.author_id)
                .having(func.count(Comment.id) >= min_comments)
                .subquery()
            )
            
            stmt = (
                select(Author)
                .options(selectinload(Author.comments))
                .join(comments_subquery, Author.id == comments_subquery.c.author_id)
                .limit(limit)
                .offset(offset)
                .order_by(comments_subquery.c.comments_count.desc())
            )
            
            result = await self.db.execute(stmt)
            authors_orm = result.scalars().all()
            
            return [self._orm_to_entity(author_orm) for author_orm in authors_orm]
        except Exception as e:
            logger.error(f"Error getting authors with comments stats: {e}")
            raise

    async def get_by_vk_id_orm(self, vk_id: int) -> Optional[Author]:
        """Получить ORM объект автора по VK ID (внутренний метод)."""
        try:
            stmt = select(Author).where(Author.vk_id == vk_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting author ORM by VK ID {vk_id}: {e}")
            raise

    def _orm_to_entity(self, author_orm: Author) -> AuthorEntity:
        """Преобразовать ORM объект в доменную сущность."""
        # Подсчитываем количество комментариев
        comments_count = len(author_orm.comments) if hasattr(author_orm, 'comments') and author_orm.comments else 0
        
        return AuthorEntity(
            id=author_orm.id,
            vk_id=author_orm.vk_id,
            first_name=author_orm.first_name,
            last_name=author_orm.last_name,
            screen_name=author_orm.screen_name,
            photo_url=author_orm.photo_url,
            created_at=author_orm.created_at,
            updated_at=author_orm.updated_at,
            comments_count=comments_count,
        )
