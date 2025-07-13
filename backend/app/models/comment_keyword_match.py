"""
Модель связи комментария с ключевым словом
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.keyword import Keyword
    from app.models.vk_comment import VKComment


class CommentKeywordMatch(BaseModel):
    """Модель связи комментария с найденным ключевым словом."""

    __tablename__ = "comment_keyword_matches"

    # Связи
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("vk_comments.id"), nullable=False
    )
    comment: Mapped["VKComment"] = relationship(back_populates="keyword_matches")

    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id"), nullable=False)
    keyword: Mapped["Keyword"] = relationship(back_populates="comment_matches")

    # Детали совпадения
    matched_text: Mapped[Optional[str]] = mapped_column(
        String(500), comment="Найденный текст"
    )
    match_position: Mapped[Optional[int]] = mapped_column(
        comment="Позиция совпадения в тексте"
    )
    match_context: Mapped[Optional[str]] = mapped_column(
        String(1000), comment="Контекст вокруг совпадения"
    )

    # Метаданные
    found_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        comment="Когда найдено совпадение",
    )

    def __repr__(self) -> str:
        return (
            f"<CommentKeywordMatch(comment_id={self.comment_id}, "
            f"keyword_id={self.keyword_id})>"
        )
