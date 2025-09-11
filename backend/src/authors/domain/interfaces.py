"""
Интерфейсы доменного слоя модуля авторов

Абстракции для репозиториев и сервисов
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .entities import AuthorEntity


class AuthorRepositoryInterface(ABC):
    """Интерфейс репозитория авторов."""

    @abstractmethod
    async def get_by_vk_id(self, vk_id: int) -> Optional[AuthorEntity]:
        """Получить автора по VK ID."""

    @abstractmethod
    async def get_by_id(self, author_id: int) -> Optional[AuthorEntity]:
        """Получить автора по внутреннему ID."""

    @abstractmethod
    async def create(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать нового автора."""

    @abstractmethod
    async def update(self, vk_id: int, update_data: Dict[str, Any]) -> AuthorEntity:
        """Обновить автора."""

    @abstractmethod
    async def upsert(self, author_data: Dict[str, Any]) -> AuthorEntity:
        """Создать или обновить автора."""

    @abstractmethod
    async def get_or_create(
        self,
        vk_id: int,
        author_name: Optional[str] = None,
        author_screen_name: Optional[str] = None,
        author_photo_url: Optional[str] = None,
    ) -> AuthorEntity:
        """Получить автора или создать его, если не существует."""

    @abstractmethod
    async def delete(self, vk_id: int) -> bool:
        """Удалить автора."""

    @abstractmethod
    async def list_authors(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[AuthorEntity]:
        """Получить список авторов."""

    @abstractmethod
    async def count_authors(self) -> int:
        """Получить общее количество авторов."""

    @abstractmethod
    async def exists_by_vk_id(self, vk_id: int) -> bool:
        """Проверить существование автора по VK ID."""

    @abstractmethod
    async def get_author_comments_count(self, vk_id: int) -> int:
        """Получить количество комментариев автора."""

    @abstractmethod
    async def get_authors_with_comments_stats(
        self, 
        limit: int = 100, 
        offset: int = 0,
        min_comments: int = 0
    ) -> List[AuthorEntity]:
        """Получить авторов со статистикой комментариев."""


class AuthorCacheInterface(ABC):
    """Интерфейс кэша авторов."""

    @abstractmethod
    async def get(self, key: str) -> Optional[AuthorEntity]:
        """Получить автора из кэша."""

    @abstractmethod
    async def set(self, key: str, author: AuthorEntity, ttl: int = 3600) -> None:
        """Сохранить автора в кэш."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удалить автора из кэша."""

    @abstractmethod
    async def invalidate_pattern(self, pattern: str) -> None:
        """Инвалидировать кэш по паттерну."""


class AuthorTaskQueueInterface(ABC):
    """Интерфейс очереди задач для авторов."""

    @abstractmethod
    async def send_author_created_notification(self, author: AuthorEntity) -> None:
        """Отправить уведомление о создании автора."""

    @abstractmethod
    async def send_author_updated_notification(self, author: AuthorEntity) -> None:
        """Отправить уведомление об обновлении автора."""

    @abstractmethod
    async def schedule_author_photo_update(self, vk_id: int) -> None:
        """Запланировать обновление фото автора."""

    @abstractmethod
    async def schedule_author_data_sync(self, vk_id: int) -> None:
        """Запланировать синхронизацию данных автора с VK API."""
