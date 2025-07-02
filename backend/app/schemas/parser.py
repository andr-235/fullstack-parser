"""
Pydantic схемы для парсинга и статистики
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ParseTaskCreate(BaseModel):
    """Схема для запуска задачи парсинга"""

    group_id: int = Field(..., description="ID группы для парсинга")
    max_posts: Optional[int] = Field(None, description="Максимальное количество постов")
    force_reparse: bool = Field(
        default=False, description="Принудительно перепарсить уже обработанные посты"
    )


class ParseTaskResponse(BaseModel):
    """Результат задачи парсинга"""

    task_id: str = Field(..., description="ID задачи")
    group_id: int = Field(..., description="ID группы")
    status: str = Field(..., description="Статус задачи (running, completed, failed)")
    started_at: datetime = Field(..., description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    stats: Optional[dict[str, Any]] = Field(None, description="Статистика парсинга")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")


class ParseStats(BaseModel):
    """Статистика парсинга"""

    posts_processed: int = Field(default=0, description="Обработано постов")
    comments_found: int = Field(default=0, description="Найдено комментариев")
    comments_with_keywords: int = Field(
        default=0, description="Комментариев с ключевыми словами"
    )
    new_comments: int = Field(default=0, description="Новых комментариев")
    keyword_matches: int = Field(default=0, description="Совпадений ключевых слов")
    duration_seconds: Optional[float] = Field(
        None, description="Продолжительность в секундах"
    )


class GlobalStats(BaseModel):
    """Общая статистика системы"""

    total_groups: int
    active_groups: int
    total_keywords: int
    active_keywords: int
    total_comments: int
    comments_with_keywords: int
    last_parse_time: Optional[datetime]


class DashboardStats(BaseModel):
    """Статистика для дашборда"""

    today_comments: int
    today_matches: int
    week_comments: int
    week_matches: int
    top_groups: list[dict]
    top_keywords: list[dict]
    recent_activity: list[dict]
