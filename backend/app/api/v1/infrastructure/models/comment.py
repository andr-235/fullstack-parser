"""
Infrastructure модель для VK комментария (DDD)

SQLAlchemy модель для работы с комментариями в Infrastructure Layer
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from .base import BaseModel


class VKCommentModel(BaseModel):
    """Infrastructure модель VK комментария"""

    __tablename__ = "vk_comments"

    # Основная информация
    vk_id = Column(
        Integer, nullable=False, index=True, comment="ID комментария в ВК"
    )
    text = Column(Text, nullable=False, comment="Текст комментария")

    # Связи
    post_id = Column(ForeignKey("vk_posts.id"), nullable=False)
    post_vk_id = Column(
        Integer, comment="ID поста в VK (для формирования ссылок)"
    )

    # Автор комментария
    author_id = Column(
        Integer, nullable=False, comment="ID автора комментария"
    )
    author_name = Column(String(200), comment="Имя автора")
    author_screen_name = Column(String(100), comment="Короткое имя автора")
    author_photo_url = Column(String(500), comment="URL фото автора")

    # Статистика и метаданные
    likes_count = Column(Integer, default=0, comment="Количество лайков")
    reply_to_comment_id = Column(
        Integer, comment="ID комментария, на который отвечают"
    )
    thread_comments_count = Column(
        Integer, default=0, comment="Количество комментариев в треде"
    )

    # Временные метки VK
    date_posted = Column(
        DateTime(timezone=True), comment="Время публикации комментария"
    )

    # Метаданные парсинга
    is_parsed = Column(
        Boolean, default=False, comment="Был ли комментарий обработан"
    )
    parsing_attempts = Column(
        Integer, default=0, comment="Количество попыток парсинга"
    )
    last_parsing_attempt = Column(
        DateTime(timezone=True), comment="Время последней попытки парсинга"
    )

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        return {
            "id": self.id,
            "vk_id": self.vk_id,
            "text": self.text,
            "post_id": self.post_id,
            "post_vk_id": self.post_vk_id,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "author_screen_name": self.author_screen_name,
            "author_photo_url": self.author_photo_url,
            "likes_count": self.likes_count or 0,
            "reply_to_comment_id": self.reply_to_comment_id,
            "thread_comments_count": self.thread_comments_count or 0,
            "date_posted": self.date_posted,
            "is_parsed": self.is_parsed or False,
            "parsing_attempts": self.parsing_attempts or 0,
            "last_parsing_attempt": self.last_parsing_attempt,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_domain_dict(cls, data: Dict[str, Any]) -> "VKCommentModel":
        """Создать модель из словаря Domain Entity"""
        model = cls()

        # Основная информация
        model.vk_id = data.get("vk_id")
        model.text = data.get("text")
        model.post_id = data.get("post_id")
        model.post_vk_id = data.get("post_vk_id")

        # Автор
        model.author_id = data.get("author_id")
        model.author_name = data.get("author_name")
        model.author_screen_name = data.get("author_screen_name")
        model.author_photo_url = data.get("author_photo_url")

        # Статистика
        model.likes_count = data.get("likes_count", 0)
        model.reply_to_comment_id = data.get("reply_to_comment_id")
        model.thread_comments_count = data.get("thread_comments_count", 0)
        model.date_posted = data.get("date_posted")

        # Метаданные парсинга
        model.is_parsed = data.get("is_parsed", False)
        model.parsing_attempts = data.get("parsing_attempts", 0)
        model.last_parsing_attempt = data.get("last_parsing_attempt")

        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        # Основная информация
        if "vk_id" in data:
            self.vk_id = data["vk_id"]
        if "text" in data:
            self.text = data["text"]
        if "post_id" in data:
            self.post_id = data["post_id"]
        if "post_vk_id" in data:
            self.post_vk_id = data["post_vk_id"]

        # Автор
        if "author_id" in data:
            self.author_id = data["author_id"]
        if "author_name" in data:
            self.author_name = data["author_name"]
        if "author_screen_name" in data:
            self.author_screen_name = data["author_screen_name"]
        if "author_photo_url" in data:
            self.author_photo_url = data["author_photo_url"]

        # Статистика
        if "likes_count" in data:
            self.likes_count = data["likes_count"]
        if "reply_to_comment_id" in data:
            self.reply_to_comment_id = data["reply_to_comment_id"]
        if "thread_comments_count" in data:
            self.thread_comments_count = data["thread_comments_count"]
        if "date_posted" in data:
            self.date_posted = data["date_posted"]

        # Метаданные парсинга
        if "is_parsed" in data:
            self.is_parsed = data["is_parsed"]
        if "parsing_attempts" in data:
            self.parsing_attempts = data["parsing_attempts"]
        if "last_parsing_attempt" in data:
            self.last_parsing_attempt = data["last_parsing_attempt"]

    def __repr__(self) -> str:
        return f"<VKCommentModel(id={self.id}, vk_id={self.vk_id}, author_id={self.author_id})>"
