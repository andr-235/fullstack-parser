"""
Use cases модуля авторов

Бизнес-логика приложения без привязки к инфраструктуре
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..domain.entities import AuthorEntity
from ..domain.interfaces import AuthorRepositoryInterface, AuthorCacheInterface, AuthorTaskQueueInterface
from ..domain.exceptions import AuthorNotFoundError, AuthorValidationError, AuthorAlreadyExistsError


class BaseAuthorUseCase(ABC):
    """Базовый класс для use cases авторов."""

    def __init__(
        self,
        repository: AuthorRepositoryInterface,
        cache: Optional[AuthorCacheInterface] = None,
        task_queue: Optional[AuthorTaskQueueInterface] = None
    ):
        self.repository = repository
        self.cache = cache
        self.task_queue = task_queue

    def _get_cache_key(self, vk_id: int) -> str:
        """Получить ключ кэша для автора."""
        return f"author:vk_id:{vk_id}"

    async def _get_from_cache(self, vk_id: int) -> Optional[AuthorEntity]:
        """Получить автора из кэша."""
        if not self.cache:
            return None
        return await self.cache.get(self._get_cache_key(vk_id))

    async def _set_to_cache(self, author: AuthorEntity, ttl: int = 3600) -> None:
        """Сохранить автора в кэш."""
        if not self.cache:
            return
        await self.cache.set(self._get_cache_key(author.vk_id), author, ttl)

    async def _invalidate_cache(self, vk_id: int) -> None:
        """Инвалидировать кэш автора."""
        if not self.cache:
            return
        await self.cache.delete(self._get_cache_key(vk_id))


class CreateAuthorUseCase(BaseAuthorUseCase):
    """Use case для создания автора."""

    async def execute(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать нового автора."""
        # Валидация обязательных полей
        if "vk_id" not in author_data or not author_data["vk_id"]:
            raise AuthorValidationError("vk_id", "отсутствует", "VK ID обязателен")

        vk_id = author_data["vk_id"]

        # Проверка существования автора
        if await self.repository.exists_by_vk_id(vk_id):
            raise AuthorAlreadyExistsError(vk_id)

        # Создание автора
        author = await self.repository.create(author_data)

        # Сохранение в кэш
        await self._set_to_cache(author)

        # Отправка уведомления
        if self.task_queue:
            await self.task_queue.send_author_created_notification(author)

        return author


class GetAuthorUseCase(BaseAuthorUseCase):
    """Use case для получения автора."""

    async def execute(self, vk_id: int) -> Optional[AuthorEntity]:
        """Получить автора по VK ID."""
        # Попытка получить из кэша
        author = await self._get_from_cache(vk_id)
        if author:
            return author

        # Получение из репозитория
        author = await self.repository.get_by_vk_id(vk_id)
        if not author:
            return None

        # Сохранение в кэш
        await self._set_to_cache(author)

        return author


class UpdateAuthorUseCase(BaseAuthorUseCase):
    """Use case для обновления автора."""

    async def execute(self, vk_id: int, update_data: Dict[str, Any]) -> AuthorEntity:
        """Обновить автора."""
        # Проверка существования автора
        if not await self.repository.exists_by_vk_id(vk_id):
            raise AuthorNotFoundError(vk_id)

        # Обновление автора
        author = await self.repository.update(vk_id, update_data)

        # Инвалидация кэша
        await self._invalidate_cache(vk_id)

        # Сохранение в кэш
        await self._set_to_cache(author)

        # Отправка уведомления
        if self.task_queue:
            await self.task_queue.send_author_updated_notification(author)

        return author


class DeleteAuthorUseCase(BaseAuthorUseCase):
    """Use case для удаления автора."""

    async def execute(self, vk_id: int) -> bool:
        """Удалить автора."""
        # Проверка существования автора
        if not await self.repository.exists_by_vk_id(vk_id):
            return False

        # Удаление автора
        result = await self.repository.delete(vk_id)

        # Инвалидация кэша
        await self._invalidate_cache(vk_id)

        return result


class ListAuthorsUseCase(BaseAuthorUseCase):
    """Use case для получения списка авторов."""

    async def execute(self, limit: int = 100, offset: int = 0) -> List[AuthorEntity]:
        """Получить список авторов."""
        return await self.repository.list_authors(limit, offset)

    async def get_count(self) -> int:
        """Получить общее количество авторов."""
        return await self.repository.count_authors()


class UpsertAuthorUseCase(BaseAuthorUseCase):
    """Use case для upsert операции автора."""

    async def execute(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать или обновить автора."""
        # Валидация обязательных полей
        if "vk_id" not in author_data or not author_data["vk_id"]:
            raise AuthorValidationError("vk_id", "отсутствует", "VK ID обязателен")

        vk_id = author_data["vk_id"]

        # Upsert автора
        author = await self.repository.upsert(author_data)

        # Инвалидация кэша
        await self._invalidate_cache(vk_id)

        # Сохранение в кэш
        await self._set_to_cache(author)

        # Отправка уведомления
        if self.task_queue:
            if await self.repository.exists_by_vk_id(vk_id):
                await self.task_queue.send_author_updated_notification(author)
            else:
                await self.task_queue.send_author_created_notification(author)

        return author


class GetOrCreateAuthorUseCase(BaseAuthorUseCase):
    """Use case для get_or_create операции автора."""

    async def execute(
        self,
        vk_id: int,
        author_name: Optional[str] = None,
        author_screen_name: Optional[str] = None,
        author_photo_url: Optional[str] = None,
    ) -> AuthorEntity:
        """Получить автора или создать его, если не существует."""
        # Попытка получить из кэша
        author = await self._get_from_cache(vk_id)
        if author:
            return author

        # Получение или создание автора
        author = await self.repository.get_or_create(
            vk_id=vk_id,
            author_name=author_name,
            author_screen_name=author_screen_name,
            author_photo_url=author_photo_url,
        )

        # Сохранение в кэш
        await self._set_to_cache(author)

        # Отправка уведомления только для новых авторов
        if self.task_queue and not author.is_updated():
            await self.task_queue.send_author_created_notification(author)

        return author
