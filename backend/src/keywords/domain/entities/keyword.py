"""
Доменная сущность Keyword
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.keywords.domain.value_objects.keyword_word import KeywordWord
from src.keywords.domain.value_objects.keyword_description import KeywordDescription
from src.keywords.domain.value_objects.keyword_category import KeywordCategory
from src.keywords.domain.value_objects.keyword_priority import KeywordPriority


@dataclass
class Keyword:
    """Доменная сущность ключевого слова"""

    id: Optional[int]
    word: KeywordWord
    description: KeywordDescription
    category: KeywordCategory
    priority: KeywordPriority
    is_active: bool
    is_archived: bool
    match_count: int
    group_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """Валидация после инициализации"""
        if self.match_count < 0:
            raise ValueError("Количество совпадений не может быть отрицательным")

        if self.is_archived and not self.is_active:
            raise ValueError("Архивированное ключевое слово не может быть неактивным")

    @classmethod
    def create(
        cls,
        word: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        group_id: Optional[int] = None,
    ) -> "Keyword":
        """Создать новое ключевое слово"""
        from src.keywords.shared.constants import DEFAULT_PRIORITY

        now = datetime.utcnow()

        return cls(
            id=None,
            word=KeywordWord(word),
            description=KeywordDescription(description),
            category=KeywordCategory(category) if category else KeywordCategory.empty(),
            priority=KeywordPriority(priority or DEFAULT_PRIORITY),
            is_active=True,
            is_archived=False,
            match_count=0,
            group_id=group_id,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        word: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        group_id: Optional[int] = None,
    ) -> None:
        """Обновить ключевое слово"""
        if word is not None:
            self.word = KeywordWord(word)

        if description is not None:
            self.description = KeywordDescription(description)

        if category is not None:
            self.category = KeywordCategory(category)

        if priority is not None:
            self.priority = KeywordPriority(priority)

        if group_id is not None:
            self.group_id = group_id

        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Активировать ключевое слово"""
        from src.keywords.shared.exceptions import CannotActivateArchivedKeywordError

        if self.is_archived:
            raise CannotActivateArchivedKeywordError()

        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Деактивировать ключевое слово"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Архивировать ключевое слово"""
        self.is_archived = True
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def increment_match_count(self) -> None:
        """Увеличить счетчик совпадений"""
        self.match_count += 1
        self.updated_at = datetime.utcnow()

    def can_be_activated(self) -> bool:
        """Проверить, можно ли активировать ключевое слово"""
        return not self.is_archived

    def is_available(self) -> bool:
        """Проверить, доступно ли ключевое слово для использования"""
        return self.is_active and not self.is_archived

    def __str__(self) -> str:
        """Строковое представление"""
        return f"Keyword(id={self.id}, word='{self.word}', active={self.is_active})"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return (f"Keyword(id={self.id}, word={self.word!r}, "
                f"category={self.category!r}, priority={self.priority!r}, "
                f"active={self.is_active}, archived={self.is_archived})")

    def __eq__(self, other) -> bool:
        """Сравнение с другим Keyword"""
        if not isinstance(other, Keyword):
            return False
        return (self.id == other.id and
                self.word == other.word and
                self.is_active == other.is_active)

    def __hash__(self) -> int:
        """Хэш для использования в множествах"""
        return hash((self.id, self.word, self.is_active))