"""
Модель VK поста
"""

from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Integer, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class VKPost(BaseModel):
    """Модель VK поста"""

    __tablename__ = "vk_posts"
    __table_args__ = (
        UniqueConstraint("vk_id", "group_id", name="uix_vkpost_vkid_groupid"),
    )

    # Основная информация
    vk_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="ID поста в ВК"
    )
    vk_owner_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="ID владельца поста"
    )
    text: Mapped[Optional[str]] = mapped_column(Text, comment="Текст поста")

    # Связь с группой
    group_id: Mapped[int] = mapped_column(
        ForeignKey("vk_groups.id"), nullable=False
    )
    group: Mapped["VKGroup"] = relationship("VKGroup", back_populates="posts")

    # Метаданные
    published_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="Дата публикации поста",
    )
    likes_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество лайков"
    )
    reposts_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество репостов"
    )
    comments_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество комментариев"
    )
    views_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество просмотров"
    )

    # Состояние обработки
    is_parsed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Обработан ли пост"
    )
    parsed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), comment="Когда был обработан"
    )

    # Вложения (упрощённо)
    has_attachments: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Есть ли вложения"
    )
    attachments_info: Mapped[Optional[str]] = mapped_column(
        Text, comment="JSON с информацией о вложениях"
    )

    # Связи
    comments: Mapped[list["VKComment"]] = relationship(
        "VKComment", back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<VKPost(vk_id={self.vk_id}, group_id={self.group_id}, parsed={self.is_parsed})>"
