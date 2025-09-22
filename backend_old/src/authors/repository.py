"""
Репозиторий для работы с авторами
"""

import asyncio
import json
import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .exceptions import AuthorAlreadyExistsError, AuthorNotFoundError
from .models import AuthorModel
from .schemas import AuthorCreate, AuthorUpdate

logger = logging.getLogger(__name__)

# Константы для таймаутов и retry
DB_OPERATION_TIMEOUT = 10.0  # секунды
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_MULTIPLIER = 1.0


class AuthorRepository:
  """
  Репозиторий для работы с авторами.

  Предоставляет методы для CRUD операций с авторами,
  включая обработку конкурентного доступа и транзакций.
  """

  def __init__(self, db: AsyncSession):
    """
    Инициализация репозитория.

    Args:
      db: Асинхронная сессия базы данных SQLAlchemy.
    """
    self.db = db

    async def get_by_id(self, author_id: int) -> Optional[AuthorModel]:
        """Получить автора по ID"""
        query = select(AuthorModel).where(AuthorModel.id == author_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_id: int) -> Optional[AuthorModel]:
        """Получить автора по VK ID"""
        query = select(AuthorModel).where(AuthorModel.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_screen_name(self, screen_name: str) -> Optional[AuthorModel]:
        """Получить автора по screen name"""
        query = select(AuthorModel).where(AuthorModel.screen_name == screen_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, author_data: AuthorCreate) -> AuthorModel:
        """Создать нового автора"""
        # Проверяем, не существует ли уже автор с таким VK ID
        existing = await self.get_by_vk_id(author_data.vk_id)
        if existing:
            raise AuthorAlreadyExistsError(author_data.vk_id)

        # Создаем автора
        author_dict = author_data.model_dump()
        if author_dict.get('metadata'):
            author_dict['author_metadata'] = json.dumps(author_dict.pop('metadata'))

        author = AuthorModel(**author_dict)
        self.db.add(author)
        return author

    async def update(self, author_id: int, update_data: AuthorUpdate) -> AuthorModel:
        """Обновить автора"""
        author = await self.get_by_id(author_id)
        if not author:
            raise AuthorNotFoundError(author_id=author_id)

        # Подготавливаем данные для обновления
        update_dict = update_data.model_dump(exclude_unset=True)
        if update_dict.get('metadata'):
            update_dict['author_metadata'] = json.dumps(update_dict.pop('metadata'))

        # Обновляем поля
        for field, value in update_dict.items():
            setattr(author, field, value)

        return author

    async def delete(self, author_id: int) -> bool:
        """Удалить автора"""
        author = await self.get_by_id(author_id)
        if not author:
            raise AuthorNotFoundError(author_id=author_id)

        await self.db.delete(author)
        return True

    async def get_stats(self) -> dict:
        """Получить статистику авторов"""
        # Общее количество
        total_result = await self.db.execute(select(func.count(AuthorModel.id)))
        total = total_result.scalar()

        # По статусам
        status_result = await self.db.execute(
            select(AuthorModel.status, func.count(AuthorModel.id))
            .group_by(AuthorModel.status)
        )
        status_stats = {status: count for status, count in status_result.fetchall()}

        # Верифицированные
        verified_result = await self.db.execute(
            select(func.count(AuthorModel.id)).where(AuthorModel.is_verified == True)
        )
        verified_count = verified_result.scalar()

        # Закрытые профили
        closed_result = await self.db.execute(
            select(func.count(AuthorModel.id)).where(AuthorModel.is_closed == True)
        )
        closed_count = closed_result.scalar()

        return {
            "total": total,
            "by_status": status_stats,
            "verified": verified_count,
            "closed": closed_count
        }