"""
Infrastructure модель для VK поста (DDD)

SQLAlchemy модель для работы с постами в Infrastructure Layer
"""

from typing import Any, Dict

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .base import BaseModel


class VKPostModel(BaseModel):
    """Infrastructure модель VK поста"""

    __tablename__ = "vk_posts"

    vk_id = Column(Integer, nullable=False, index=True)
    group_id = Column(Integer, nullable=False, index=True)
    text = Column(Text)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    reposts_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    date_posted = Column(DateTime(timezone=True))
    is_pinned = Column(Boolean, default=False)

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        return {
            "id": self.id,
            "vk_id": self.vk_id,
            "group_id": self.group_id,
            "text": self.text,
            "likes_count": self.likes_count or 0,
            "comments_count": self.comments_count or 0,
            "reposts_count": self.reposts_count or 0,
            "views_count": self.views_count or 0,
            "date_posted": self.date_posted,
            "is_pinned": self.is_pinned or False,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_domain_dict(cls, data: Dict[str, Any]) -> "VKPostModel":
        """Создать модель из словаря Domain Entity"""
        model = cls()
        model.vk_id = data.get("vk_id")
        model.group_id = data.get("group_id")
        model.text = data.get("text")
        model.likes_count = data.get("likes_count", 0)
        model.comments_count = data.get("comments_count", 0)
        model.reposts_count = data.get("reposts_count", 0)
        model.views_count = data.get("views_count", 0)
        model.date_posted = data.get("date_posted")
        model.is_pinned = data.get("is_pinned", False)
        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        if "vk_id" in data:
            self.vk_id = data["vk_id"]
        if "group_id" in data:
            self.group_id = data["group_id"]
        if "text" in data:
            self.text = data["text"]
        if "likes_count" in data:
            self.likes_count = data["likes_count"]
        if "comments_count" in data:
            self.comments_count = data["comments_count"]
        if "reposts_count" in data:
            self.reposts_count = data["reposts_count"]
        if "views_count" in data:
            self.views_count = data["views_count"]
        if "date_posted" in data:
            self.date_posted = data["date_posted"]
        if "is_pinned" in data:
            self.is_pinned = data["is_pinned"]

    def __repr__(self) -> str:
        return f"<VKPostModel(id={self.id}, vk_id={self.vk_id})>"
