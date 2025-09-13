"""
Pydantic схемы для API модуля Keywords
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict

from shared.presentation.responses.base_responses import PaginatedResponse


class KeywordCategory(BaseModel):
    """Категория ключевого слова"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class KeywordStatus(BaseModel):
    """Статус ключевого слова"""
    is_active: bool = Field(True)
    is_archived: bool = Field(False)


class KeywordCreate(BaseModel):
    """Схема для создания ключевого слова"""
    word: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(5, ge=1, le=10)


class KeywordUpdate(BaseModel):
    """Схема для обновления ключевого слова"""
    word: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(None, ge=1, le=10)


class KeywordResponse(BaseModel):
    """Схема ответа с ключевым словом"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    word: str
    description: Optional[str]
    priority: int
    match_count: int
    group_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    status: KeywordStatus
    category: Optional[KeywordCategory]


class KeywordsListResponse(PaginatedResponse):
    """Схема ответа со списком ключевых слов"""
    items: List[KeywordResponse]


class KeywordsSearchRequest(BaseModel):
    """Схема для поиска ключевых слов"""
    query: str = Field(..., min_length=1, max_length=255)
    active_only: bool = Field(True)
    category: Optional[str] = Field(None)
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class KeywordsFilterRequest(BaseModel):
    """Схема для фильтрации ключевых слов"""
    active_only: bool = Field(True)
    category: Optional[str] = Field(None)
    priority_min: Optional[int] = Field(None, ge=1, le=10)
    priority_max: Optional[int] = Field(None, ge=1, le=10)
    match_count_min: Optional[int] = Field(None, ge=0)
    match_count_max: Optional[int] = Field(None, ge=0)
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class KeywordBulkAction(BaseModel):
    """Схема для массовых операций"""
    keyword_ids: List[int] = Field(..., min_length=1, max_length=100)
    action: Literal["activate", "deactivate", "archive", "delete"]


class KeywordBulkCreate(BaseModel):
    """Схема для массового создания"""
    keywords: List[KeywordCreate] = Field(..., min_length=1, max_length=100)


class KeywordBulkResponse(BaseModel):
    """Схема ответа для массовых операций"""
    total_requested: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)


class KeywordStats(BaseModel):
    """Статистика ключевых слов"""
    total_keywords: int
    active_keywords: int
    archived_keywords: int
    total_categories: int
    total_matches: int
    avg_matches_per_keyword: float


class KeywordCategoriesResponse(BaseModel):
    """Схема ответа со списком категорий"""
    categories: List[str]
    categories_with_stats: List[Dict[str, Any]]


class KeywordImportRequest(BaseModel):
    """Схема для импорта ключевых слов"""
    keywords_data: str = Field(..., min_length=1)
    update_existing: bool = Field(False)
    skip_duplicates: bool = Field(True)


class KeywordExportRequest(BaseModel):
    """Схема для экспорта ключевых слов"""
    format: Literal["json", "csv", "txt"] = Field("json")
    active_only: bool = Field(True)
    category: Optional[str] = Field(None)


class KeywordExportResponse(BaseModel):
    """Схема ответа для экспорта"""
    export_data: str
    format: str
    total_exported: int
    filename: Optional[str] = None


class KeywordValidationRequest(BaseModel):
    """Схема для валидации ключевых слов"""
    words: List[str] = Field(..., min_length=1, max_length=100)


class KeywordValidationResponse(BaseModel):
    """Схема ответа валидации"""
    valid_keywords: List[str]
    invalid_keywords: List[str]
    suggestions: Dict[str, List[str]]