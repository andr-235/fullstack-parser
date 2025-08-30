"""
Pydantic схемы для модуля Keywords

Определяет входные и выходные модели данных для API управления ключевыми словами
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class KeywordCategory(BaseModel):
    """Категория ключевого слова"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ..., description="Название категории", min_length=1, max_length=100
    )
    description: Optional[str] = Field(
        None, description="Описание категории", max_length=500
    )


class KeywordStatus(BaseModel):
    """Статус ключевого слова"""

    model_config = ConfigDict(from_attributes=True)

    is_active: bool = Field(True, description="Активно ли ключевое слово")
    is_archived: bool = Field(
        False, description="Архивировано ли ключевое слово"
    )


class KeywordBase(BaseModel):
    """Базовая схема ключевого слова"""

    word: str = Field(
        ..., description="Ключевое слово", min_length=1, max_length=255
    )
    category: Optional[KeywordCategory] = Field(
        None, description="Категория ключевого слова"
    )
    description: Optional[str] = Field(
        None, description="Описание ключевого слова", max_length=1000
    )
    priority: int = Field(
        5, description="Приоритет ключевого слова", ge=1, le=10
    )


class KeywordCreate(BaseModel):
    """Схема для создания ключевого слова"""

    word: str = Field(
        ..., description="Ключевое слово", min_length=1, max_length=255
    )
    category_name: Optional[str] = Field(
        None, description="Название категории", min_length=1, max_length=100
    )
    category_description: Optional[str] = Field(
        None, description="Описание категории", max_length=500
    )
    description: Optional[str] = Field(
        None, description="Описание ключевого слова", max_length=1000
    )
    priority: int = Field(
        5, description="Приоритет ключевого слова", ge=1, le=10
    )


class KeywordUpdate(BaseModel):
    """Схема для обновления ключевого слова"""

    word: Optional[str] = Field(
        None, description="Ключевое слово", min_length=1, max_length=255
    )
    category_name: Optional[str] = Field(
        None, description="Название категории", min_length=1, max_length=100
    )
    category_description: Optional[str] = Field(
        None, description="Описание категории", max_length=500
    )
    description: Optional[str] = Field(
        None, description="Описание ключевого слова", max_length=1000
    )
    priority: Optional[int] = Field(
        None, description="Приоритет ключевого слова", ge=1, le=10
    )


class KeywordResponse(BaseModel):
    """Схема ответа с ключевым словом"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID ключевого слова")
    word: str = Field(..., description="Ключевое слово")
    category: Optional[KeywordCategory] = Field(
        None, description="Категория ключевого слова"
    )
    status: KeywordStatus = Field(..., description="Статус ключевого слова")
    description: Optional[str] = Field(
        None, description="Описание ключевого слова"
    )
    priority: int = Field(..., description="Приоритет ключевого слова")
    match_count: int = Field(0, description="Количество совпадений")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class KeywordsListResponse(PaginatedResponse):
    """Схема ответа со списком ключевых слов"""

    items: List[KeywordResponse] = Field(
        ..., description="Список ключевых слов"
    )


class KeywordsSearchRequest(BaseModel):
    """Схема для поиска ключевых слов"""

    query: str = Field(
        ..., description="Поисковый запрос", min_length=1, max_length=255
    )
    active_only: bool = Field(
        True, description="Только активные ключевые слова"
    )
    category: Optional[str] = Field(None, description="Фильтр по категории")
    limit: int = Field(50, description="Количество результатов", ge=1, le=100)
    offset: int = Field(0, description="Смещение", ge=0)


class KeywordsFilterRequest(BaseModel):
    """Схема для фильтрации ключевых слов"""

    active_only: bool = Field(
        True, description="Только активные ключевые слова"
    )
    category: Optional[str] = Field(None, description="Фильтр по категории")
    priority_min: Optional[int] = Field(
        None, description="Минимальный приоритет", ge=1, le=10
    )
    priority_max: Optional[int] = Field(
        None, description="Максимальный приоритет", ge=1, le=10
    )
    match_count_min: Optional[int] = Field(
        None, description="Минимальное количество совпадений", ge=0
    )
    match_count_max: Optional[int] = Field(
        None, description="Максимальное количество совпадений", ge=0
    )
    limit: int = Field(50, description="Количество результатов", ge=1, le=100)
    offset: int = Field(0, description="Смещение", ge=0)


class KeywordBulkAction(BaseModel):
    """Схема для массовых операций с ключевыми словами"""

    keyword_ids: List[int] = Field(
        ..., description="ID ключевых слов", min_length=1, max_length=100
    )
    action: str = Field(
        ...,
        description="Действие",
        enum=["activate", "deactivate", "archive", "delete"],
    )


class KeywordBulkCreate(BaseModel):
    """Схема для массового создания ключевых слов"""

    keywords: List[KeywordCreate] = Field(
        ..., description="Список ключевых слов", min_length=1, max_length=100
    )


class KeywordBulkResponse(BaseModel):
    """Схема ответа для массовых операций"""

    total_requested: int = Field(..., description="Общее количество запрошено")
    successful: int = Field(..., description="Успешных операций")
    failed: int = Field(..., description="Неудачных операций")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Ошибки"
    )


class KeywordStats(BaseModel):
    """Статистика ключевых слов"""

    total_keywords: int = Field(
        ..., description="Общее количество ключевых слов"
    )
    active_keywords: int = Field(..., description="Активных ключевых слов")
    archived_keywords: int = Field(
        ..., description="Архивированных ключевых слов"
    )
    total_categories: int = Field(
        ..., description="Общее количество категорий"
    )
    total_matches: int = Field(..., description="Общее количество совпадений")
    avg_matches_per_keyword: float = Field(
        ..., description="Среднее количество совпадений на ключевое слово"
    )
    top_categories: List[Dict[str, Any]] = Field(
        ..., description="Топ категорий"
    )


class KeywordCategoryStats(BaseModel):
    """Статистика категории ключевых слов"""

    category_name: str = Field(..., description="Название категории")
    keyword_count: int = Field(..., description="Количество ключевых слов")
    active_count: int = Field(..., description="Активных ключевых слов")
    total_matches: int = Field(..., description="Общее количество совпадений")


class KeywordCategoriesResponse(BaseModel):
    """Схема ответа со списком категорий"""

    categories: List[str] = Field(..., description="Список категорий")
    categories_with_stats: List[KeywordCategoryStats] = Field(
        ..., description="Категории со статистикой"
    )


class KeywordMatch(BaseModel):
    """Совпадение ключевого слова"""

    model_config = ConfigDict(from_attributes=True)

    keyword_id: int = Field(..., description="ID ключевого слова")
    comment_id: int = Field(..., description="ID комментария")
    word_position: int = Field(..., description="Позиция слова в комментарии")
    confidence: float = Field(
        ..., description="Уверенность совпадения", ge=0.0, le=1.0
    )
    matched_at: datetime = Field(..., description="Время совпадения")


class KeywordMatchesResponse(BaseModel):
    """Схема ответа с совпадениями ключевых слов"""

    keyword_id: int = Field(..., description="ID ключевого слова")
    matches: List[KeywordMatch] = Field(..., description="Список совпадений")
    total_matches: int = Field(..., description="Общее количество совпадений")


class KeywordImportRequest(BaseModel):
    """Схема для импорта ключевых слов"""

    keywords_data: str = Field(
        ..., description="Данные ключевых слов в формате JSON", min_length=1
    )
    update_existing: bool = Field(
        False, description="Обновлять существующие ключевые слова"
    )
    skip_duplicates: bool = Field(True, description="Пропускать дубликаты")


class KeywordExportRequest(BaseModel):
    """Схема для экспорта ключевых слов"""

    format: str = Field(
        "json", description="Формат экспорта", enum=["json", "csv", "txt"]
    )
    active_only: bool = Field(
        True, description="Экспортировать только активные"
    )
    category: Optional[str] = Field(None, description="Фильтр по категории")


class KeywordExportResponse(BaseModel):
    """Схема ответа для экспорта"""

    export_data: str = Field(..., description="Экспортированные данные")
    format: str = Field(..., description="Формат экспорта")
    total_exported: int = Field(
        ..., description="Общее количество экспортировано"
    )
    filename: Optional[str] = Field(None, description="Имя файла")


class KeywordValidationRequest(BaseModel):
    """Схема для валидации ключевых слов"""

    words: List[str] = Field(
        ...,
        description="Список слов для валидации",
        min_length=1,
        max_length=100,
    )


class KeywordValidationResponse(BaseModel):
    """Схема ответа валидации"""

    valid_keywords: List[str] = Field(
        ..., description="Валидные ключевые слова"
    )
    invalid_keywords: List[str] = Field(
        ..., description="Невалидные ключевые слова"
    )
    suggestions: Dict[str, List[str]] = Field(
        ..., description="Предложения для невалидных слов"
    )


# Экспорт всех схем
__all__ = [
    "KeywordCategory",
    "KeywordStatus",
    "KeywordBase",
    "KeywordCreate",
    "KeywordUpdate",
    "KeywordResponse",
    "KeywordsListResponse",
    "KeywordsSearchRequest",
    "KeywordsFilterRequest",
    "KeywordBulkAction",
    "KeywordBulkCreate",
    "KeywordBulkResponse",
    "KeywordStats",
    "KeywordCategoryStats",
    "KeywordCategoriesResponse",
    "KeywordMatch",
    "KeywordMatchesResponse",
    "KeywordImportRequest",
    "KeywordExportRequest",
    "KeywordExportResponse",
    "KeywordValidationRequest",
    "KeywordValidationResponse",
]
