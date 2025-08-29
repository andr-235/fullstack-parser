"""
Infrastructure модель для связи комментариев и ключевых слов (DDD)

SQLAlchemy модель для работы со связями комментариев и ключевых слов в Infrastructure Layer
"""

from typing import Any, Dict

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from .base import BaseModel


class CommentKeywordMatchModel(BaseModel):
    """Infrastructure модель связи комментария и ключевого слова"""

    __tablename__ = "comment_keyword_matches"

    comment_id = Column(
        ForeignKey("vk_comments.id"), nullable=False, index=True
    )
    keyword_id = Column(ForeignKey("keywords.id"), nullable=False, index=True)
    match_type = Column(
        String(50), default="exact"
    )  # exact, morphological, fuzzy
    confidence_score = Column(Integer, default=100)  # 0-100
    context_before = Column(String(255))
    context_after = Column(String(255))
    match_position = Column(Integer)  # позиция совпадения в тексте

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        return {
            "id": self.id,
            "comment_id": self.comment_id,
            "keyword_id": self.keyword_id,
            "match_type": self.match_type,
            "confidence_score": self.confidence_score or 100,
            "context_before": self.context_before,
            "context_after": self.context_after,
            "match_position": self.match_position,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_domain_dict(
        cls, data: Dict[str, Any]
    ) -> "CommentKeywordMatchModel":
        """Создать модель из словаря Domain Entity"""
        model = cls()
        model.comment_id = data.get("comment_id")
        model.keyword_id = data.get("keyword_id")
        model.match_type = data.get("match_type", "exact")
        model.confidence_score = data.get("confidence_score", 100)
        model.context_before = data.get("context_before")
        model.context_after = data.get("context_after")
        model.match_position = data.get("match_position")
        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        if "comment_id" in data:
            self.comment_id = data["comment_id"]
        if "keyword_id" in data:
            self.keyword_id = data["keyword_id"]
        if "match_type" in data:
            self.match_type = data["match_type"]
        if "confidence_score" in data:
            self.confidence_score = data["confidence_score"]
        if "context_before" in data:
            self.context_before = data["context_before"]
        if "context_after" in data:
            self.context_after = data["context_after"]
        if "match_position" in data:
            self.match_position = data["match_position"]

    def __repr__(self) -> str:
        return f"<CommentKeywordMatchModel(id={self.id}, comment_id={self.comment_id}, keyword_id={self.keyword_id})>"
