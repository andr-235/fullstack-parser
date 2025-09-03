"""
Глобальные модели базы данных VK Comments Parser

Мигрировано из app/api/v1/infrastructure/models/
в соответствии с fastapi-best-practices
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Типизированный базовый класс SQLAlchemy для моделей

    Используем DeclarativeBase из SQLAlchemy 2.x, чтобы mypy корректно
    воспринимал базовый класс как тип, без необходимости аннотации Any.
    """

    pass


class BaseModel(Base):
    """Базовая модель с общими полями"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать модель в словарь"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря"""
        for key, value in data.items():
            if hasattr(self, key) and key not in [
                "id",
                "created_at",
                "updated_at",
            ]:
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"


# Глобальные модели, которые используются в нескольких модулях
class User(BaseModel):
    """Модель пользователя"""

    __tablename__ = "users"

    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    role = Column(String(50), default="user", nullable=False)


class Group(BaseModel):
    """Модель группы VK"""

    __tablename__ = "vk_groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vk_id = Column(Integer, unique=True, index=True, nullable=False)
    screen_name = Column(String(255), nullable=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    max_posts_to_check = Column(Integer, default=100)
    auto_monitoring_enabled = Column(Boolean, default=False, nullable=False)
    monitoring_interval_minutes = Column(Integer, default=60)
    next_monitoring_at = Column(DateTime(timezone=True), nullable=True)
    monitoring_priority = Column(Integer, default=5)
    last_parsed_at = Column(DateTime(timezone=True), nullable=True)
    total_posts_parsed = Column(Integer, default=0)
    total_comments_found = Column(Integer, default=0)
    monitoring_runs_count = Column(Integer, default=0)
    last_monitoring_success = Column(DateTime(timezone=True), nullable=True)
    last_monitoring_error = Column(Text, nullable=True)
    members_count = Column(Integer, nullable=True)
    is_closed = Column(Boolean, default=False, nullable=False)
    photo_url = Column(String(500), nullable=True)


class Keyword(BaseModel):
    """Модель ключевого слова"""

    __tablename__ = "keywords"

    word = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    group_id = Column(
        Integer, index=True, nullable=True
    )  # NULL = глобальное ключевое слово


class Comment(BaseModel):
    """Модель комментария"""

    __tablename__ = "vk_comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vk_id = Column(Integer, unique=True, index=True, nullable=False)
    text = Column(Text, nullable=False)
    post_id = Column(Integer, index=True, nullable=False)
    author_id = Column(Integer, index=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    is_viewed = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    published_at = Column(DateTime(timezone=True), nullable=False)
    post_vk_id = Column(Integer, nullable=True)
    author_name = Column(String(200), nullable=True)
    author_screen_name = Column(String(100), nullable=True)
    author_photo_url = Column(String(500), nullable=True)
    likes_count = Column(Integer, default=0)
    parent_comment_id = Column(Integer, index=True, nullable=True)
    has_attachments = Column(Boolean, default=False, nullable=False)
    attachments_info = Column(Text, nullable=True)
    is_processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    matched_keywords_count = Column(Integer, default=0, nullable=False)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)


class Post(BaseModel):
    """Модель поста VK"""

    __tablename__ = "vk_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vk_id = Column(Integer, index=True, nullable=False)
    group_id = Column(Integer, index=True, nullable=False)
    text = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    published_at = Column(DateTime(timezone=True), nullable=False)
    vk_owner_id = Column(Integer, default=0, nullable=False)
    likes_count = Column(Integer, default=0)
    reposts_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    is_parsed = Column(Boolean, default=False, nullable=False)
    parsed_at = Column(DateTime(timezone=True), nullable=True)
    has_attachments = Column(Boolean, default=False, nullable=False)
    attachments_info = Column(Text, nullable=True)


class ErrorReport(BaseModel):
    """Модель отчета об ошибке"""

    __tablename__ = "error_reports"

    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    resolved = Column(Integer, default=0, nullable=False)


class CommentKeywordMatch(BaseModel):
    """Модель соответствия комментария ключевому слову"""

    __tablename__ = "comment_keyword_matches"

    comment_id = Column(Integer, index=True, nullable=False)
    keyword_id = Column(Integer, index=True, nullable=False)
    group_id = Column(Integer, index=True, nullable=False)
    matched_at = Column(DateTime(timezone=True), server_default=func.now())


# Импорт всех моделей для Alembic
__all__ = [
    "Base",
    "BaseModel",
    "User",
    "Group",
    "Keyword",
    "Comment",
    "Post",
    "ErrorReport",
    "CommentKeywordMatch",
]
