"""
Сервис для работы с авторами - рефакторинг с использованием Unit of Work паттерна
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import AuthorAlreadyExistsError, AuthorNotFoundError
from .schemas import (
    AuthorCreate,
    AuthorResponse,
    AuthorUpdate,
)
from .unit_of_work import AuthorUnitOfWork

logger = logging.getLogger(__name__)


class AuthorService:
    """Сервис для работы с авторами с использованием Unit of Work паттерна"""

    def __init__(self, db: AsyncSession):
        self.uow = AuthorUnitOfWork(db)

    async def create_author(self, data: AuthorCreate) -> AuthorResponse:
        """
        Создает нового автора в системе.

        Выполняет создание автора с использованием Unit of Work паттерна,
        обеспечивая транзакционность и обработку бизнес-логики.

        Args:
            data: Данные для создания автора, прошедшие валидацию.

        Returns:
            AuthorResponse: Созданный автор с полными данными.

        Raises:
            AuthorAlreadyExistsError: Если автор с таким VK ID уже существует.
            AuthorValidationError: Если данные не проходят бизнес-валидацию.
            Exception: При других ошибках создания.

        Examples:
            >>> service = AuthorService(db_session)
            >>> author_data = AuthorCreate(vk_id=123, first_name="Иван")
            >>> author = await service.create_author(author_data)
            >>> print(author.id)
            1
        """
        try:
            async with self.uow.transaction():
                author = await self.uow.create_author(data)
                logger.info(f"Created author: ID={author.id}, VK ID={author.vk_id}")
                return AuthorResponse.model_validate(author)
        except AuthorAlreadyExistsError:
            raise
        except Exception as e:
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
        author = await self.uow.get_author_by_id(author_id)
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
        author = await self.uow.get_author_by_vk_id(vk_id)
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
        author = await self.uow.get_author_by_screen_name(screen_name)
        return AuthorResponse.model_validate(author) if author else None

    async def update_author(self, author_id: int, data: AuthorUpdate) -> AuthorResponse:
        """Обновляет автора"""
        try:
            async with self.uow.transaction():
                author = await self.uow.update_author(author_id, data)
                logger.info(f"Updated author: ID={author_id}")
                return AuthorResponse.model_validate(author)
        except AuthorNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update author {author_id}: {e}")
            raise

    async def delete_author(self, author_id: int) -> None:
        """Удаляет автора"""
        try:
            async with self.uow.transaction():
                result = await self.uow.delete_author(author_id)
                if result:
                    logger.info(f"Deleted author: ID={author_id}")
        except AuthorNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete author {author_id}: {e}")
            raise

    async def get_stats(self) -> dict:
        """Получает статистику авторов"""
        return await self.uow.get_authors_stats()