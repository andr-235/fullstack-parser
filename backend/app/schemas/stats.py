"""
Pydantic-схемы для данных статистики.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class GlobalStats(BaseModel):
    """Глобальная статистика системы."""

    total_groups: int = Field(..., description="Всего групп")
    active_groups: int = Field(..., description="Активных групп")
    total_keywords: int = Field(..., description="Всего ключевых слов")
    active_keywords: int = Field(..., description="Активных ключевых слов")
    total_comments: int = Field(..., description="Всего комментариев")
    comments_with_keywords: int = Field(
        ..., description="Комментариев с ключевыми словами"
    )
    last_parse_time: Optional[datetime] = Field(
        None, description="Время последнего парсинга"
    )


class DashboardTopItem(BaseModel):
    """Элемент топа для дашборда."""

    name: str
    count: int


class RecentActivityItem(BaseModel):
    """Элемент недавней активности."""

    id: int
    type: str
    message: str
    timestamp: datetime


class DashboardStats(BaseModel):
    """Статистика для дашборда."""

    today_comments: int
    today_matches: int
    week_comments: int
    week_matches: int
    top_groups: List[DashboardTopItem]
    top_keywords: List[DashboardTopItem]
    recent_activity: List[RecentActivityItem]
