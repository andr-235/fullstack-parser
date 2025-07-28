"""
Pydantic схемы для VK комментариев
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin
from app.schemas.vk_group import VKGroupResponse


class VKCommentBase(BaseModel):
    """
    Базовая схема VK комментария
    """

    text: str = Field(..., description="Текст комментария")
    author_id: int = Field(..., description="ID автора комментария")
    author_name: Optional[str] = Field(None, description="Имя автора")
    published_at: datetime = Field(
        ..., description="Дата публикации комментария"
    )


class VKCommentResponse(VKCommentBase, IDMixin, TimestampMixin, BaseSchema):
    """
    Схема ответа VK комментария
    """

    vk_id: int = Field(..., description="ID комментария в ВК")
    post_id: int = Field(..., description="ID поста")
    post_vk_id: Optional[int] = Field(
        None, description="ID поста в VK (для формирования ссылки)"
    )
    author_screen_name: Optional[str] = Field(
        None, description="Короткое имя автора"
    )
    author_photo_url: Optional[str] = Field(
        None, description="URL фото автора"
    )
    likes_count: int = Field(default=0, description="Количество лайков")
    parent_comment_id: Optional[int] = Field(
        None, description="ID родительского комментария"
    )
    has_attachments: bool = Field(
        default=False, description="Есть ли вложения"
    )
    matched_keywords_count: int = Field(
        default=0, description="Количество найденных ключевых слов"
    )
    is_processed: bool = Field(
        default=False, description="Обработан ли комментарий"
    )
    processed_at: Optional[datetime] = Field(
        None, description="Когда был обработан"
    )
    is_viewed: bool = Field(
        default=False, description="Просмотрен ли комментарий"
    )
    viewed_at: Optional[datetime] = Field(
        None, description="Когда был просмотрен"
    )
    is_archived: bool = Field(
        default=False, description="Архивирован ли комментарий"
    )
    archived_at: Optional[datetime] = Field(
        None, description="Когда был архивирован"
    )
    group: Optional[VKGroupResponse] = None
    matched_keywords: Optional[list[str]] = Field(
        default=None, description="Найденные ключевые слова"
    )


class CommentWithKeywords(VKCommentResponse):
    """
    Комментарий с найденными ключевыми словами
    """

    matched_keywords: list[str] = Field(
        default=[], description="Найденные ключевые слова"
    )
    keyword_matches: list[dict] = Field(
        default=[], description="Детали совпадений"
    )


class CommentUpdateRequest(BaseModel):
    """Схема для обновления статуса комментария"""

    is_viewed: Optional[bool] = None
    is_archived: Optional[bool] = None


class CommentSearchParams(BaseModel):
    """Параметры поиска комментариев"""

    text: Optional[str] = None
    group_id: Optional[int] = None
    keyword_id: Optional[int] = None
    author_id: Optional[int] = None
    author_screen_name: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_viewed: Optional[bool] = None
    is_archived: Optional[bool] = None
    order_by: Optional[str] = None
    order_dir: Optional[str] = None
