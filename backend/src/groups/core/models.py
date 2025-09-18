"""
SQLAlchemy модели для модуля Groups
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from src.common.database import Base


class Group(Base):
    """SQLAlchemy модель группы VK"""

    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    screen_name = Column(String(255), unique=True, index=True)
    description = Column(Text)
    members_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
