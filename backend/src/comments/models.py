"""
Модели SQLAlchemy для модуля Comments

Определяет модели данных для работы с комментариями VK
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..keywords.models import Keyword
    from ..authors.infrastructure.models import Author
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from ..models import BaseModel


class Comment(BaseModel):
    """
    Модель комментария VK

    Основная модель для хранения комментариев из VK API
    """

    __tablename__ = "vk_comments"

    # Основные поля
    vk_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # VK специфичные поля
    post_vk_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    group_vk_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True
    )
    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        Integer, index=True, nullable=True
    )

    # Информация об авторе
    author_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    author_screen_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    author_photo_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    # Статистика и взаимодействия
    likes_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    matched_keywords_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Статусы
    is_archived: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_viewed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_processed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    has_attachments: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Временные метки
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Дополнительные данные
    attachments_info: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Связи
    author = relationship(
        "authors.infrastructure.models.Author",
        back_populates="comments",
        foreign_keys=[author_id],
        lazy="select"
    )

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_vk_comments_group_published", "group_vk_id", "published_at"),
        Index("ix_vk_comments_post_published", "post_id", "published_at"),
        Index("ix_vk_comments_author_published", "author_id", "published_at"),
        Index(
            "ix_vk_comments_status_processed",
            "is_viewed",
            "is_processed",
            "is_archived",
        ),
        Index("ix_vk_comments_text_search", "text", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, vk_id={self.vk_id}, author={self.author_name})>"

    @property
    def is_recent(self) -> bool:
        """Проверяет, является ли комментарий недавним (за последние 24 часа)"""
        if not self.published_at:
            return False
        return (datetime.utcnow() - self.published_at).total_seconds() < 86400

    @property
    def has_keywords(self) -> bool:
        """Проверяет, есть ли у комментария совпадения с ключевыми словами"""
        return self.matched_keywords_count > 0

    def mark_as_viewed(self) -> None:
        """Отметить комментарий как просмотренный"""
        self.is_viewed = True
        self.viewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_as_processed(self) -> None:
        """Отметить комментарий как обработанный"""
        self.is_processed = True
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Архивировать комментарий"""
        self.is_archived = True
        self.archived_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class CommentKeywordMatch(BaseModel):
    """
    Модель для связи комментариев с ключевыми словами

    Связывает комментарии с найденными в них ключевыми словами
    """

    __tablename__ = "comment_keyword_matches"

    comment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vk_comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("keywords.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Дополнительная информация о совпадении
    match_position: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    match_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Связи
    comment: Mapped["Comment"] = relationship(
        "Comment", back_populates="keyword_matches"
    )
    keyword: Mapped["Keyword"] = relationship("Keyword")

    __table_args__ = (
        Index(
            "ix_comment_keyword_unique",
            "comment_id",
            "keyword_id",
            unique=True,
        ),
        Index("ix_comment_keyword_comment", "comment_id"),
        Index("ix_comment_keyword_keyword", "keyword_id"),
    )

    def __repr__(self) -> str:
        return f"<CommentKeywordMatch(comment_id={self.comment_id}, keyword_id={self.keyword_id})>"


class CommentAnalysis(BaseModel):
    """
    Модель для хранения результатов анализа комментариев

    Содержит результаты различных видов анализа текста комментариев
    """

    __tablename__ = "comment_analyses"

    comment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vk_comments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Результаты анализа
    sentiment_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    sentiment_label: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    toxicity_score: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Морфологический анализ
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    character_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    avg_word_length: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Дополнительные метрики
    readability_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    complexity_score: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Метаданные анализа
    analysis_version: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    analysis_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Связи
    comment: Mapped["Comment"] = relationship(
        "Comment", back_populates="analysis"
    )

    def __repr__(self) -> str:
        return f"<CommentAnalysis(comment_id={self.comment_id}, sentiment={self.sentiment_label})>"


# Добавляем обратные связи к основной модели Comment
Comment.keyword_matches: Mapped[List["CommentKeywordMatch"]] = relationship(
    "CommentKeywordMatch",
    back_populates="comment",
    cascade="all, delete-orphan",
)

Comment.analysis: Mapped[Optional["CommentAnalysis"]] = relationship(
    "CommentAnalysis",
    back_populates="comment",
    uselist=False,
    cascade="all, delete-orphan",
)


# Экспорт моделей
__all__ = [
    "Comment",
    "CommentKeywordMatch",
    "CommentAnalysis",
]
