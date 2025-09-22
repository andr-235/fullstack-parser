"""
SQLAlchemy модель для ключевых слов
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import Base
from src.keywords.domain.entities.keyword import Keyword
from src.keywords.domain.value_objects.keyword_word import KeywordWord
from src.keywords.domain.value_objects.keyword_description import KeywordDescription
from src.keywords.domain.value_objects.keyword_category import KeywordCategory
from src.keywords.domain.value_objects.keyword_priority import KeywordPriority


class KeywordModel(Base):
    """SQLAlchemy модель ключевого слова"""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category_name = Column(String(100), nullable=True, index=True)
    priority = Column(Integer, default=5, nullable=False)
    match_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    group_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @classmethod
    def from_domain(cls, keyword: Keyword) -> "KeywordModel":
        """Создать модель из доменной сущности"""
        return cls(
            id=keyword.id,
            word=str(keyword.word),
            description=str(keyword.description) if keyword.description.value else None,
            category_name=str(keyword.category) if keyword.category.value else None,
            priority=keyword.priority.value,
            match_count=keyword.match_count,
            is_active=keyword.is_active,
            is_archived=keyword.is_archived,
            group_id=keyword.group_id,
            created_at=keyword.created_at,
            updated_at=keyword.updated_at,
        )

    def to_domain(self) -> Keyword:
        """Преобразовать в доменную сущность"""
        return Keyword(
            id=self.id,
            word=KeywordWord(self.word),
            description=KeywordDescription(self.description) if self.description else KeywordDescription.empty(),
            category=KeywordCategory(self.category_name) if self.category_name else KeywordCategory.empty(),
            priority=KeywordPriority(self.priority),
            is_active=self.is_active,
            is_archived=self.is_archived,
            match_count=self.match_count,
            group_id=self.group_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )