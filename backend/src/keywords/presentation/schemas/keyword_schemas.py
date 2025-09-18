"""
Pydantic схемы для API ключевых слов
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class KeywordBase(BaseModel):
    """Базовая схема ключевого слова"""

    word: str = Field(..., min_length=1, max_length=255, description="Ключевое слово")
    description: Optional[str] = Field(None, max_length=1000, description="Описание")
    category_name: Optional[str] = Field(None, max_length=100, description="Категория")
    priority: int = Field(5, ge=1, le=10, description="Приоритет (1-10)")
    group_id: Optional[int] = Field(None, description="ID группы")


class KeywordCreate(KeywordBase):
    """Схема для создания ключевого слова"""
    pass


class KeywordUpdate(BaseModel):
    """Схема для обновления ключевого слова"""

    word: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category_name: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=1, le=10)
    group_id: Optional[int] = Field(None)


class KeywordResponse(BaseModel):
    """Схема ответа для ключевого слова"""

    id: int
    word: str
    description: Optional[str]
    category_name: Optional[str]
    priority: int
    is_active: bool
    is_archived: bool
    match_count: int
    group_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KeywordsListResponse(BaseModel):
    """Схема ответа для списка ключевых слов"""

    keywords: list[KeywordResponse]
    total: int
    limit: int
    offset: int


class KeywordStats(BaseModel):
    """Схема статистики ключевых слов"""

    total_keywords: int = Field(..., description="Общее количество ключевых слов")
    active_keywords: int = Field(..., description="Количество активных ключевых слов")
    archived_keywords: int = Field(..., description="Количество архивированных ключевых слов")
    recent_keywords: int = Field(..., description="Количество новых ключевых слов за неделю")


class KeywordFilterParams(BaseModel):
    """Параметры фильтрации для запросов"""

    active_only: bool = True
    category: Optional[str] = None
    search: Optional[str] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)