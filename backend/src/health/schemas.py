"""
Pydantic схемы для модуля Health

Определяет входные и выходные модели данных для API здоровья
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class HealthStatusResponse(BaseModel):
    """Ответ со статусом здоровья системы"""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Общий статус здоровья")
    service: str = Field(..., description="Название сервиса")
    version: str = Field(..., description="Версия сервиса")
    components: Dict[str, str] = Field(..., description="Статусы компонентов")
    timestamp: str = Field(..., description="Время проверки")
    uptime_seconds: Optional[int] = Field(
        None, description="Время работы в секундах"
    )


class HealthCheckResult(BaseModel):
    """Результат проверки здоровья компонента"""

    model_config = ConfigDict(from_attributes=True)

    component: str = Field(..., description="Название компонента")
    status: str = Field(..., description="Статус компонента")
    response_time_ms: Optional[float] = Field(
        None, description="Время ответа в мс"
    )
    error_message: Optional[str] = Field(
        None, description="Сообщение об ошибке"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные детали"
    )
    checked_at: str = Field(..., description="Время проверки")


class HealthDetailedResponse(BaseModel):
    """Детальный ответ о здоровье системы"""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Общий статус здоровья")
    service: str = Field(..., description="Название сервиса")
    version: str = Field(..., description="Версия сервиса")
    components: Dict[str, str] = Field(..., description="Статусы компонентов")
    timestamp: str = Field(..., description="Время проверки")
    uptime_seconds: Optional[int] = Field(
        None, description="Время работы в секундах"
    )
    system_info: Dict[str, Any] = Field(
        default_factory=dict, description="Информация о системе"
    )


class HealthReadinessResponse(BaseModel):
    """Ответ проверки готовности"""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Статус готовности")
    service: str = Field(..., description="Название сервиса")
    components: Dict[str, str] = Field(
        ..., description="Статусы критических компонентов"
    )
    timestamp: str = Field(..., description="Время проверки")


class HealthLivenessResponse(BaseModel):
    """Ответ проверки живости"""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Статус живости")
    service: str = Field(..., description="Название сервиса")
    uptime_seconds: int = Field(..., description="Время работы в секундах")
    timestamp: str = Field(..., description="Время проверки")


class HealthComponentResponse(BaseModel):
    """Ответ о здоровье компонента"""

    model_config = ConfigDict(from_attributes=True)

    component: str = Field(..., description="Название компонента")
    status: str = Field(..., description="Статус компонента")
    response_time_ms: Optional[float] = Field(
        None, description="Время ответа в мс"
    )
    last_checked: Optional[str] = Field(
        None, description="Время последней проверки"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Детали компонента"
    )


class HealthComponentsResponse(BaseModel):
    """Ответ со статусами всех компонентов"""

    components: Dict[str, Dict[str, Any]] = Field(
        ..., description="Статусы компонентов"
    )
    total_components: int = Field(
        ..., description="Общее количество компонентов"
    )
    healthy_components: int = Field(
        ..., description="Количество здоровых компонентов"
    )
    unhealthy_components: int = Field(
        ..., description="Количество нездоровых компонентов"
    )


class HealthHistoryResponse(BaseModel):
    """Ответ с историей проверок здоровья"""

    history: List[HealthCheckResult] = Field(
        ..., description="История проверок"
    )
    total_checks: int = Field(..., description="Общее количество проверок")
    component_filter: Optional[str] = Field(
        None, description="Фильтр по компоненту"
    )


class HealthMetricsResponse(BaseModel):
    """Ответ с метриками здоровья"""

    model_config = ConfigDict(from_attributes=True)

    total_checks: int = Field(..., description="Общее количество проверок")
    successful_checks: int = Field(..., description="Успешных проверок")
    failed_checks: int = Field(..., description="Неуспешных проверок")
    success_rate: float = Field(..., description="Процент успешности")
    average_response_time_ms: float = Field(
        ..., description="Среднее время ответа"
    )
    timestamp: str = Field(..., description="Время получения метрик")


class HealthSummaryResponse(BaseModel):
    """Ответ со сводкой здоровья"""

    model_config = ConfigDict(from_attributes=True)

    overall_status: str = Field(..., description="Общий статус")
    total_components: int = Field(
        ..., description="Общее количество компонентов"
    )
    healthy_components: int = Field(..., description="Здоровых компонентов")
    unhealthy_components: Dict[str, str] = Field(
        ..., description="Нездоровые компоненты"
    )
    last_check: Optional[str] = Field(
        None, description="Время последней проверки"
    )
    uptime_seconds: Optional[int] = Field(None, description="Время работы")
    metrics: Dict[str, Any] = Field(..., description="Метрики")
    score: Optional[float] = Field(None, description="Оценка здоровья (0-100)")


class HealthExportResponse(BaseModel):
    """Ответ с экспортированными данными здоровья"""

    model_config = ConfigDict(from_attributes=True)

    export_format: str = Field(..., description="Формат экспорта")
    exported_at: str = Field(..., description="Время экспорта")
    health_status: Optional[Dict[str, Any]] = Field(
        None, description="Статус здоровья"
    )
    components_status: Dict[str, Any] = Field(
        ..., description="Статусы компонентов"
    )
    recent_history: List[Dict[str, Any]] = Field(
        ..., description="Недавняя история"
    )
    metrics: Dict[str, Any] = Field(..., description="Метрики")


class HealthTrendsResponse(BaseModel):
    """Ответ с тенденциями здоровья"""

    model_config = ConfigDict(from_attributes=True)

    trend: str = Field(..., description="Тенденция")
    description: str = Field(..., description="Описание тенденции")
    total_checks: int = Field(..., description="Количество проверок")
    healthy_ratio: float = Field(..., description="Доля успешных проверок")
    time_window_minutes: int = Field(
        ..., description="Временное окно в минутах"
    )


class HealthAlert(BaseModel):
    """Алерт о здоровье"""

    model_config = ConfigDict(from_attributes=True)

    alert_type: str = Field(..., description="Тип алерта")
    component: str = Field(..., description="Компонент")
    old_status: str = Field(..., description="Старый статус")
    new_status: str = Field(..., description="Новый статус")
    severity: str = Field(..., description="Серьезность")
    timestamp: str = Field(..., description="Время алерта")
    details: Dict[str, Any] = Field(default_factory=dict, description="Детали")


class HealthReportResponse(BaseModel):
    """Ответ с отчетом о здоровье"""

    model_config = ConfigDict(from_attributes=True)

    report_generated_at: str = Field(..., description="Время генерации отчета")
    overall_score: float = Field(..., description="Общая оценка (0-100)")
    status: str = Field(..., description="Текущий статус")
    trends: Dict[str, Any] = Field(..., description="Тенденции")
    recommendations: List[str] = Field(..., description="Рекомендации")
    unhealthy_components: List[str] = Field(
        ..., description="Нездоровые компоненты"
    )
    metrics_summary: Dict[str, Any] = Field(..., description="Сводка метрик")
    uptime_seconds: Optional[int] = Field(None, description="Время работы")


class HealthSystemInfo(BaseModel):
    """Информация о системе"""

    model_config = ConfigDict(from_attributes=True)

    cpu_usage_percent: float = Field(..., description="Загрузка CPU (%)")
    memory_usage_percent: float = Field(
        ..., description="Использование памяти (%)"
    )
    memory_total_gb: float = Field(..., description="Общий объем памяти (GB)")
    memory_available_gb: float = Field(
        ..., description="Доступная память (GB)"
    )
    disk_usage_percent: float = Field(
        ..., description="Использование диска (%)"
    )
    disk_total_gb: float = Field(..., description="Общий объем диска (GB)")
    disk_free_gb: float = Field(
        ..., description="Свободное место на диске (GB)"
    )


class HealthCheckRequest(BaseModel):
    """Запрос на проверку здоровья компонента"""

    component: str = Field(..., description="Название компонента для проверки")


class HealthExportRequest(BaseModel):
    """Запрос на экспорт данных здоровья"""

    format: str = Field("json", description="Формат экспорта")
    include_history: bool = Field(True, description="Включить историю")
    max_history_items: int = Field(
        100, description="Максимум элементов истории"
    )


class HealthHistoryRequest(BaseModel):
    """Запрос на получение истории здоровья"""

    component: Optional[str] = Field(None, description="Фильтр по компоненту")
    limit: int = Field(50, description="Максимальное количество записей")
    since: Optional[str] = Field(
        None, description="Начиная с времени (ISO format)"
    )


# Экспорт всех схем
__all__ = [
    "HealthStatusResponse",
    "HealthCheckResult",
    "HealthDetailedResponse",
    "HealthReadinessResponse",
    "HealthLivenessResponse",
    "HealthComponentResponse",
    "HealthComponentsResponse",
    "HealthHistoryResponse",
    "HealthMetricsResponse",
    "HealthSummaryResponse",
    "HealthExportResponse",
    "HealthTrendsResponse",
    "HealthAlert",
    "HealthReportResponse",
    "HealthSystemInfo",
    "HealthCheckRequest",
    "HealthExportRequest",
    "HealthHistoryRequest",
]
