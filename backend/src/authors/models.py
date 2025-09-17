"""
SQLAlchemy модели для модуля авторов
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Index, Integer, JSON, String
from sqlalchemy.orm import relationship

from src.common.database import Base

if TYPE_CHECKING:
  from comments.models import Comment


class AuthorModel(Base):
  """SQLAlchemy модель автора VK.

  Модель представляет автора в системе мониторинга комментариев VK.
  Содержит основную информацию из VK API и дополнительные метаданные
  для управления состоянием автора в системе.

  Attributes:
      id (int): Уникальный идентификатор автора в системе.
      vk_id (int): Идентификатор автора в VK.
      first_name (str): Имя автора.
      last_name (str): Фамилия автора.
      screen_name (str): Короткое имя (screen name) автора в VK.
      photo_url (str): URL фотографии автора.
      status (str): Статус автора в системе (active, inactive, banned и т.д.).
      is_closed (bool): Флаг закрытого профиля VK.
      is_verified (bool): Флаг верификации автора в VK.
      followers_count (int): Количество подписчиков.
      last_activity (datetime): Время последней активности автора.
      author_metadata (dict): Дополнительные метаданные автора в формате JSON.
      comments_count (int): Количество комментариев автора.
      created_at (datetime): Дата и время создания записи.
      updated_at (datetime): Дата и время последнего обновления.
      comments (relationship): Связь с комментариями автора.
  """
  __tablename__ = "authors"

  id = Column(Integer, primary_key=True, index=True)
  """Уникальный идентификатор автора в базе данных."""

  vk_id = Column(Integer, unique=True, index=True, nullable=False)
  """Идентификатор автора в VK."""

  first_name = Column(String(255), nullable=True)
  """Имя автора."""

  last_name = Column(String(255), nullable=True)
  """Фамилия автора."""

  screen_name = Column(String(100), nullable=True, index=True)
  """Короткое имя автора (screen name)."""

  photo_url = Column(String(500), nullable=True)
  """URL фотографии автора."""

  status = Column(String(20), default="active", nullable=False)
  """Статус автора (active, inactive и т.д.)."""

  is_closed = Column(Boolean, default=False, nullable=False)
  """Закрыт ли профиль автора."""

  is_verified = Column(Boolean, default=False, nullable=False)
  """Верифицирован ли автор."""

  followers_count = Column(Integer, default=0, nullable=False)
  """Количество подписчиков автора."""

  last_activity = Column(DateTime, nullable=True)
  """Время последней активности автора."""

  author_metadata = Column(JSON, nullable=True)
  """Дополнительные метаданные автора в формате JSON."""

  comments_count = Column(Integer, default=0, nullable=False)
  """Количество комментариев автора."""

  created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
  """Время создания записи."""

  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
  """Время последнего обновления записи."""

  # Связи
  comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan", lazy="select")
  """Связь с комментариями автора."""

  # Индексы
  __table_args__ = (
    Index('idx_authors_status', 'status'),
    Index('idx_authors_created_at', 'created_at'),
    Index('idx_authors_is_verified', 'is_verified'),
    CheckConstraint('followers_count >= 0', name='check_followers_count_non_negative'),
  )
