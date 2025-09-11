"""
Сервисы приложения модуля авторов

Оркестрация use cases и бизнес-логика
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
import logging

from ..domain.entities import AuthorEntity
from ..domain.interfaces import AuthorRepositoryInterface, AuthorCacheInterface, AuthorTaskQueueInterface
from ..domain.exceptions import AuthorNotFoundError, AuthorValidationError
from .use_cases import (
    CreateAuthorUseCase,
    GetAuthorUseCase,
    UpdateAuthorUseCase,
    DeleteAuthorUseCase,
    ListAuthorsUseCase,
    UpsertAuthorUseCase,
    GetOrCreateAuthorUseCase
)

logger = logging.getLogger(__name__)


class AuthorService:
    """Сервис для работы с авторами VK."""

    def __init__(
        self,
        repository: AuthorRepositoryInterface,
        cache: Optional[AuthorCacheInterface] = None,
        task_queue: Optional[AuthorTaskQueueInterface] = None
    ):
        self.repository = repository
        self.cache = cache
        self.task_queue = task_queue

        # Инициализация use cases
        self._create_use_case = CreateAuthorUseCase(repository, cache, task_queue)
        self._get_use_case = GetAuthorUseCase(repository, cache, task_queue)
        self._update_use_case = UpdateAuthorUseCase(repository, cache, task_queue)
        self._delete_use_case = DeleteAuthorUseCase(repository, cache, task_queue)
        self._list_use_case = ListAuthorsUseCase(repository, cache, task_queue)
        self._upsert_use_case = UpsertAuthorUseCase(repository, cache, task_queue)
        self._get_or_create_use_case = GetOrCreateAuthorUseCase(repository, cache, task_queue)

    async def create_author(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать нового автора."""
        logger.info(f"Creating author with VK ID: {author_data.get('vk_id')}")
        
        try:
            return await self._create_use_case.execute(author_data)
        except Exception as e:
            logger.error(f"Failed to create author: {e}")
            raise

    async def get_author(self, vk_id: int) -> Optional[AuthorEntity]:
        """Получить автора по VK ID."""
        logger.debug(f"Getting author with VK ID: {vk_id}")
        
        try:
            return await self._get_use_case.execute(vk_id)
        except Exception as e:
            logger.error(f"Failed to get author {vk_id}: {e}")
            raise

    async def update_author(self, vk_id: int, update_data: Dict[str, Any]) -> AuthorEntity:
        """Обновить автора."""
        logger.info(f"Updating author with VK ID: {vk_id}")
        
        try:
            return await self._update_use_case.execute(vk_id, update_data)
        except AuthorNotFoundError:
            logger.warning(f"Author {vk_id} not found for update")
            raise
        except Exception as e:
            logger.error(f"Failed to update author {vk_id}: {e}")
            raise

    async def delete_author(self, vk_id: int) -> bool:
        """Удалить автора."""
        logger.info(f"Deleting author with VK ID: {vk_id}")
        
        try:
            return await self._delete_use_case.execute(vk_id)
        except Exception as e:
            logger.error(f"Failed to delete author {vk_id}: {e}")
            raise

    async def list_authors(self, limit: int = 100, offset: int = 0) -> List[AuthorEntity]:
        """Получить список авторов."""
        logger.debug(f"Listing authors: limit={limit}, offset={offset}")
        
        try:
            return await self._list_use_case.execute(limit, offset)
        except Exception as e:
            logger.error(f"Failed to list authors: {e}")
            raise

    async def get_authors_count(self) -> int:
        """Получить общее количество авторов."""
        logger.debug("Getting authors count")
        
        try:
            return await self._list_use_case.get_count()
        except Exception as e:
            logger.error(f"Failed to get authors count: {e}")
            raise

    async def upsert_author(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать или обновить автора."""
        logger.info(f"Upserting author with VK ID: {author_data.get('vk_id')}")
        
        try:
            return await self._upsert_use_case.execute(author_data)
        except Exception as e:
            logger.error(f"Failed to upsert author: {e}")
            raise

    async def get_or_create_author(
        self,
        vk_id: int,
        author_name: Optional[str] = None,
        author_screen_name: Optional[str] = None,
        author_photo_url: Optional[str] = None,
    ) -> AuthorEntity:
        """Получить автора или создать его, если не существует."""
        logger.info(f"Get or create author with VK ID: {vk_id}")
        
        try:
            return await self._get_or_create_use_case.execute(
                vk_id=vk_id,
                author_name=author_name,
                author_screen_name=author_screen_name,
                author_photo_url=author_photo_url,
            )
        except Exception as e:
            logger.error(f"Failed to get or create author {vk_id}: {e}")
            raise

    async def bulk_create_authors(self, authors_data: List[Dict[str, Any]]) -> List[AuthorEntity]:
        """Массовое создание авторов."""
        logger.info(f"Bulk creating {len(authors_data)} authors")
        
        created_authors = []
        errors = []

        for author_data in authors_data:
            try:
                author = await self.create_author(author_data)
                created_authors.append(author)
            except Exception as e:
                logger.error(f"Failed to create author {author_data.get('vk_id')}: {e}")
                errors.append({
                    "vk_id": author_data.get('vk_id'),
                    "error": str(e)
                })

        if errors:
            logger.warning(f"Bulk create completed with {len(errors)} errors")
            # Можно добавить отправку ошибок в очередь задач

        return created_authors

    async def search_authors(self, query: str, limit: int = 100) -> List[AuthorEntity]:
        """Поиск авторов по имени или screen_name."""
        logger.debug(f"Searching authors with query: {query}")
        
        # Простая реализация поиска
        # В реальном проекте лучше использовать полнотекстовый поиск
        all_authors = await self.list_authors(limit=1000)  # Ограничиваем для простоты
        
        query_lower = query.lower()
        filtered_authors = [
            author for author in all_authors
            if (
                (author.first_name and query_lower in author.first_name.lower()) or
                (author.last_name and query_lower in author.last_name.lower()) or
                (author.screen_name and query_lower in author.screen_name.lower())
            )
        ]
        
        return filtered_authors[:limit]

    async def get_author_comments_count(self, vk_id: int) -> int:
        """Получить количество комментариев автора."""
        logger.debug(f"Getting comments count for author {vk_id}")
        
        try:
            return await self.repository.get_author_comments_count(vk_id)
        except Exception as e:
            logger.error(f"Failed to get comments count for author {vk_id}: {e}")
            raise

    async def get_authors_with_comments_stats(
        self, 
        limit: int = 100, 
        offset: int = 0,
        min_comments: int = 0
    ) -> List[AuthorEntity]:
        """Получить авторов со статистикой комментариев."""
        logger.debug(f"Getting authors with comments stats: min_comments={min_comments}")
        
        try:
            return await self.repository.get_authors_with_comments_stats(
                limit=limit,
                offset=offset,
                min_comments=min_comments
            )
        except Exception as e:
            logger.error(f"Failed to get authors with comments stats: {e}")
            raise

    async def get_top_authors_by_comments(
        self, 
        limit: int = 10,
        min_comments: int = 1
    ) -> List[AuthorEntity]:
        """Получить топ авторов по количеству комментариев."""
        logger.info(f"Getting top {limit} authors by comments (min: {min_comments})")
        
        try:
            return await self.repository.get_authors_with_comments_stats(
                limit=limit,
                offset=0,
                min_comments=min_comments
            )
        except Exception as e:
            logger.error(f"Failed to get top authors by comments: {e}")
            raise
