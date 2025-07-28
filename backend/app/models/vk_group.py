"""
Модель VK группы для мониторинга
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.vk_post import VKPost


class VKGroup(BaseModel):
    """Модель VK группы для мониторинга"""

    __tablename__ = "vk_groups"

    # Основная информация
    vk_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="ID группы в ВК",
    )
    screen_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Короткое имя группы (@group_name)",
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Название группы"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="Описание группы"
    )

    # Настройки мониторинга
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Активен ли мониторинг группы"
    )
    max_posts_to_check: Mapped[int] = mapped_column(
        Integer, default=100, comment="Максимум постов для проверки"
    )

    # Настройки автоматического мониторинга
    auto_monitoring_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Включен ли автоматический мониторинг"
    )
    monitoring_interval_minutes: Mapped[int] = mapped_column(
        Integer, default=60, comment="Интервал мониторинга в минутах"
    )
    next_monitoring_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        comment="Когда следующий раз запускать мониторинг",
    )
    monitoring_priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
        comment="Приоритет мониторинга (1-10, где 10 - высший)",
    )

    # Статистика
    last_parsed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        comment="Когда последний раз парсили группу",
    )
    total_posts_parsed: Mapped[int] = mapped_column(
        Integer, default=0, comment="Общее количество обработанных постов"
    )
    total_comments_found: Mapped[int] = mapped_column(
        Integer, default=0, comment="Общее количество найденных комментариев"
    )

    # Статистика мониторинга
    monitoring_runs_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество запусков мониторинга"
    )
    last_monitoring_success: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        comment="Последний успешный запуск мониторинга",
    )
    last_monitoring_error: Mapped[Optional[str]] = mapped_column(
        Text, comment="Последняя ошибка мониторинга"
    )

    # Метаданные VK
    members_count: Mapped[Optional[int]] = mapped_column(
        Integer, comment="Количество участников"
    )
    is_closed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Закрытая ли группа"
    )
    photo_url: Mapped[Optional[str]] = mapped_column(
        String(500), comment="URL аватара группы"
    )

    # Связи
    posts: Mapped[List["VKPost"]] = relationship(
        "VKPost", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<VKGroup(vk_id={self.vk_id}, name={self.name}, active={self.is_active})>"
