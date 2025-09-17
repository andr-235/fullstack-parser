"""
SQLAlchemy модели для модуля авторов
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from src.common.database import Base

if TYPE_CHECKING:
    from comments.models import Comment


class AuthorModel(Base):
    """SQLAlchemy модель автора"""
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    screen_name = Column(String(100), nullable=True, index=True)
    photo_url = Column(String(500), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    followers_count = Column(Integer, default=0, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    author_metadata = Column(Text, nullable=True)  # JSON as text
    comments_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Связи
    comments = relationship("Comment", back_populates="author", lazy="select")

    # Индексы
    __table_args__ = (
        Index('idx_authors_vk_id', 'vk_id'),
        Index('idx_authors_screen_name', 'screen_name'),
        Index('idx_authors_status', 'status'),
        Index('idx_authors_created_at', 'created_at'),
    )
