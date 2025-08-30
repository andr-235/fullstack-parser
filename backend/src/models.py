"""
Глобальные модели базы данных VK Comments Parser

Мигрировано из app/api/v1/infrastructure/models/
в соответствии с fastapi-best-practices
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, func
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

    __tablename__ = "groups"

    vk_group_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    screen_name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    members_count = Column(Integer, default=0)
    is_active = Column(Integer, default=1, nullable=False)
    last_parsed_at = Column(DateTime(timezone=True), nullable=True)


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

    __tablename__ = "comments"

    vk_comment_id = Column(String(50), unique=True, index=True, nullable=False)
    vk_post_id = Column(String(50), index=True, nullable=False)
    vk_group_id = Column(String(50), index=True, nullable=False)
    author_id = Column(String(50), index=True, nullable=False)
    author_name = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    date = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)


class Post(BaseModel):
    """Модель поста VK"""

    __tablename__ = "posts"

    vk_post_id = Column(String(50), unique=True, index=True, nullable=False)
    vk_group_id = Column(String(50), index=True, nullable=False)
    author_id = Column(String(50), index=True, nullable=False)
    author_name = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    date = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)


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
