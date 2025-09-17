"""
Unit of Work паттерн для работы с авторами
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import AuthorAlreadyExistsError, AuthorNotFoundError
from .models import Author
from .repository import AuthorRepository
from .schemas import AuthorCreate, AuthorUpdate

logger = logging.getLogger(__name__)


class AuthorUnitOfWork:
    """Unit of Work для операций с авторами"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._repository = None

    @property
    def repository(self) -> AuthorRepository:
        """Ленивая инициализация репозитория"""
        if self._repository is None:
            self._repository = AuthorRepository(self.db)
        return self._repository

    @asynccontextmanager
    async def transaction(self):
        """Контекстный менеджер для транзакций"""
        try:
            yield
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Transaction failed: {e}")
            raise

    async def create_author(self, data: AuthorCreate) -> Author:
        """Создает автора"""
        return await self.repository.create(data)

    async def get_author_by_id(self, author_id: int) -> Optional[Author]:
        """Получает автора по ID"""
        return await self.repository.get_by_id(author_id)

    async def get_author_by_vk_id(self, vk_id: int) -> Optional[Author]:
        """Получает автора по VK ID"""
        return await self.repository.get_by_vk_id(vk_id)

    async def get_author_by_screen_name(self, screen_name: str) -> Optional[Author]:
        """Получает автора по screen name"""
        return await self.repository.get_by_screen_name(screen_name)

    async def update_author(self, author_id: int, data: AuthorUpdate) -> Author:
        """Обновляет автора"""
        return await self.repository.update(author_id, data)

    async def delete_author(self, author_id: int) -> bool:
        """Удаляет автора"""
        return await self.repository.delete(author_id)

    async def get_authors_stats(self) -> dict:
        """Получает статистику авторов"""
        return await self.repository.get_stats()