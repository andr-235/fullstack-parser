"""
Pydantic схемы для VK комментариев
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampMixin, IDMixin


class VKCommentBase(BaseModel):
    """Базовая схема VK комментария"""
    text: str = Field(..., description="Текст комментария")
    author_id: int = Field(..., description="ID автора комментария")
    author_name: Optional[str] = Field(None, description="Имя автора")
    published_at: datetime = Field(..., description="Дата публикации комментария")


class VKCommentResponse(VKCommentBase, IDMixin, TimestampMixin, BaseSchema):
    """Схема ответа VK комментария"""
    vk_id: int = Field(..., description="ID комментария в ВК")
    post_id: int = Field(..., description="ID поста")
    author_screen_name: Optional[str] = Field(None, description="Короткое имя автора")
    author_photo_url: Optional[str] = Field(None, description="URL фото автора")
    likes_count: int = Field(default=0, description="Количество лайков")
    parent_comment_id: Optional[int] = Field(None, description="ID родительского комментария")
    has_attachments: bool = Field(default=False, description="Есть ли вложения")
    matched_keywords_count: int = Field(default=0, description="Количество найденных ключевых слов")
    is_processed: bool = Field(default=False, description="Обработан ли комментарий")
    processed_at: Optional[datetime] = Field(None, description="Когда был обработан")


class CommentWithKeywords(VKCommentResponse):
    """Комментарий с найденными ключевыми словами"""
    matched_keywords: List[str] = Field(default=[], description="Найденные ключевые слова")
    keyword_matches: List[dict] = Field(default=[], description="Детали совпадений")


class CommentSearchParams(BaseModel):
    """Параметры поиска комментариев"""
    group_id: Optional[int] = None
    keyword_id: Optional[int] = None
    author_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    skip: int = 0
    limit: int = 100 