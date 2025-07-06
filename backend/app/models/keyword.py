"""
Модель ключевых слов для фильтрации комментариев
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from app.models.base import BaseModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.comment_keyword_match import CommentKeywordMatch


class Keyword(BaseModel):
    """Модель ключевого слова для фильтрации."""

    __tablename__ = "keywords"

    # Основная информация
    word: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment="Ключевое слово"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100), comment="Категория ключевого слова"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="Описание ключевого слова"
    )

    # Настройки поиска
    is_active: Mapped[bool] = mapped_column(
        default=True, comment="Активно ли ключевое слово"
    )
    is_case_sensitive: Mapped[bool] = mapped_column(
        default=False, comment="Учитывать регистр"
    )
    is_whole_word: Mapped[bool] = mapped_column(
        default=False, comment="Искать только целые слова"
    )

    # Статистика
    total_matches: Mapped[int] = mapped_column(
        default=0, comment="Общее количество совпадений"
    )

    # Связи
    comment_matches: Mapped[List["CommentKeywordMatch"]] = relationship(
        back_populates="keyword", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Keyword(word='{self.word}', "
            f"category='{self.category}', active={self.is_active})>"
        )
