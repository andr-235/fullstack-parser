"""
Pydantic схемы для модуля Health
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Базовый ответ о здоровье системы"""
    status: str = Field(..., description="Статус здоровья")
    service: str = Field(default="vk-comments-parser", description="Название сервиса")
    version: str = Field(default="1.0.0", description="Версия сервиса")
    components: Dict[str, str] = Field(default_factory=dict, description="Статусы компонентов")
    timestamp: str = Field(..., description="Время проверки")
    uptime_seconds: Optional[int] = Field(None, description="Время работы в секундах")


class HealthCheckResult(BaseModel):
    """Результат проверки компонента"""
    component: str = Field(..., description="Название компонента")
    status: str = Field(..., description="Статус компонента")
    response_time_ms: Optional[float] = Field(None, description="Время ответа в мс")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
    details: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные детали")
    checked_at: str = Field(..., description="Время проверки")


class HealthMetrics(BaseModel):
    """Метрики здоровья"""
    total_checks: int = Field(..., description="Общее количество проверок")
    successful_checks: int = Field(..., description="Успешных проверок")
    failed_checks: int = Field(..., description="Неуспешных проверок")
    success_rate: float = Field(..., description="Процент успешности")
    average_response_time_ms: float = Field(..., description="Среднее время ответа")
    timestamp: str = Field(..., description="Время получения метрик")


class HealthCheckRequest(BaseModel):
    """Запрос на проверку компонента"""
    component: str = Field(..., description="Название компонента")


class HealthHistoryRequest(BaseModel):
    """Запрос на получение истории"""
    component: Optional[str] = Field(None, description="Фильтр по компоненту")
    limit: int = Field(default=50, description="Максимальное количество записей")


__all__ = [
    "HealthResponse",
    "HealthCheckResult", 
    "HealthMetrics",
    "HealthCheckRequest",
    "HealthHistoryRequest",
]
