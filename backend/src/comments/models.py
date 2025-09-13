"""
SQLAlchemy модели для модуля Comments
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from common.database import Base


class Comment(Base):
    """SQLAlchemy модель комментария"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, unique=True, index=True, nullable=False)
    group_id = Column(Integer, nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_deleted = Column(Boolean, default=False, index=True)

    # Связи
    post = relationship("Post", back_populates="comments", lazy="select")
    author = relationship("AuthorModel", back_populates="comments", lazy="select")
    keyword_matches = relationship("CommentKeywordMatch", back_populates="comment", lazy="select")


class CommentKeywordMatch(Base):
    """SQLAlchemy модель совпадения ключевых слов"""

    __tablename__ = "comment_keyword_matches"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    confidence = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    comment = relationship("Comment", back_populates="keyword_matches")

    # Индексы
    __table_args__ = (
        Index('ix_comment_keyword', 'comment_id', 'keyword'),
        Index('ix_keyword_confidence', 'keyword', 'confidence'),
    )
