"""
Модель ключевых слов для фильтрации комментариев
"""

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Keyword(BaseModel):
    """Модель ключевого слова для фильтрации"""

    __tablename__ = "keywords"

    # Основная информация
    word = Column(String(200), nullable=False, index=True, comment="Ключевое слово")
    category = Column(String(100), comment="Категория ключевого слова")
    description = Column(Text, comment="Описание ключевого слова")

    # Настройки поиска
    is_active = Column(Boolean, default=True, comment="Активно ли ключевое слово")
    is_case_sensitive = Column(Boolean, default=False, comment="Учитывать регистр")
    is_whole_word = Column(Boolean, default=False, comment="Искать только целые слова")

    # Статистика
    total_matches = Column(Integer, default=0, comment="Общее количество совпадений")

    # Связи
    comment_matches = relationship("CommentKeywordMatch", back_populates="keyword")

    def __repr__(self):
        return f"<Keyword(word={self.word}, category={self.category}, active={self.is_active})>"
