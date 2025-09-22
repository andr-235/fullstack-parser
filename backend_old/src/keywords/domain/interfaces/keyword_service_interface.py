"""
Интерфейс сервиса для работы с ключевыми словами
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.keywords.domain.entities.keyword import Keyword


class KeywordServiceInterface(ABC):
    """Интерфейс сервиса ключевых слов"""

    @abstractmethod
    async def create_keyword(
        self,
        word: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        group_id: Optional[int] = None,
    ) -> Keyword:
        """Создать ключевое слово"""
        pass

    @abstractmethod
    async def get_keyword(self, keyword_id: int) -> Optional[Keyword]:
        """Получить ключевое слово по ID"""
        pass

    @abstractmethod
    async def get_keywords(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Keyword]:
        """Получить список ключевых слов"""
        pass

    @abstractmethod
    async def update_keyword(
        self,
        keyword_id: int,
        word: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        group_id: Optional[int] = None,
    ) -> bool:
        """Обновить ключевое слово"""
        pass

    @abstractmethod
    async def delete_keyword(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        pass

    @abstractmethod
    async def activate_keyword(self, keyword_id: int) -> bool:
        """Активировать ключевое слово"""
        pass

    @abstractmethod
    async def deactivate_keyword(self, keyword_id: int) -> bool:
        """Деактивировать ключевое слово"""
        pass

    @abstractmethod
    async def archive_keyword(self, keyword_id: int) -> bool:
        """Архивировать ключевое слово"""
        pass

    @abstractmethod
    async def get_keyword_stats(self) -> dict:
        """Получить статистику по ключевым словам"""
        pass