"""
Domain сущности для ключевых слов (DDD)
"""

from typing import List, Optional
from .base import Entity, ValueObject


class KeywordStatus(ValueObject):
    """Статус ключевого слова"""

    def __init__(self, is_active: bool = True, is_archived: bool = False):
        self.is_active = is_active
        self.is_archived = is_archived


class KeywordCategory(ValueObject):
    """Категория ключевого слова"""

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description


class Keyword(Entity):
    """Доменная сущность ключевого слова"""

    def __init__(
        self,
        id: Optional[int] = None,
        word: str = None,
        category: Optional[KeywordCategory] = None,
        status: Optional[KeywordStatus] = None,
    ):
        super().__init__(id)
        self.word = word
        self.category = category
        self.status = status or KeywordStatus()
        self.matched_comments_count = 0

    def activate(self) -> None:
        """Активировать ключевое слово"""
        self.status = KeywordStatus(
            is_active=True, is_archived=self.status.is_archived
        )
        self.update()

    def deactivate(self) -> None:
        """Деактивировать ключевое слово"""
        self.status = KeywordStatus(
            is_active=False, is_archived=self.status.is_archived
        )
        self.update()

    def archive(self) -> None:
        """Архивировать ключевое слово"""
        self.status = KeywordStatus(is_active=False, is_archived=True)
        self.update()

    def increment_matches(self) -> None:
        """Увеличить счетчик совпадений"""
        self.matched_comments_count += 1
        self.update()

    def reset_matches(self) -> None:
        """Сбросить счетчик совпадений"""
        self.matched_comments_count = 0
        self.update()

    @property
    def is_active(self) -> bool:
        return self.status.is_active

    @property
    def is_archived(self) -> bool:
        return self.status.is_archived

    @property
    def category_name(self) -> Optional[str]:
        return self.category.name if self.category else None
