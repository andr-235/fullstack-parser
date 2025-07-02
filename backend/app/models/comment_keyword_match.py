"""
Модель связи комментария с ключевым словом
"""

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class CommentKeywordMatch(BaseModel):
    """Модель связи комментария с найденным ключевым словом"""

    __tablename__ = "comment_keyword_matches"

    # Связи
    comment_id = Column(Integer, ForeignKey("vk_comments.id"), nullable=False)
    comment = relationship("VKComment", back_populates="keyword_matches")

    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    keyword = relationship("Keyword", back_populates="comment_matches")

    # Детали совпадения
    matched_text = Column(String(500), comment="Найденный текст")
    match_position = Column(Integer, comment="Позиция совпадения в тексте")
    match_context = Column(String(1000), comment="Контекст вокруг совпадения")

    # Метаданные
    found_at = Column(
        DateTime, default=datetime.utcnow, comment="Когда найдено совпадение"
    )

    def __repr__(self):
        return f"<CommentKeywordMatch(comment_id={self.comment_id}, keyword_id={self.keyword_id})>"
