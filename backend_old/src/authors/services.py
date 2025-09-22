"""
Сервис для работы с авторами - упрощенная версия с прямым доступом к SQLAlchemy

Убрана зависимость от Unit of Work паттерна, логика repository интегрирована напрямую.
Сервис работает непосредственно с базой данных через SQLAlchemy.
"""

import json
import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import AuthorAlreadyExistsError, AuthorNotFoundError
from .models import AuthorModel
from .schemas import (
    AuthorCreate,
    AuthorResponse,
    AuthorUpdate,
)

logger = logging.getLogger(__name__)


class AuthorService:
    """Сервис для работы с авторами с прямым доступом к SQLAlchemy"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_author(self, data: AuthorCreate) -> AuthorResponse:
        """
        Создает нового автора в системе.

        Выполняет создание автора с проверкой на дублирование VK ID,
        обеспечивает транзакционность и обработку бизнес-логики.

        Args:
            data: Данные для создания автора, прошедшие валидацию.

        Returns:
            AuthorResponse: Созданный автор с полными данными.

        Raises:
            AuthorAlreadyExistsError: Если автор с таким VK ID уже существует.
            Exception: При других ошибках создания.

        Examples:
            >>> service = AuthorService(db_session)
            >>> author_data = AuthorCreate(vk_id=123, first_name="Иван")
            >>> author = await service.create_author(author_data)
            >>> print(author.id)
            1
        """
        try:
            # Проверяем, не существует ли уже автор с таким VK ID
            existing = await self._get_by_vk_id(data.vk_id)
            if existing:
                raise AuthorAlreadyExistsError(data.vk_id)

            # Создаем автора
            author_dict = data.model_dump()
            if author_dict.get('metadata'):
                author_dict['author_metadata'] = json.dumps(author_dict.pop('metadata'))

            author = AuthorModel(**author_dict)
            self.db.add(author)
            await self.db.commit()
            await self.db.refresh(author)

            logger.info(f"Created author: ID={author.id}, VK ID={author.vk_id}")
            return AuthorResponse.model_validate(author)
        except AuthorAlreadyExistsError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create author: {e}")
            raise

    async def get_by_id(self, author_id: int) -> Optional[AuthorResponse]:
        """
        Получает автора по его уникальному идентификатору.

        Args:
            author_id: Уникальный идентификатор автора в базе данных.

        Returns:
            Optional[AuthorResponse]: Данные автора или None, если автор не найден.

        Examples:
            >>> service = AuthorService(db_session)
            >>> author = await service.get_by_id(1)
            >>> print(author.first_name if author else "Not found")
            Иван
        """
        author = await self._get_by_id(author_id)
        return AuthorResponse.model_validate(author) if author else None

    async def get_by_vk_id(self, vk_id: int) -> Optional[AuthorResponse]:
        """
        Получает автора по его VK ID.

        Args:
            vk_id: Уникальный идентификатор автора в VK.

        Returns:
            Optional[AuthorResponse]: Данные автора или None, если автор не найден.

        Examples:
            >>> service = AuthorService(db_session)
            >>> author = await service.get_by_vk_id(123456)
            >>> print(author.screen_name if author else "Not found")
            ivanov
        """
        author = await self._get_by_vk_id(vk_id)
        return AuthorResponse.model_validate(author) if author else None

    async def get_by_screen_name(self, screen_name: str) -> Optional[AuthorResponse]:
        """
        Получает автора по его screen name.

        Args:
            screen_name: Уникальное имя автора (screen name) в системе.

        Returns:
            Optional[AuthorResponse]: Данные автора или None, если автор не найден.

        Examples:
            >>> service = AuthorService(db_session)
            >>> author = await service.get_by_screen_name("ivanov")
            >>> print(author.vk_id if author else "Not found")
            123456
        """
        author = await self._get_by_screen_name(screen_name)
        return AuthorResponse.model_validate(author) if author else None

    async def update_author(self, author_id: int, data: AuthorUpdate) -> AuthorResponse:
        """Обновляет автора"""
        try:
            author = await self._get_by_id(author_id)
            if not author:
                raise AuthorNotFoundError(author_id=author_id)

            # Подготавливаем данные для обновления
            update_dict = data.model_dump(exclude_unset=True)
            if update_dict.get('metadata'):
                update_dict['author_metadata'] = json.dumps(update_dict.pop('metadata'))

            # Обновляем поля
            for field, value in update_dict.items():
                setattr(author, field, value)

            await self.db.commit()
            await self.db.refresh(author)

            logger.info(f"Updated author: ID={author_id}")
            return AuthorResponse.model_validate(author)
        except AuthorNotFoundError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update author {author_id}: {e}")
            raise

    async def delete_author(self, author_id: int) -> None:
        """Удаляет автора"""
        try:
            author = await self._get_by_id(author_id)
            if not author:
                raise AuthorNotFoundError(author_id=author_id)

            await self.db.delete(author)
            await self.db.commit()

            logger.info(f"Deleted author: ID={author_id}")
        except AuthorNotFoundError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete author {author_id}: {e}")
            raise

    async def get_stats(self) -> dict:
        """Получает статистику авторов"""
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

    # Вспомогательные методы для работы с базой данных
    async def _get_by_id(self, author_id: int) -> Optional[AuthorModel]:
        """Получить автора по ID"""
        query = select(AuthorModel).where(AuthorModel.id == author_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_by_vk_id(self, vk_id: int) -> Optional[AuthorModel]:
        """Получить автора по VK ID"""
        query = select(AuthorModel).where(AuthorModel.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_by_screen_name(self, screen_name: str) -> Optional[AuthorModel]:
        """Получить автора по screen name"""
        query = select(AuthorModel).where(AuthorModel.screen_name == screen_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()