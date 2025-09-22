"""
Сервис для работы с постами
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from common.exceptions import NotFoundError
from .models import Post, PostRepository


class PostService:
    """Сервис для работы с постами"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PostRepository(db)

    async def create_post(self, vk_id: int, group_id: int, author_id: int, 
                         text: str, status: str = "published", post_type: str = "text",
                         likes_count: int = 0, comments_count: int = 0, 
                         reposts_count: int = 0, views_count: int = 0) -> Post:
        """Создать пост"""
        existing = await self.repository.get_by_vk_id(vk_id)
        if existing:
            raise ValueError(f"Post with VK ID {vk_id} already exists")

        return await self.repository.create(
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

    async def get_post(self, post_id: int) -> Post:
        """Получить пост по ID"""
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with ID {post_id} not found")
        return post

    async def get_post_by_vk_id(self, vk_id: int) -> Post:
        """Получить пост по VK ID"""
        post = await self.repository.get_by_vk_id(vk_id)
        if not post:
            raise NotFoundError(f"Post with VK ID {vk_id} not found")
        return post

    async def list_posts(self, group_id: int = None, author_id: int = None, 
                        status: str = None, search_text: str = None, 
                        limit: int = 50, offset: int = 0) -> List[Post]:
        """Получить список постов"""
        return await self.repository.list_posts(
            group_id=group_id,
            author_id=author_id,
            status=status,
            search_text=search_text,
            limit=limit,
            offset=offset
        )

    async def update_post(self, post_id: int, **data) -> bool:
        """Обновить пост"""
        return await self.repository.update(post_id, **data)

    async def delete_post(self, post_id: int) -> bool:
        """Удалить пост"""
        return await self.repository.delete(post_id)
