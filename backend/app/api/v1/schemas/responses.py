"""
Стандартизированные схемы ответов для API v1 с DDD архитектурой

Этот модуль содержит Pydantic модели для стандартизированных ответов API,
интегрированных с DDD архитектурой и enterprise-grade middleware.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from uuid import uuid4


class MetaInfo(BaseModel):
    """Метаданные ответа API с DDD интеграцией"""

    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Уникальный ID запроса для трассировки",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Время создания ответа",
    )
    processing_time: Optional[float] = Field(
        default=None, description="Время обработки запроса в секундах"
    )
    cached: bool = Field(
        default=False, description="Был ли ответ получен из кэша"
    )
    version: str = Field(default="v1.6.0", description="Версия API")
    architecture: str = Field(
        default="DDD + Middleware", description="Архитектурный стиль"
    )


class PaginationInfo(BaseModel):
    """Информация о пагинации с enterprise-grade метаданными"""

    page: int = Field(..., description="Текущий номер страницы", ge=1)
    size: int = Field(..., description="Размер страницы", ge=1, le=100)
    total: int = Field(..., description="Общее количество элементов", ge=0)
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")
    total_pages: int = Field(..., description="Общее количество страниц", ge=0)


class SuccessResponse(BaseModel):
    """Стандартизированный успешный ответ с DDD интеграцией"""

    data: Any = Field(..., description="Основные данные ответа")
    pagination: Optional[PaginationInfo] = Field(
        default=None, description="Информация о пагинации (если применимо)"
    )
    meta: MetaInfo = Field(..., description="Метаданные ответа")

    class Config:
        """Pydantic конфигурация"""

        json_encoders = {datetime: lambda v: v.isoformat()}


class ErrorDetail(BaseModel):
    """Детали ошибки с enterprise-grade информацией"""

    code: str = Field(..., description="Код ошибки для программной обработки")
    message: str = Field(
        ..., description="Человеко-читаемое сообщение об ошибке"
    )
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Дополнительные детали ошибки"
    )
    field: Optional[str] = Field(
        default=None, description="Поле, вызвавшее ошибку (для валидации)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Время возникновения ошибки",
    )


class ErrorResponse(BaseModel):
    """Стандартизированный ответ с ошибкой с DDD интеграцией"""

    error: ErrorDetail = Field(..., description="Детали ошибки")
    meta: MetaInfo = Field(..., description="Метаданные ответа")
    suggestions: Optional[List[str]] = Field(
        default_factory=list, description="Предложения по исправлению ошибки"
    )

    class Config:
        """Pydantic конфигурация"""

        json_encoders = {datetime: lambda v: v.isoformat()}


class HealthStatusResponse(BaseModel):
    """Ответ со статусом здоровья системы (DDD Domain объект)"""

    status: str = Field(..., description="Общий статус системы")
    service: str = Field(..., description="Название сервиса")
    version: str = Field(..., description="Версия сервиса")
    components: Dict[str, str] = Field(
        default_factory=dict, description="Статусы компонентов"
    )
    uptime_seconds: Optional[int] = Field(
        default=None, description="Время работы в секундах"
    )
    meta: MetaInfo = Field(..., description="Метаданные ответа")


class ValidationResponse(BaseModel):
    """Ответ валидации с детальной информацией"""

    valid: bool = Field(..., description="Результат валидации")
    issues: Dict[str, List[str]] = Field(
        default_factory=dict, description="Проблемы по секциям/полям"
    )
    total_sections: int = Field(..., description="Общее количество секций")
    sections_with_issues: int = Field(
        default=0, description="Количество секций с проблемами"
    )
    meta: MetaInfo = Field(..., description="Метаданные ответа")


class StatisticsResponse(BaseModel):
    """Ответ со статистикой системы"""

    period_days: int = Field(..., description="Период в днях")
    total_reports: int = Field(..., description="Общее количество отчетов")
    acknowledged_reports: int = Field(
        ..., description="Количество подтвержденных отчетов"
    )
    resolved_reports: int = Field(
        ..., description="Количество разрешенных отчетов"
    )
    critical_reports: int = Field(
        ..., description="Количество критических отчетов"
    )
    acknowledgment_rate: float = Field(
        ..., description="Процент подтверждения", ge=0.0, le=100.0
    )
    resolution_rate: float = Field(
        ..., description="Процент разрешения", ge=0.0, le=100.0
    )
    error_types_stats: Dict[str, int] = Field(
        default_factory=dict, description="Статистика по типам ошибок"
    )
    severity_stats: Dict[str, int] = Field(
        default_factory=dict, description="Статистика по серьезности"
    )
    operation_stats: Dict[str, int] = Field(
        default_factory=dict, description="Статистика по операциям"
    )
    meta: MetaInfo = Field(..., description="Метаданные ответа")
