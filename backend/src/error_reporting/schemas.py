"""
Pydantic схемы для модуля Error Reporting

Определяет входные и выходные модели данных для API отчетов об ошибках
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

from ..pagination import PaginatedResponse


class ErrorReportBase(BaseModel):
    """Базовая схема отчета об ошибке"""

    model_config = ConfigDict(from_attributes=True)

    error_type: str = Field(..., description="Тип ошибки")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Уровень серьезности"
    )
    message: str = Field(
        ..., description="Сообщение об ошибке", min_length=1, max_length=10000
    )
    stack_trace: Optional[str] = Field(
        None, description="Трассировка стека", max_length=50000
    )
    operation: Optional[str] = Field(
        None, description="Операция, во время которой произошла ошибка"
    )
    user_id: Optional[str] = Field(None, description="ID пользователя")
    request_id: Optional[str] = Field(None, description="ID запроса")
    additional_context: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительный контекст"
    )


class ErrorReportCreate(ErrorReportBase):
    """Схема для создания отчета об ошибке"""

    @field_validator("error_type")
    @classmethod
    def validate_error_type(cls, v):
        valid_types = [
            "network",
            "database",
            "api",
            "validation",
            "authentication",
            "authorization",
            "business_logic",
            "external_service",
            "system",
            "unknown",
        ]
        if v not in valid_types:
            raise ValueError(
                f'Invalid error type. Must be one of: {", ".join(valid_types)}'
            )
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        valid_severities = ["low", "medium", "high", "critical"]
        if v not in valid_severities:
            raise ValueError(
                f'Invalid severity level. Must be one of: {", ".join(valid_severities)}'
            )
        return v


class ErrorReportContext(BaseModel):
    """Схема контекста ошибки"""

    model_config = ConfigDict(from_attributes=True)

    operation: Optional[str] = Field(None, description="Операция")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    session_id: Optional[str] = Field(None, description="ID сессии")
    request_id: Optional[str] = Field(None, description="ID запроса")
    endpoint: Optional[str] = Field(None, description="Endpoint")
    method: Optional[str] = Field(None, description="HTTP метод")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")
    additional_data: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные данные"
    )


class ErrorReportStatus(BaseModel):
    """Схема статуса отчета об ошибке"""

    model_config = ConfigDict(from_attributes=True)

    current: str = Field(..., description="Текущий статус")
    acknowledged: bool = Field(..., description="Подтвержден")
    acknowledged_by: Optional[str] = Field(None, description="Кто подтвердил")
    acknowledged_at: Optional[str] = Field(
        None, description="Когда подтвержден"
    )
    resolved: bool = Field(..., description="Разрешен")
    resolved_at: Optional[str] = Field(None, description="Когда разрешен")
    resolution_notes: Optional[str] = Field(
        None, description="Заметки о разрешении"
    )


class ErrorReportTimestamps(BaseModel):
    """Схема временных меток отчета об ошибке"""

    model_config = ConfigDict(from_attributes=True)

    created_at: str = Field(..., description="Время создания")
    updated_at: str = Field(..., description="Время обновления")
    time_to_acknowledge: Optional[float] = Field(
        None, description="Время до подтверждения (часы)"
    )
    time_to_resolve: Optional[float] = Field(
        None, description="Время до разрешения (часы)"
    )


class ErrorReportMetadata(BaseModel):
    """Схема метаданных отчета об ошибке"""

    model_config = ConfigDict(from_attributes=True)

    version: int = Field(..., description="Версия отчета")
    is_critical: bool = Field(..., description="Критическая ошибка")
    is_pending: bool = Field(..., description="Ожидает обработки")
    is_resolved: bool = Field(..., description="Разрешена")


class ErrorReportResponse(BaseModel):
    """Полная схема ответа отчета об ошибке"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="ID отчета")
    error_type: str = Field(..., description="Тип ошибки")
    severity: str = Field(..., description="Уровень серьезности")
    message: str = Field(..., description="Сообщение об ошибке")
    stack_trace: Optional[str] = Field(None, description="Трассировка стека")
    context: ErrorReportContext = Field(..., description="Контекст ошибки")
    status: ErrorReportStatus = Field(..., description="Статус отчета")
    timestamps: ErrorReportTimestamps = Field(
        ..., description="Временные метки"
    )
    metadata: ErrorReportMetadata = Field(..., description="Метаданные")


class ErrorReportsListResponse(BaseModel):
    """Схема ответа списка отчетов об ошибках"""

    model_config = ConfigDict(from_attributes=True)

    items: List[ErrorReportResponse] = Field(..., description="Список отчетов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Общее количество страниц")
    has_next: bool = Field(..., description="Есть следующая страница")
    has_prev: bool = Field(..., description="Есть предыдущая страница")


class ErrorReportAcknowledgeRequest(BaseModel):
    """Схема запроса на подтверждение отчета"""

    acknowledged_by: str = Field(
        ..., description="Кто подтверждает отчет", min_length=1
    )


class ErrorReportResolveRequest(BaseModel):
    """Схема запроса на разрешение отчета"""

    resolution_notes: Optional[str] = Field(
        None, description="Заметки о разрешении", max_length=10000
    )


class ErrorReportBulkAcknowledgeRequest(BaseModel):
    """Схема запроса на массовое подтверждение отчетов"""

    report_ids: List[str] = Field(
        default_factory=list,
        description="Список ID отчетов",
        min_length=1,
        max_length=100,
    )
    acknowledged_by: str = Field(
        ..., description="Кто подтверждает отчеты", min_length=1
    )


class ErrorReportBulkAcknowledgeResponse(BaseModel):
    """Схема ответа на массовое подтверждение"""

    model_config = ConfigDict(from_attributes=True)

    successful: List[str] = Field(..., description="Успешно подтвержденные ID")
    failed: List[Dict[str, Any]] = Field(
        ..., description="Неудачные подтверждения"
    )
    total_processed: int = Field(..., description="Всего обработано")
    success_count: int = Field(..., description="Количество успешных")
    failure_count: int = Field(..., description="Количество неудачных")


class ErrorReportStatisticsResponse(BaseModel):
    """Схема ответа статистики по ошибкам"""

    model_config = ConfigDict(from_attributes=True)

    period_days: int = Field(..., description="Период в днях")
    total_reports: int = Field(..., description="Общее количество отчетов")
    acknowledged_reports: int = Field(..., description="Подтвержденные отчеты")
    resolved_reports: int = Field(..., description="Разрешенные отчеты")
    critical_reports: int = Field(..., description="Критические отчеты")
    acknowledgment_rate: float = Field(
        ..., description="Процент подтверждения"
    )
    resolution_rate: float = Field(..., description="Процент разрешения")
    error_types_stats: Dict[str, int] = Field(
        ..., description="Статистика по типам ошибок"
    )
    severity_stats: Dict[str, int] = Field(
        ..., description="Статистика по серьезности"
    )
    operation_stats: Dict[str, int] = Field(
        ..., description="Статистика по операциям"
    )


class ErrorReportTimeoutCheck(BaseModel):
    """Схема проверки таймаутов отчета"""

    model_config = ConfigDict(from_attributes=True)

    report_id: str = Field(..., description="ID отчета")
    acknowledge_timeout: bool = Field(
        ..., description="Просрочено подтверждение"
    )
    resolve_timeout: bool = Field(..., description="Просрочено разрешение")
    warnings: List[str] = Field(..., description="Предупреждения")


class ErrorReportSummaryResponse(BaseModel):
    """Схема ответа сводки отчетов об ошибках"""

    model_config = ConfigDict(from_attributes=True)

    total_reports: int = Field(..., description="Общее количество отчетов")
    metrics: Dict[str, Any] = Field(..., description="Метрики")
    severity_distribution: Dict[str, int] = Field(
        ..., description="Распределение по серьезности"
    )
    most_common_error_type: Optional[str] = Field(
        None, description="Самый распространенный тип ошибки"
    )
    recommendations: List[str] = Field(..., description="Рекомендации")
    generated_at: str = Field(..., description="Время генерации")


class ErrorReportExportRequest(BaseModel):
    """Схема запроса на экспорт отчетов"""

    format: Literal["json", "csv"] = Field(
        "json", description="Формат экспорта"
    )
    start_date: Optional[datetime] = Field(None, description="Начальная дата")
    end_date: Optional[datetime] = Field(None, description="Конечная дата")
    error_type: Optional[str] = Field(
        None, description="Фильтр по типу ошибки"
    )
    severity: Optional[str] = Field(None, description="Фильтр по серьезности")
    include_resolved: bool = Field(True, description="Включать разрешенные")
    max_records: int = Field(
        10000, description="Максимальное количество записей"
    )


class ErrorReportCleanupRequest(BaseModel):
    """Схема запроса на очистку отчетов"""

    max_age_days: int = Field(365, description="Максимальный возраст в днях")
    dry_run: bool = Field(False, description="Тестовый запуск")


class ErrorReportCleanupResponse(BaseModel):
    """Схема ответа на очистку отчетов"""

    model_config = ConfigDict(from_attributes=True)

    deleted_count: int = Field(..., description="Количество удаленных отчетов")
    total_before: int = Field(..., description="Количество до очистки")
    total_after: int = Field(..., description="Количество после очистки")
    dry_run: bool = Field(..., description="Был ли это тестовый запуск")


class ErrorReportFilterParams(BaseModel):
    """Параметры фильтрации отчетов об ошибках"""

    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")
    error_type: Optional[str] = Field(
        None, description="Фильтр по типу ошибки"
    )
    severity: Optional[str] = Field(None, description="Фильтр по серьезности")
    operation: Optional[str] = Field(None, description="Фильтр по операции")
    acknowledged: Optional[bool] = Field(
        None, description="Фильтр по подтверждению"
    )
    resolved: Optional[bool] = Field(None, description="Фильтр по разрешению")
    start_date: Optional[datetime] = Field(None, description="Начальная дата")
    end_date: Optional[datetime] = Field(None, description="Конечная дата")


# Экспорт всех схем
__all__ = [
    "ErrorReportBase",
    "ErrorReportCreate",
    "ErrorReportContext",
    "ErrorReportStatus",
    "ErrorReportTimestamps",
    "ErrorReportMetadata",
    "ErrorReportResponse",
    "ErrorReportsListResponse",
    "ErrorReportAcknowledgeRequest",
    "ErrorReportResolveRequest",
    "ErrorReportBulkAcknowledgeRequest",
    "ErrorReportBulkAcknowledgeResponse",
    "ErrorReportStatisticsResponse",
    "ErrorReportTimeoutCheck",
    "ErrorReportSummaryResponse",
    "ErrorReportExportRequest",
    "ErrorReportCleanupRequest",
    "ErrorReportCleanupResponse",
    "ErrorReportFilterParams",
]
