"""
Pydantic схемы для модуля Comments
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from authors.schemas import AuthorResponse


# Константы для валидации
MIN_COMMENT_TEXT_LENGTH = 1
MAX_COMMENT_TEXT_LENGTH = 10000
MIN_SEARCH_TEXT_LENGTH = 2
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
DEFAULT_OFFSET = 0
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 1.0
DEFAULT_MIN_CONFIDENCE = 0.3
MAX_KEYWORDS = 50
DEFAULT_MAX_KEYWORDS = 10
MIN_KEYWORDS_LIST = 1
MAX_KEYWORDS_LIST = 20
MIN_WORD_LENGTH = 3
DEFAULT_KEYWORD_CONFIDENCE = 50
GROWTH_PERIOD_DAYS = 30

from authors.schemas import AuthorResponse


class KeywordMatch(BaseModel):
    """Схема совпадения ключевого слова"""
    keyword: str
    confidence: int
    created_at: datetime


class CommentResponse(BaseModel):
    """Схема комментария для ответа API"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    id: int
    vk_id: int
    group_id: int
    post_id: int
    author_id: int
    text: str
    created_at: datetime
    is_deleted: bool = False
    keyword_matches: List[KeywordMatch] = []
    author: Optional[AuthorResponse] = None


class CommentCreate(BaseModel):
    """Схема для создания комментария"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    vk_id: int
    group_id: int
    post_id: int
    author_id: int
    text: str = Field(..., min_length=MIN_COMMENT_TEXT_LENGTH, max_length=MAX_COMMENT_TEXT_LENGTH)


class CommentUpdate(BaseModel):
    """Схема для обновления комментария"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: Optional[str] = Field(None, min_length=MIN_COMMENT_TEXT_LENGTH, max_length=MAX_COMMENT_TEXT_LENGTH)
    is_deleted: Optional[bool] = None


class CommentFilter(BaseModel):
    """Схема для фильтрации комментариев"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    group_id: Optional[int] = None
    post_id: Optional[int] = None
    author_id: Optional[int] = None
    search_text: Optional[str] = Field(None, min_length=MIN_SEARCH_TEXT_LENGTH)
    is_deleted: Optional[bool] = None
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=DEFAULT_OFFSET, ge=0)


class CommentListResponse(BaseModel):
    """Схема списка комментариев"""

    items: List[CommentResponse]
    total: int
    limit: int
    offset: int


class CommentStats(BaseModel):
    """Схема статистики комментариев"""

    total_comments: int
    comments_by_group: Dict[int, int] = {}
    comments_by_author: Dict[int, int] = {}
    avg_comments_per_group: float


# Схемы для анализа ключевых слов
class KeywordAnalysisRequest(BaseModel):
    """Запрос на анализ ключевых слов"""

    comment_id: int
    min_confidence: float = Field(DEFAULT_MIN_CONFIDENCE, ge=MIN_CONFIDENCE, le=MAX_CONFIDENCE)
    max_keywords: int = Field(DEFAULT_MAX_KEYWORDS, ge=MIN_KEYWORDS_LIST, le=MAX_KEYWORDS)


class KeywordAnalysisResponse(BaseModel):
    """Ответ анализа ключевых слов"""

    comment_id: int
    keywords_found: int
    keywords_created: int
    keywords_updated: int
    status: str


class BatchKeywordAnalysisRequest(BaseModel):
    """Запрос на массовый анализ"""

    comment_ids: List[int] = Field(..., min_items=MIN_KEYWORDS_LIST, max_items=MAX_KEYWORDS_LIST)
    min_confidence: float = Field(DEFAULT_MIN_CONFIDENCE, ge=MIN_CONFIDENCE, le=MAX_CONFIDENCE)
    max_keywords: int = Field(DEFAULT_MAX_KEYWORDS, ge=MIN_KEYWORDS_LIST, le=MAX_KEYWORDS)


class BatchKeywordAnalysisResponse(BaseModel):
    """Ответ массового анализа"""

    total_processed: int
    successful: int
    errors: int
    total_keywords_found: int
    total_keywords_created: int
    total_keywords_updated: int
    results: List[KeywordAnalysisResponse]


class KeywordSearchRequest(BaseModel):
    """Запрос поиска по ключевым словам"""

    keywords: List[str] = Field(..., min_items=MIN_KEYWORDS_LIST, max_items=MAX_KEYWORDS_LIST)
    min_confidence: float = Field(DEFAULT_MIN_CONFIDENCE, ge=MIN_CONFIDENCE, le=MAX_CONFIDENCE)
    limit: int = Field(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(DEFAULT_OFFSET, ge=0)


class KeywordSearchResponse(BaseModel):
    """Ответ поиска по ключевым словам"""

    comments: List[CommentResponse]
    total: int
    limit: int
    offset: int
    keywords: List[str]


class KeywordStatisticsResponse(BaseModel):
    """Статистика ключевых слов"""

    total_keywords: int
    total_matches: int
    categories: Dict[str, Dict[str, int]]
    top_keywords: List[Dict[str, Any]]


