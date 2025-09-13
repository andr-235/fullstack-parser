"""
SQLAlchemy модели для модуля Posts
"""

from datetime import datetime
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
    JSON,
    ForeignKey,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src import Base


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
    
    # Дополнительные данные
    attachments: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    hashtags: Mapped[List[str]] = mapped_column(JSON, default=list)
    mentions: Mapped[List[str]] = mapped_column(JSON, default=list)
    post_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Флаги
    is_parsed: Mapped[bool] = mapped_column(Boolean, default=False)
    parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Связи
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Уникальный индекс для vk_id + group_id
    __table_args__ = (
        {"extend_existing": True},
    )


class PostRepository:
    """Репозиторий для работы с постами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Получить пост по ID"""
        query = select(Post).where(Post.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_id: int) -> Optional[Post]:
        """Получить пост по VK ID"""
        query = select(Post).where(Post.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id_and_group(self, vk_id: int, group_id: int) -> Optional[Post]:
        """Получить пост по VK ID и группе"""
        query = select(Post).where(
            and_(Post.vk_id == vk_id, Post.group_id == group_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        group_id: Optional[int] = None,
        author_id: Optional[int] = None,
        status: Optional[str] = None,
        search_text: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[Post]:
        """Получить список постов с фильтрацией"""
        query = select(Post)
        
        if group_id:
            query = query.where(Post.group_id == group_id)
        if author_id:
            query = query.where(Post.author_id == author_id)
        if status:
            query = query.where(Post.status == status)
        if search_text:
            query = query.where(Post.text.ilike(f"%{search_text}%"))
        
        # Сортировка
        order_column = getattr(Post, order_by, Post.created_at)
        if order_direction.lower() == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
        
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, post_data: Dict[str, Any]) -> Post:
        """Создать пост"""
        post = Post(**post_data)
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def upsert(self, post_data: Dict[str, Any]) -> Post:
        """Создать или обновить пост"""
        vk_id = post_data.get("vk_id")
        group_id = post_data.get("group_id")
        
        if not vk_id or not group_id:
            raise ValueError("vk_id и group_id обязательны для upsert")
        
        try:
            return await self.create(post_data)
        except IntegrityError:
            await self.db.rollback()
            existing = await self.get_by_vk_id_and_group(vk_id, group_id)
            if existing:
                # Обновляем существующий пост
                for key, value in post_data.items():
                    if hasattr(existing, key) and key not in ["id", "created_at"]:
                        setattr(existing, key, value)
                await self.db.commit()
                await self.db.refresh(existing)
                return existing
            raise

    async def update(self, post_id: int, update_data: Dict[str, Any]) -> Optional[Post]:
        """Обновить пост"""
        post = await self.get_by_id(post_id)
        if not post:
            return None
        
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
        total_query = select(func.count(Post.id))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Среднее количество лайков
        avg_likes_query = select(func.avg(Post.likes_count))
        avg_likes_result = await self.db.execute(avg_likes_query)
        avg_likes = avg_likes_result.scalar() or 0.0
        
        # Количество распарсенных постов
        parsed_query = select(func.count(Post.id)).where(Post.is_parsed == True)
        parsed_result = await self.db.execute(parsed_query)
        parsed = parsed_result.scalar() or 0
        
        return {
            "total_posts": total,
            "avg_likes_per_post": round(avg_likes, 2),
            "parsed_posts": parsed,
        }

    async def count_posts(
        self,
        group_id: Optional[int] = None,
        author_id: Optional[int] = None,
        status: Optional[str] = None,
        search_text: Optional[str] = None,
    ) -> int:
        """Подсчитать количество постов"""
        query = select(func.count(Post.id))
        
        if group_id:
            query = query.where(Post.group_id == group_id)
        if author_id:
            query = query.where(Post.author_id == author_id)
        if status:
            query = query.where(Post.status == status)
        if search_text:
            query = query.where(Post.text.ilike(f"%{search_text}%"))
        
        result = await self.db.execute(query)
        return result.scalar() or 0


# Функция для создания репозитория
async def get_post_repository(db: AsyncSession) -> PostRepository:
    """Создать репозиторий постов"""
    return PostRepository(db)