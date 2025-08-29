"""
Infrastructure модель для ключевого слова (DDD)

SQLAlchemy модель для работы с ключевыми словами в Infrastructure Layer
"""

from typing import Any, Dict

from sqlalchemy import Boolean, Column, Integer, String, Text

from .base import BaseModel


class KeywordModel(BaseModel):
    """Infrastructure модель ключевого слова"""

    __tablename__ = "keywords"

    word = Column(String(255), nullable=False, index=True)
    category = Column(String(100), default="general")
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    match_count = Column(Integer, default=0)

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        return {
            "id": self.id,
            "word": self.word,
            "category": self.category,
            "description": self.description,
            "is_active": self.is_active,
            "priority": self.priority,
            "match_count": self.match_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_domain_dict(cls, data: Dict[str, Any]) -> "KeywordModel":
        """Создать модель из словаря Domain Entity"""
        model = cls()
        model.word = data.get("word")
        model.category = data.get("category", "general")
        model.description = data.get("description")
        model.is_active = data.get("is_active", True)
        model.priority = data.get("priority", 5)
        model.match_count = data.get("match_count", 0)
        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        if "word" in data:
            self.word = data["word"]
        if "category" in data:
            self.category = data["category"]
        if "description" in data:
            self.description = data["description"]
        if "is_active" in data:
            self.is_active = data["is_active"]
        if "priority" in data:
            self.priority = data["priority"]
        if "match_count" in data:
            self.match_count = data["match_count"]

    def __repr__(self) -> str:
        return f"<KeywordModel(id={self.id}, word='{self.word}')>"
