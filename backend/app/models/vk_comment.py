"""
Модель VK комментария
"""

from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class VKComment(BaseModel):
    """Модель VK комментария"""

    __tablename__ = "vk_comments"

    # Основная информация
    vk_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="ID комментария в ВК"
    )
    text: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Текст комментария"
    )

    # Связи
    post_id: Mapped[int] = mapped_column(
        ForeignKey("vk_posts.id"), nullable=False
    )
    post: Mapped["VKPost"] = relationship("VKPost", back_populates="comments")
    post_vk_id: Mapped[Optional[int]] = mapped_column(
        Integer, comment="ID поста в VK (для формирования ссылок)"
    )

    # Автор комментария
    author_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="ID автора комментария"
    )
    author_name: Mapped[Optional[str]] = mapped_column(
        String(200), comment="Имя автора"
    )
    author_screen_name: Mapped[Optional[str]] = mapped_column(
        String(100), comment="Короткое имя автора"
    )
    author_photo_url: Mapped[Optional[str]] = mapped_column(
        String(500), comment="URL фото автора"
    )

    # Метаданные
    published_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="Дата публикации комментария",
    )
    likes_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество лайков"
    )

    # Иерархия комментариев
    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vk_comments.id"), comment="ID родительского комментария"
    )
    parent_comment: Mapped[Optional["VKComment"]] = relationship(
        "VKComment", remote_side="VKComment.id"
    )

    # Вложения (упрощённо)
    has_attachments: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Есть ли вложения"
    )
    attachments_info: Mapped[Optional[str]] = mapped_column(
        Text, comment="JSON с информацией о вложениях"
    )

    # Состояние обработки
    is_processed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Обработан ли комментарий"
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), comment="Когда был обработан"
    )

    # Найденные ключевые слова
    matched_keywords_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество найденных ключевых слов"
    )

    # Статус просмотра и архивирования
    is_viewed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Просмотрен ли комментарий"
    )
    viewed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), comment="Когда был просмотрен"
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Архивирован ли комментарий"
    )
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), comment="Когда был архивирован"
    )

    # Связи с ключевыми словами
    keyword_matches: Mapped[list["CommentKeywordMatch"]] = relationship(
        "CommentKeywordMatch",
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<VKComment(vk_id={self.vk_id}, post_id={self.post_id}, matches={self.matched_keywords_count})>"
