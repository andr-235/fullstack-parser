"""
Pydantic схемы для модуля Monitoring

Определяет входные и выходные модели данных для API мониторинга групп
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class MonitoringConfigBase(BaseModel):
    """Базовая конфигурация мониторинга"""

    interval_minutes: int = Field(
        5, description="Интервал мониторинга в минутах", ge=1, le=1440
    )
    max_concurrent_groups: int = Field(
        10, description="Максимум групп одновременно", ge=1, le=100
    )
    enable_auto_retry: bool = Field(
        True, description="Включить авто-перезапуск при ошибках"
    )
    max_retries: int = Field(
        3, description="Максимум попыток перезапуска", ge=0, le=10
    )
    timeout_seconds: int = Field(
        30, description="Таймаут выполнения в секундах", ge=5, le=300
    )
    enable_notifications: bool = Field(
        False, description="Включить уведомления"
    )
    notification_channels: Optional[List[str]] = Field(
        None, description="Каналы уведомлений"
    )


class MonitoringBase(BaseModel):
    """Базовая модель мониторинга"""

    group_id: int = Field(..., description="ID группы VK")
    group_name: str = Field(..., description="Название группы")
    owner_id: str = Field(..., description="ID владельца мониторинга")
    status: str = Field("active", description="Статус мониторинга")
    config: MonitoringConfigBase = Field(
        ..., description="Конфигурация мониторинга"
    )


class MonitoringCreate(MonitoringBase):
    """Схема для создания мониторинга"""

    pass


class MonitoringUpdate(BaseModel):
    """Схема для обновления мониторинга"""

    status: Optional[str] = Field(None, description="Новый статус")
    config: Optional[MonitoringConfigBase] = Field(
        None, description="Новая конфигурация"
    )


class MonitoringResponse(MonitoringBase):
    """Схема ответа с информацией о мониторинге"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="ID мониторинга")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(
        ..., description="Время последнего обновления"
    )
    last_run_at: Optional[datetime] = Field(
        None, description="Время последнего запуска"
    )
    next_run_at: Optional[datetime] = Field(
        None, description="Время следующего запуска"
    )
    total_runs: int = Field(0, description="Общее количество запусков")
    successful_runs: int = Field(0, description="Количество успешных запусков")
    failed_runs: int = Field(0, description="Количество неудачных запусков")
    average_processing_time: float = Field(
        0.0, description="Среднее время обработки"
    )


class MonitoringListResponse(PaginatedResponse[MonitoringResponse]):
    """Схема ответа со списком мониторингов"""

    pass


class MonitoringResultBase(BaseModel):
    """Базовый результат мониторинга"""

    monitoring_id: str = Field(..., description="ID мониторинга")
    group_id: int = Field(..., description="ID группы VK")
    posts_found: int = Field(0, description="Найдено постов")
    comments_found: int = Field(0, description="Найдено комментариев")
    keywords_found: Optional[List[str]] = Field(
        None, description="Найденные ключевые слова"
    )
    processing_time: float = Field(
        0.0, description="Время обработки в секундах"
    )
    errors: List[str] = Field(
        default_factory=list, description="Список ошибок"
    )


class MonitoringResultCreate(MonitoringResultBase):
    """Схема для создания результата мониторинга"""

    pass


class MonitoringResultResponse(MonitoringResultBase):
    """Схема ответа с результатом мониторинга"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="ID результата")
    started_at: datetime = Field(..., description="Время начала")
    completed_at: datetime = Field(..., description="Время завершения")
    created_at: datetime = Field(..., description="Время создания")


class MonitoringStats(BaseModel):
    """Статистика мониторинга"""

    total_monitorings: int = Field(
        ..., description="Общее количество мониторингов"
    )
    active_monitorings: int = Field(
        ..., description="Количество активных мониторингов"
    )
    paused_monitorings: int = Field(
        ..., description="Количество приостановленных мониторингов"
    )
    total_runs: int = Field(..., description="Общее количество запусков")
    successful_runs: int = Field(
        ..., description="Количество успешных запусков"
    )
    failed_runs: int = Field(..., description="Количество неудачных запусков")
    average_processing_time: float = Field(
        ..., description="Среднее время обработки"
    )
    total_posts_found: int = Field(..., description="Всего найдено постов")
    total_comments_found: int = Field(
        ..., description="Всего найдено комментариев"
    )
    uptime_percentage: float = Field(..., description="Процент времени работы")


class MonitoringHealth(BaseModel):
    """Здоровье системы мониторинга"""

    is_healthy: bool = Field(..., description="Система работает нормально")
    active_monitorings: int = Field(
        ..., description="Количество активных мониторингов"
    )
    pending_tasks: int = Field(..., description="Количество задач в очереди")
    failed_tasks_last_hour: int = Field(
        ..., description="Неудачных задач за последний час"
    )
    average_response_time: float = Field(
        ..., description="Среднее время ответа"
    )
    redis_connected: bool = Field(..., description="Подключение к Redis")
    database_connected: bool = Field(..., description="Подключение к БД")
    last_health_check: datetime = Field(
        ..., description="Время последней проверки"
    )


class MonitoringSchedule(BaseModel):
    """Расписание мониторинга"""

    monitoring_id: str = Field(..., description="ID мониторинга")
    next_run_at: datetime = Field(..., description="Время следующего запуска")
    interval_minutes: int = Field(..., description="Интервал в минутах")
    priority: int = Field(..., description="Приоритет выполнения", ge=1, le=10)


class BulkMonitoringAction(BaseModel):
    """Массовое действие с мониторингами"""

    monitoring_ids: List[str] = Field(
        ..., description="Список ID мониторингов"
    )
    action: str = Field(
        ..., description="Действие: start, stop, pause, resume"
    )
    reason: Optional[str] = Field(None, description="Причина действия")


class BulkMonitoringResponse(BaseModel):
    """Ответ на массовое действие"""

    successful: int = Field(..., description="Количество успешных операций")
    failed: int = Field(..., description="Количество неудачных операций")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Список ошибок"
    )


class MonitoringAlert(BaseModel):
    """Уведомление о мониторинге"""

    monitoring_id: str = Field(..., description="ID мониторинга")
    alert_type: str = Field(..., description="Тип уведомления")
    message: str = Field(..., description="Текст уведомления")
    severity: str = Field(..., description="Уровень серьезности")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительные данные"
    )
    created_at: datetime = Field(..., description="Время создания")


class MonitoringReport(BaseModel):
    """Отчет о мониторинге"""

    monitoring_id: str = Field(..., description="ID мониторинга")
    period_start: datetime = Field(..., description="Начало периода")
    period_end: datetime = Field(..., description="Конец периода")
    total_runs: int = Field(..., description="Общее количество запусков")
    successful_runs: int = Field(..., description="Успешных запусков")
    failed_runs: int = Field(..., description="Неудачных запусков")
    posts_found: int = Field(..., description="Найдено постов")
    comments_found: int = Field(..., description="Найдено комментариев")
    average_processing_time: float = Field(
        ..., description="Среднее время обработки"
    )
    uptime_percentage: float = Field(..., description="Процент времени работы")
    top_keywords: List[str] = Field(
        default_factory=list, description="Популярные ключевые слова"
    )


# Экспорт всех схем
__all__ = [
    "MonitoringConfigBase",
    "MonitoringBase",
    "MonitoringCreate",
    "MonitoringUpdate",
    "MonitoringResponse",
    "MonitoringListResponse",
    "MonitoringResultBase",
    "MonitoringResultCreate",
    "MonitoringResultResponse",
    "MonitoringStats",
    "MonitoringHealth",
    "MonitoringSchedule",
    "BulkMonitoringAction",
    "BulkMonitoringResponse",
    "MonitoringAlert",
    "MonitoringReport",
]
