"""
SQLAlchemy модели для модуля Posts
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.database import Base

if TYPE_CHECKING:
    from comments.models import Comment


class Post(Base):
    """Модель поста VK"""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vk_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    group_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="published")
    post_type: Mapped[str] = mapped_column(String(20), default="text")

    # Статистика
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    reposts_count: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)

    # Временные метки
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    comments = relationship("Comment", back_populates="post", lazy="select")


class PostRepository:
    """Репозиторий для работы с постами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Получить пост по ID"""
        from sqlalchemy import select
        result = await self.db.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_id: int) -> Optional[Post]:
        """Получить пост по VK ID"""
        from sqlalchemy import select
        result = await self.db.execute(select(Post).where(Post.vk_id == vk_id))
        return result.scalar_one_or_none()

    async def list_posts(self, group_id: int = None, author_id: int = None, 
                        status: str = None, search_text: str = None, 
                        limit: int = 50, offset: int = 0) -> list[Post]:
        """Получить список постов"""
        from sqlalchemy import select, and_, desc
        
        query = select(Post)
        conditions = []
        
        if group_id:
            conditions.append(Post.group_id == group_id)
        if author_id:
            conditions.append(Post.author_id == author_id)
        if status:
            conditions.append(Post.status == status)
        if search_text:
            conditions.append(Post.text.ilike(f"%{search_text}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(Post.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, vk_id: int, group_id: int, author_id: int, 
                    text: str, status: str = "published", post_type: str = "text",
                    likes_count: int = 0, comments_count: int = 0, 
                    reposts_count: int = 0, views_count: int = 0) -> Post:
        """Создать пост"""
        post = Post(
            vk_id=vk_id,
            group_id=group_id,
            author_id=author_id,
            text=text,
            status=status,
            post_type=post_type,
            likes_count=likes_count,
            comments_count=comments_count,
            reposts_count=reposts_count,
            views_count=views_count
        )
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def update(self, post_id: int, **data) -> bool:
        """Обновить пост"""
        post = await self.get_by_id(post_id)
        if not post:
            return False

        for field, value in data.items():
            if hasattr(post, field) and field not in ["id", "created_at"]:
                setattr(post, field, value)

        await self.db.commit()
        return True

    async def delete(self, post_id: int) -> bool:
        """Удалить пост"""
        post = await self.get_by_id(post_id)
        if not post:
            return False

        await self.db.delete(post)
        await self.db.commit()
        return True
