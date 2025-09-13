"""
Сервис для работы с постами
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import Post, PostRepository
from .schemas import PostCreate, PostUpdate, PostFilter, PostStats, PostBulkUpdate
class NotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PostService:
    """Сервис для работы с постами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PostRepository(db)

    async def create_post(self, post_data: PostCreate) -> Post:
        """Создать пост"""
        # Проверяем, не существует ли уже пост с таким VK ID
        existing = await self.repository.get_by_vk_id(post_data.vk_id)
        if existing:
            raise ValueError(f"Post with VK ID {post_data.vk_id} already exists")
        
        post_dict = post_data.dict()
        return await self.repository.create(post_dict)

    async def get_post(self, post_id: int) -> Post:
        """Получить пост по ID"""
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with ID {post_id} not found")
        return post

    async def get_post_by_vk_id(self, vk_id: int) -> Post:
        """Получить пост по VK ID"""
        post = await self.repository.get_by_vk_id(vk_id)
        if not post:
            raise NotFoundException(f"Post with VK ID {vk_id} not found")
        return post

    async def list_posts(self, filters: PostFilter) -> tuple[List[Post], int]:
        """Получить список постов с фильтрацией"""
        posts = await self.repository.list_posts(
            group_id=filters.group_id,
            author_id=filters.author_id,
            status=filters.status,
            search_text=filters.search_text,
            limit=filters.limit,
            offset=filters.offset,
            order_by=filters.order_by,
            order_direction=filters.order_direction
        )
        
        total = await self.repository.count_posts(
            group_id=filters.group_id,
            author_id=filters.author_id,
            status=filters.status,
            search_text=filters.search_text
        )
        
        return posts, total

    async def update_post(self, post_id: int, update_data: PostUpdate) -> Post:
        """Обновить пост"""
        # Убираем None значения
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise ValueError("No data to update")
        
        post = await self.repository.update(post_id, update_dict)
        if not post:
            raise NotFoundException(f"Post with ID {post_id} not found")
        return post

    async def delete_post(self, post_id: int) -> bool:
        """Удалить пост"""
        return await self.repository.delete(post_id)

    async def upsert_post(self, post_data: PostCreate) -> Post:
        """Создать или обновить пост"""
        post_dict = post_data.dict()
        return await self.repository.upsert(post_dict)

    async def get_post_stats(self) -> PostStats:
        """Получить статистику постов"""
        stats = await self.repository.get_stats()
        return PostStats(**stats)

    async def bulk_update_posts(self, bulk_data: PostBulkUpdate) -> int:
        """Массовое обновление постов"""
        if not bulk_data.update_data:
            raise ValueError("No data to update")
        
        updated_count = 0
        for post_id in bulk_data.post_ids:
            post = await self.repository.update(post_id, bulk_data.update_data)
            if post:
                updated_count += 1
        
        return updated_count

    async def search_posts(self, query: str, limit: int = 50, offset: int = 0) -> tuple[List[Post], int]:
        """Поиск постов по тексту"""
        posts = await self.repository.list_posts(
            search_text=query,
            limit=limit,
            offset=offset
        )
        
        total = await self.repository.count_posts(search_text=query)
        
        return posts, total

    async def get_posts_by_hashtag(self, hashtag: str, limit: int = 50, offset: int = 0) -> tuple[List[Post], int]:
        """Получить посты по хештегу"""
        # Ищем посты, содержащие хештег в списке hashtags
        posts = await self.repository.list_posts(limit=limit, offset=offset)
        
        # Фильтруем по хештегу (это можно оптимизировать через SQL запрос)
        filtered_posts = [post for post in posts if hashtag in post.hashtags]
        
        return filtered_posts, len(filtered_posts)

    async def mark_as_parsed(self, post_id: int) -> bool:
        """Отметить пост как распарсенный"""
        from datetime import datetime
        
        update_data = {
            "is_parsed": True,
            "parsed_at": datetime.utcnow(),
        }
        
        post = await self.repository.update(post_id, update_data)
        return post is not None

    async def get_by_id_with_comments(self, post_id: int) -> Optional[Post]:
        """Получить пост по ID с комментариями"""
        from sqlalchemy.orm import selectinload
        
        query = select(Post).options(selectinload(Post.comments)).where(Post.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
