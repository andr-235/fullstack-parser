"""
Интерфейс репозитория для работы с ключевыми словами
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.keywords.domain.entities.keyword import Keyword


class KeywordRepositoryInterface(ABC):
    """Интерфейс репозитория ключевых слов"""

    @abstractmethod
    async def save(self, keyword: Keyword) -> Keyword:
        """Сохранить ключевое слово"""
        pass

    @abstractmethod
    async def find_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Найти ключевое слово по ID"""
        pass

    @abstractmethod
    async def find_by_word(self, word: str) -> Optional[Keyword]:
        """Найти ключевое слово по слову"""
        pass

    @abstractmethod
    async def find_all(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Keyword]:
        """Найти все ключевые слова с фильтрами"""
        pass

    @abstractmethod
    async def update(self, keyword: Keyword) -> bool:
        """Обновить ключевое слово"""
        pass

    @abstractmethod
    async def delete(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        pass

    @abstractmethod
    async def exists_by_word(self, word: str) -> bool:
        """Проверить существование ключевого слова по слову"""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Получить общее количество ключевых слов"""
        pass

    @abstractmethod
    async def count_active(self) -> int:
        """Получить количество активных ключевых слов"""
        pass

    @abstractmethod
    async def count_by_period(self, days: int) -> int:
        """Получить количество ключевых слов за период"""
        pass