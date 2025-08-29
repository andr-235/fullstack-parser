"""
Стандартизированные схемы ответов для API v1
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from uuid import uuid4


class MetaInfo(BaseModel):
    """Метаданные ответа"""
    request_id: str = str(uuid4())
    timestamp: str = datetime.utcnow().isoformat()
    processing_time: Optional[float] = None
    cached: bool = False


class PaginationInfo(BaseModel):
    """Информация о пагинации"""
    page: int
    size: int
    total: int
    has_next: bool
    has_prev: bool
    total_pages: int


class SuccessResponse(BaseModel):
    """Стандартизированный успешный ответ"""
    data: Any
    pagination: Optional[PaginationInfo] = None
    meta: MetaInfo


class ErrorDetail(BaseModel):
    """Детали ошибки"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Стандартизированный ответ с ошибкой"""
    error: ErrorDetail
    meta: MetaInfo
