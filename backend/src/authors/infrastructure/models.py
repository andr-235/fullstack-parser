"""
Модели SQLAlchemy для модуля авторов

Определяет модели данных для работы с авторами VK
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ...models import BaseModel

if TYPE_CHECKING:
    from ...comments.models import Comment


class Author(BaseModel):
    """Модель автора VK"""

    __tablename__ = "vk_authors"

    vk_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    first_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    screen_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    photo_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    # Связи
    comments: Mapped[List["Comment"]] = relationship(
        "comments.models.Comment",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_vk_authors_vk_id", "vk_id"),
        Index("ix_vk_authors_screen_name", "screen_name"),
        Index("ix_vk_authors_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, vk_id={self.vk_id}, name={self.first_name} {self.last_name})>"

    @property
    def full_name(self) -> str:
        """Полное имя автора."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else str(self.vk_id)

    @property
    def display_name(self) -> str:
        """Отображаемое имя автора."""
        if self.screen_name:
            return self.screen_name
        return self.full_name

    def is_updated(self) -> bool:
        """Проверка, был ли автор обновлен."""
        return self.updated_at is not None

    def get_comments_count(self) -> int:
        """Получить количество комментариев автора."""
        return len(self.comments) if self.comments else 0
