"""
Pydantic схемы для модуля Comments

Определяет входные и выходные модели данных для API комментариев
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class CommentBase(BaseModel):
    """Базовая схема комментария"""

    vk_comment_id: str = Field(..., description="ID комментария в VK")
    vk_post_id: str = Field(..., description="ID поста в VK")
    vk_group_id: str = Field(..., description="ID группы в VK")
    author_id: str = Field(..., description="ID автора комментария")
    author_name: str = Field(..., description="Имя автора")
    text: str = Field(..., description="Текст комментария")
    likes_count: int = Field(default=0, description="Количество лайков")
    date: datetime = Field(..., description="Дата публикации")


class CommentCreate(CommentBase):
    """Схема для создания комментария"""

    pass


class CommentUpdate(BaseModel):
    """Схема для обновления комментария"""

    is_viewed: Optional[bool] = Field(
        None, description="Отметить как просмотренный"
    )
    is_processed: Optional[bool] = Field(
        None, description="Отметить как обработанный"
    )
    is_archived: Optional[bool] = Field(
        None, description="Архивировать комментарий"
    )


class CommentResponse(CommentBase):
    """Схема ответа с информацией о комментарии"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID в базе данных")
    processed_at: Optional[datetime] = Field(
        None, description="Время обработки"
    )
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(
        ..., description="Время последнего обновления"
    )


class CommentListResponse(PaginatedResponse[CommentResponse]):
    """Схема ответа со списком комментариев"""

    pass


class CommentFilter(BaseModel):
    """Фильтры для поиска комментариев"""

    group_id: Optional[int] = Field(
        None, description="ID группы для фильтрации"
    )
    post_id: Optional[str] = Field(None, description="ID поста для фильтрации")
    author_id: Optional[str] = Field(
        None, description="ID автора для фильтрации"
    )
    is_viewed: Optional[bool] = Field(
        None, description="Показать только просмотренные"
    )
    is_processed: Optional[bool] = Field(
        None, description="Показать только обработанные"
    )
    is_archived: Optional[bool] = Field(
        None, description="Показать только архивированные"
    )
    search_text: Optional[str] = Field(
        None, description="Поиск по тексту комментария"
    )
    date_from: Optional[datetime] = Field(
        None, description="Дата начала периода"
    )
    date_to: Optional[datetime] = Field(None, description="Дата конца периода")


class CommentStats(BaseModel):
    """Статистика комментариев"""

    total_comments: int = Field(
        ..., description="Общее количество комментариев"
    )
    viewed_comments: int = Field(..., description="Количество просмотренных")
    processed_comments: int = Field(..., description="Количество обработанных")
    archived_comments: int = Field(
        ..., description="Количество архивированных"
    )
    avg_likes_per_comment: float = Field(
        ..., description="Среднее количество лайков"
    )


class CommentBulkAction(BaseModel):
    """Массовые действия с комментариями"""

    comment_ids: List[int] = Field(..., description="Список ID комментариев")
    action: str = Field(
        ..., description="Действие: view, process, archive, unarchive"
    )


class CommentBulkResponse(BaseModel):
    """Ответ на массовое действие"""

    success_count: int = Field(..., description="Количество успешных операций")
    error_count: int = Field(..., description="Количество ошибок")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Список ошибок"
    )


# Экспорт всех схем
__all__ = [
    "CommentBase",
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentListResponse",
    "CommentFilter",
    "CommentStats",
    "CommentBulkAction",
    "CommentBulkResponse",
]
