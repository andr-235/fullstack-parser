"""
Модель VK поста
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class VKPost(BaseModel):
    """Модель VK поста"""

    __tablename__ = "vk_posts"

    # Основная информация
    vk_id = Column(Integer, nullable=False, index=True, comment="ID поста в ВК")
    vk_owner_id = Column(Integer, nullable=False, comment="ID владельца поста")
    text = Column(Text, comment="Текст поста")

    # Связь с группой
    group_id = Column(Integer, ForeignKey("vk_groups.id"), nullable=False)
    group = relationship("VKGroup", back_populates="posts")

    # Метаданные
    published_at = Column(DateTime, nullable=False, comment="Дата публикации поста")
    likes_count = Column(Integer, default=0, comment="Количество лайков")
    reposts_count = Column(Integer, default=0, comment="Количество репостов")
    comments_count = Column(Integer, default=0, comment="Количество комментариев")
    views_count = Column(Integer, default=0, comment="Количество просмотров")

    # Состояние обработки
    is_parsed = Column(Boolean, default=False, comment="Обработан ли пост")
    parsed_at = Column(DateTime, comment="Когда был обработан")

    # Вложения (упрощённо)
    has_attachments = Column(Boolean, default=False, comment="Есть ли вложения")
    attachments_info = Column(Text, comment="JSON с информацией о вложениях")

    # Связи
    comments = relationship(
        "VKComment", back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<VKPost(vk_id={self.vk_id}, group_id={self.group_id}, parsed={self.is_parsed})>"
