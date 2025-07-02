"""
Модель VK группы для мониторинга
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class VKGroup(BaseModel):
    """Модель VK группы для мониторинга"""

    __tablename__ = "vk_groups"

    # Основная информация
    vk_id = Column(
        Integer, unique=True, nullable=False, index=True, comment="ID группы в ВК"
    )
    screen_name = Column(
        String(100), nullable=False, comment="Короткое имя группы (@group_name)"
    )
    name = Column(String(200), nullable=False, comment="Название группы")
    description = Column(Text, comment="Описание группы")

    # Настройки мониторинга
    is_active = Column(Boolean, default=True, comment="Активен ли мониторинг группы")
    max_posts_to_check = Column(
        Integer, default=100, comment="Максимум постов для проверки"
    )

    # Статистика
    last_parsed_at = Column(DateTime, comment="Когда последний раз парсили группу")
    total_posts_parsed = Column(
        Integer, default=0, comment="Общее количество обработанных постов"
    )
    total_comments_found = Column(
        Integer, default=0, comment="Общее количество найденных комментариев"
    )

    # Метаданные VK
    members_count = Column(Integer, comment="Количество участников")
    is_closed = Column(Boolean, default=False, comment="Закрытая ли группа")
    photo_url = Column(String(500), comment="URL аватара группы")

    # Связи
    posts = relationship("VKPost", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<VKGroup(vk_id={self.vk_id}, name={self.name}, active={self.is_active})>"
        )
