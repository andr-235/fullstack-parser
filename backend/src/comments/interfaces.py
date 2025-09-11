"""
Интерфейсы для модуля Comments

Определяет абстракции для слоев репозитория и сервиса
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Protocol
from datetime import datetime

from .models import Comment as BaseComment


class CommentRepositoryInterface(ABC):
    """Интерфейс репозитория комментариев"""

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Optional[BaseComment]:
        """Получить комментарий по ID"""
        pass

    @abstractmethod
    async def get_by_vk_id(self, vk_comment_id: str) -> Optional[BaseComment]:
        """Получить комментарий по VK ID"""
        pass

    @abstractmethod
    async def get_by_group_id(
        self,
        group_id: str,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить комментарии по ID группы"""
        pass

    @abstractmethod
    async def get_by_post_id(
        self,
        post_id: str,
        limit: int = 100,
        offset: int = 0,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить комментарии к посту"""
        pass

    @abstractmethod
    async def get_all_comments(
        self,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
    ) -> List[BaseComment]:
        """Получить все комментарии с пагинацией"""
        pass

    @abstractmethod
    async def create(self, comment_data: Dict[str, Any]) -> BaseComment:
        """Создать новый комментарий"""
        pass

    @abstractmethod
    async def upsert(self, comment_data: Dict[str, Any]) -> BaseComment:
        """Создать или обновить комментарий (upsert)"""
        pass

    @abstractmethod
    async def update(
        self, comment_id: int, update_data: Dict[str, Any]
    ) -> BaseComment:
        """Обновить комментарий"""
        pass

    @abstractmethod
    async def delete(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику комментариев"""
        pass

    @abstractmethod
    async def mark_as_viewed(self, comment_id: int) -> bool:
        """Отметить комментарий как просмотренный"""
        pass

    @abstractmethod
    async def bulk_update(
        self, comment_ids: List[int], update_data: Dict[str, Any]
    ) -> int:
        """Массовое обновление комментариев"""
        pass

    @abstractmethod
    async def count_by_group(
        self,
        group_id: str,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев в группе"""
        pass

    @abstractmethod
    async def count_by_post(
        self,
        post_id: str,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев к посту"""
        pass

    @abstractmethod
    async def count_all(
        self,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать общее количество комментариев"""
        pass


class CommentServiceInterface(ABC):
    """Интерфейс сервиса комментариев"""

    @abstractmethod
    async def get_comment(self, comment_id: int) -> Dict[str, Any]:
        """Получить комментарий по ID"""
        pass

    @abstractmethod
    async def get_comments_by_group(
        self,
        group_id: str,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить комментарии группы с пагинацией"""
        pass

    @abstractmethod
    async def get_all_comments(
        self,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить все комментарии с пагинацией"""
        pass

    @abstractmethod
    async def get_comments_by_post(
        self,
        post_id: str,
        limit: int = 100,
        offset: int = 0,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить комментарии к посту"""
        pass

    @abstractmethod
    async def create_comment(
        self, comment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Создать новый комментарий"""
        pass

    @abstractmethod
    async def update_comment(
        self, comment_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить комментарий"""
        pass

    @abstractmethod
    async def delete_comment(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        pass

    @abstractmethod
    async def mark_as_viewed(self, comment_id: int) -> Dict[str, Any]:
        """Отметить комментарий как просмотренный"""
        pass

    @abstractmethod
    async def bulk_mark_as_viewed(
        self, comment_ids: List[int]
    ) -> Dict[str, Any]:
        """Массовое отмечание комментариев как просмотренные"""
        pass

    @abstractmethod
    async def get_group_stats(self, group_id: str) -> Dict[str, Any]:
        """Получить статистику комментариев группы"""
        pass

    @abstractmethod
    async def search_comments(
        self,
        query: str,
        group_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Поиск комментариев по тексту"""
        pass

    @abstractmethod
    async def count_by_group(
        self,
        group_id: str,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев в группе"""
        pass

    @abstractmethod
    async def count_by_post(
        self,
        post_id: str,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев к посту"""
        pass

    @abstractmethod
    async def count_all(
        self,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать общее количество комментариев"""
        pass


class CacheServiceInterface(Protocol):
    """Протокол для сервиса кеширования"""

    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        ...

    async def set(
        self, namespace: str, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Сохранить значение в кеш"""
        ...

    async def delete(self, namespace: str, key: str) -> bool:
        """Удалить значение из кеша"""
        ...


class LoggerInterface(Protocol):
    """Протокол для логгера"""

    def debug(self, message: str) -> None:
        """Логирование отладочной информации"""
        ...

    def info(self, message: str) -> None:
        """Логирование информационных сообщений"""
        ...

    def warning(self, message: str) -> None:
        """Логирование предупреждений"""
        ...

    def error(self, message: str) -> None:
        """Логирование ошибок"""
        ...


# Экспорт интерфейсов
__all__ = [
    "CommentRepositoryInterface",
    "CommentServiceInterface",
    "CacheServiceInterface",
    "LoggerInterface",
]
