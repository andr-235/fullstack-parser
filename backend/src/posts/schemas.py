"""
Pydantic схемы для модуля Posts
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class PostCreate(BaseModel):
    """Схема для создания поста"""
    vk_id: int = Field(..., description="VK ID поста")
    group_id: int = Field(..., description="ID группы")
    author_id: int = Field(..., description="ID автора")
    text: str = Field(..., min_length=1, max_length=10000, description="Текст поста")
    status: str = Field(default="published", description="Статус поста")
    post_type: str = Field(default="text", description="Тип поста")
    likes_count: int = Field(default=0, ge=0, description="Количество лайков")
    comments_count: int = Field(default=0, ge=0, description="Количество комментариев")
    reposts_count: int = Field(default=0, ge=0, description="Количество репостов")
    views_count: int = Field(default=0, ge=0, description="Количество просмотров")
    published_at: Optional[datetime] = Field(None, description="Время публикации")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Вложения")
    hashtags: List[str] = Field(default_factory=list, description="Хештеги")
    mentions: List[str] = Field(default_factory=list, description="Упоминания")
    post_metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")
    
    @validator("status")
    def validate_status(cls, v):
        valid_statuses = ["published", "draft", "archived", "deleted"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
    
    @validator("post_type")
    def validate_post_type(cls, v):
        valid_types = ["text", "photo", "video", "audio", "document", "link", "poll", "mixed"]
        if v not in valid_types:
            raise ValueError(f"Post type must be one of: {valid_types}")
        return v


class PostUpdate(BaseModel):
    """Схема для обновления поста"""
    text: Optional[str] = Field(None, min_length=1, max_length=10000, description="Текст поста")
    status: Optional[str] = Field(None, description="Статус поста")
    post_type: Optional[str] = Field(None, description="Тип поста")
    likes_count: Optional[int] = Field(None, ge=0, description="Количество лайков")
    comments_count: Optional[int] = Field(None, ge=0, description="Количество комментариев")
    reposts_count: Optional[int] = Field(None, ge=0, description="Количество репостов")
    views_count: Optional[int] = Field(None, ge=0, description="Количество просмотров")
    published_at: Optional[datetime] = Field(None, description="Время публикации")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Вложения")
    hashtags: Optional[List[str]] = Field(None, description="Хештеги")
    mentions: Optional[List[str]] = Field(None, description="Упоминания")
    post_metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")
    
    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["published", "draft", "archived", "deleted"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
    
    @validator("post_type")
    def validate_post_type(cls, v):
        if v is not None:
            valid_types = ["text", "photo", "video", "audio", "document", "link", "poll", "mixed"]
            if v not in valid_types:
                raise ValueError(f"Post type must be one of: {valid_types}")
        return v


class PostResponse(BaseModel):
    """Схема для ответа с постом"""
    id: int
    vk_id: int
    group_id: int
    author_id: int
    text: str
    status: str
    post_type: str
    likes_count: int
    comments_count: int
    reposts_count: int
    views_count: int
    published_at: Optional[datetime]
    attachments: List[Dict[str, Any]]
    hashtags: List[str]
    mentions: List[str]
    post_metadata: Dict[str, Any]
    is_parsed: bool
    parsed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    comments: Optional[List["CommentResponse"]] = None
    
    class Config:
        from_attributes = True


class PostFilter(BaseModel):
    """Схема для фильтрации постов"""
    group_id: Optional[int] = Field(None, description="Фильтр по группе")
    author_id: Optional[int] = Field(None, description="Фильтр по автору")
    status: Optional[str] = Field(None, description="Фильтр по статусу")
    post_type: Optional[str] = Field(None, description="Фильтр по типу")
    search_text: Optional[str] = Field(None, description="Поиск по тексту")
    limit: int = Field(default=50, ge=1, le=1000, description="Лимит записей")
    offset: int = Field(default=0, ge=0, description="Смещение")
    order_by: str = Field(default="created_at", description="Поле для сортировки")
    order_direction: str = Field(default="desc", description="Направление сортировки")
    
    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["published", "draft", "archived", "deleted"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
    
    @validator("post_type")
    def validate_post_type(cls, v):
        if v is not None:
            valid_types = ["text", "photo", "video", "audio", "document", "link", "poll", "mixed"]
            if v not in valid_types:
                raise ValueError(f"Post type must be one of: {valid_types}")
        return v


class PostListResponse(BaseModel):
    """Схема для ответа со списком постов"""
    posts: List[PostResponse]
    total: int
    limit: int
    offset: int


class PostStats(BaseModel):
    """Схема для статистики постов"""
    total_posts: int
    avg_likes_per_post: float
    parsed_posts: int


class PostBulkUpdate(BaseModel):
    """Схема для массового обновления постов"""
    post_ids: List[int] = Field(..., min_items=1, description="Список ID постов")
    update_data: Dict[str, Any] = Field(..., description="Данные для обновления")


# Forward reference для CommentResponse
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from comments.schemas import CommentResponse
