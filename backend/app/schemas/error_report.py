"""
Схемы для отчетов об ошибках
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class ErrorSeverity(str, Enum):
    """Уровни серьезности ошибок"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(str, Enum):
    """Типы ошибок"""

    VALIDATION = "validation"
    DATABASE = "database"
    API = "api"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ErrorContext(BaseModel):
    """Контекст ошибки"""

    user_id: Optional[int] = None
    group_id: Optional[int] = None
    vk_id: Optional[int] = None
    screen_name: Optional[str] = None
    operation: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class ErrorEntry(BaseModel):
    """Запись об ошибке"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    context: Optional[ErrorContext] = None
    stack_trace: Optional[str] = None


class ErrorReport(BaseSchema):
    """Отчет об ошибках"""

    report_id: str = Field(..., description="Уникальный ID отчета")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    operation: str = Field(
        ..., description="Операция, при которой произошли ошибки"
    )
    total_errors: int = Field(..., description="Общее количество ошибок")
    errors: List[ErrorEntry] = Field(default_factory=list)
    summary: Dict[str, int] = Field(
        default_factory=dict
    )  # Количество ошибок по типам
    recommendations: List[str] = Field(default_factory=list)


class GroupLoadErrorReport(ErrorReport):
    """Специализированный отчет для ошибок загрузки групп"""

    groups_processed: int = Field(
        ..., description="Количество обработанных групп"
    )
    groups_successful: int = Field(
        ..., description="Количество успешно загруженных групп"
    )
    groups_failed: int = Field(..., description="Количество групп с ошибками")
    groups_skipped: int = Field(
        ..., description="Количество пропущенных групп"
    )
    processing_time_seconds: float = Field(
        ..., description="Время обработки в секундах"
    )


class ErrorReportResponse(BaseModel):
    """Ответ с отчетом об ошибках"""

    success: bool
    report: Optional[ErrorReport] = None
    message: str
