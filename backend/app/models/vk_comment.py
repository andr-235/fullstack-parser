"""
Модель VK комментария
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class VKComment(BaseModel):
    """Модель VK комментария"""
    
    __tablename__ = "vk_comments"
    
    # Основная информация
    vk_id = Column(Integer, nullable=False, index=True, comment="ID комментария в ВК")
    text = Column(Text, nullable=False, comment="Текст комментария")
    
    # Связи
    post_id = Column(Integer, ForeignKey("vk_posts.id"), nullable=False)
    post = relationship("VKPost", back_populates="comments")
    
    # Автор комментария
    author_id = Column(Integer, nullable=False, comment="ID автора комментария")
    author_name = Column(String(200), comment="Имя автора")
    author_screen_name = Column(String(100), comment="Короткое имя автора")
    author_photo_url = Column(String(500), comment="URL фото автора")
    
    # Метаданные
    published_at = Column(DateTime, nullable=False, comment="Дата публикации комментария")
    likes_count = Column(Integer, default=0, comment="Количество лайков")
    
    # Иерархия комментариев
    parent_comment_id = Column(Integer, ForeignKey("vk_comments.id"), comment="ID родительского комментария")
    parent_comment = relationship("VKComment", remote_side="VKComment.id")
    
    # Вложения (упрощённо)
    has_attachments = Column(Boolean, default=False, comment="Есть ли вложения")
    attachments_info = Column(Text, comment="JSON с информацией о вложениях")
    
    # Состояние обработки
    is_processed = Column(Boolean, default=False, comment="Обработан ли комментарий")
    processed_at = Column(DateTime, comment="Когда был обработан")
    
    # Найденные ключевые слова
    matched_keywords_count = Column(Integer, default=0, comment="Количество найденных ключевых слов")
    
    # Связи с ключевыми словами
    keyword_matches = relationship("CommentKeywordMatch", back_populates="comment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VKComment(vk_id={self.vk_id}, post_id={self.post_id}, matches={self.matched_keywords_count})>" 