"""
Infrastructure модель для VK группы (DDD)

SQLAlchemy модель для работы с группами в Infrastructure Layer
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from .base import BaseModel


class VKGroupModel(BaseModel):
    """Infrastructure модель VK группы"""

    __tablename__ = "vk_groups"

    # Основная информация
    vk_id = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="ID группы в ВК",
    )
    screen_name = Column(
        String(100),
        nullable=False,
        comment="Короткое имя группы (@group_name)",
    )
    name = Column(String(200), nullable=False, comment="Название группы")
    description = Column(Text, comment="Описание группы")

    # Настройки мониторинга
    is_active = Column(
        Boolean, default=True, comment="Активен ли мониторинг группы"
    )
    max_posts_to_check = Column(
        Integer, default=100, comment="Максимум постов для проверки"
    )

    # Статистика
    total_posts_parsed = Column(
        Integer, default=0, comment="Общее количество обработанных постов"
    )
    total_comments_found = Column(
        Integer, default=0, comment="Общее количество найденных комментариев"
    )
    last_parsed_at = Column(
        DateTime(timezone=True), comment="Время последней обработки"
    )

    # Дополнительная информация из VK
    members_count = Column(Integer, default=0, comment="Количество участников")
    photo_url = Column(String(500), comment="URL фото группы")
    is_closed = Column(Boolean, default=False, comment="Закрыта ли группа")

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        return {
            "id": self.id,
            "vk_id": self.vk_id,
            "screen_name": self.screen_name,
            "name": self.name,
            "description": self.description or "",
            "is_active": self.is_active,
            "max_posts_to_check": self.max_posts_to_check,
            "members_count": self.members_count or 0,
            "photo_url": self.photo_url or "",
            "is_closed": self.is_closed or False,
            "total_posts_parsed": self.total_posts_parsed or 0,
            "total_comments_found": self.total_comments_found or 0,
            "last_parsed_at": self.last_parsed_at,
        }

    @classmethod
    def from_domain_dict(cls, data: Dict[str, Any]) -> "VKGroupModel":
        """Создать модель из словаря Domain Entity"""
        model = cls()

        # Основная информация
        model.vk_id = data.get("vk_id")
        model.screen_name = data.get("screen_name")
        model.name = data.get("name")
        model.description = data.get("description")

        # Настройки мониторинга
        model.is_active = data.get("is_active", True)
        model.max_posts_to_check = data.get("max_posts_to_check", 100)

        # Статистика
        model.total_posts_parsed = data.get("total_posts_parsed", 0)
        model.total_comments_found = data.get("total_comments_found", 0)
        model.last_parsed_at = data.get("last_parsed_at")

        # Дополнительная информация
        model.members_count = data.get("members_count", 0)
        model.photo_url = data.get("photo_url", "")
        model.is_closed = data.get("is_closed", False)

        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        # Основная информация
        if "vk_id" in data:
            self.vk_id = data["vk_id"]
        if "screen_name" in data:
            self.screen_name = data["screen_name"]
        if "name" in data:
            self.name = data["name"]
        if "description" in data:
            self.description = data["description"]

        # Настройки мониторинга
        if "is_active" in data:
            self.is_active = data["is_active"]
        if "max_posts_to_check" in data:
            self.max_posts_to_check = data["max_posts_to_check"]

        # Статистика
        if "total_posts_parsed" in data:
            self.total_posts_parsed = data["total_posts_parsed"]
        if "total_comments_found" in data:
            self.total_comments_found = data["total_comments_found"]
        if "last_parsed_at" in data:
            self.last_parsed_at = data["last_parsed_at"]

        # Дополнительная информация
        if "members_count" in data:
            self.members_count = data["members_count"]
        if "photo_url" in data:
            self.photo_url = data["photo_url"]
        if "is_closed" in data:
            self.is_closed = data["is_closed"]

    def __repr__(self) -> str:
        return f"<VKGroupModel(id={self.id}, vk_id={self.vk_id}, screen_name='{self.screen_name}')>"
