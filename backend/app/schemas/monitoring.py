"""
Схемы для API автоматического мониторинга
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MonitoringStats(BaseModel):
    """Статистика мониторинга"""

    total_groups: int = Field(description="Общее количество групп")
    active_groups: int = Field(description="Количество активных групп")
    monitored_groups: int = Field(
        description="Количество групп с включенным мониторингом"
    )
    ready_for_monitoring: int = Field(
        description="Количество групп, готовых для мониторинга"
    )
    next_monitoring_at: Optional[str] = Field(
        description="Время следующего мониторинга (UTC)"
    )
    next_monitoring_at_local: Optional[str] = Field(
        description="Время следующего мониторинга (локальное время Владивостока)"
    )


class SchedulerStatus(BaseModel):
    """Статус планировщика"""

    is_running: bool = Field(description="Запущен ли планировщик")
    monitoring_interval_seconds: int = Field(
        description="Интервал мониторинга в секундах"
    )
    redis_connected: bool = Field(description="Подключен ли к Redis")
    last_check: str = Field(description="Время последней проверки")


class GroupMonitoringConfig(BaseModel):
    """Конфигурация мониторинга группы"""

    interval_minutes: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Интервал мониторинга в минутах (1-1440)",
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Приоритет мониторинга (1-10, где 10 - высший)",
    )


class GroupMonitoringResponse(BaseModel):
    """Ответ с информацией о мониторинге группы"""

    id: int = Field(description="ID группы")
    group_name: str = Field(description="Название группы")
    screen_name: Optional[str] = Field(description="Короткое имя группы")
    auto_monitoring_enabled: bool = Field(
        description="Включен ли автоматический мониторинг"
    )
    monitoring_interval_minutes: int = Field(
        description="Интервал мониторинга в минутах"
    )
    monitoring_priority: int = Field(description="Приоритет мониторинга")
    next_monitoring_at: Optional[datetime] = Field(
        description="Время следующего мониторинга (UTC)"
    )
    next_monitoring_at_local: Optional[str] = Field(
        description="Время следующего мониторинга (локальное время Владивостока)"
    )
    monitoring_runs_count: int = Field(
        description="Количество запусков мониторинга"
    )
    last_monitoring_success: Optional[datetime] = Field(
        description="Последний успешный запуск (UTC)"
    )
    last_monitoring_success_local: Optional[str] = Field(
        description="Последний успешный запуск (локальное время Владивостока)"
    )
    last_monitoring_error: Optional[str] = Field(
        description="Последняя ошибка мониторинга"
    )


class MonitoringCycleResult(BaseModel):
    """Результат цикла мониторинга"""

    total_groups: int = Field(description="Общее количество групп")
    monitored_groups: int = Field(description="Количество обработанных групп")
    successful_runs: int = Field(description="Успешных запусков")
    failed_runs: int = Field(description="Неудачных запусков")
    duration_seconds: float = Field(description="Время выполнения в секундах")
