"""
Pydantic схемы для ARQ API

Содержит модели запросов и ответов для работы с асинхронными задачами.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class TaskEnqueueRequest(BaseModel):
    """
    Запрос на добавление задачи в очередь
    """

    function_name: str = Field(..., description="Имя функции для выполнения")
    args: Optional[List[Any]] = Field(
        default_factory=list, description="Позиционные аргументы"
    )
    kwargs: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Именованные аргументы"
    )
    job_id: Optional[str] = Field(None, description="Уникальный ID задачи")
    defer_until: Optional[datetime] = Field(
        None, description="Отложить до указанного времени"
    )
    defer_by: Optional[Union[int, str]] = Field(
        None, description="Отложить на указанное время"
    )


class TaskStatusResponse(BaseModel):
    """
    Ответ со статусом задачи
    """

    job_id: str = Field(..., description="ID задачи")
    status: str = Field(..., description="Статус задачи")
    result: Optional[Any] = Field(None, description="Результат выполнения")
    error: Optional[str] = Field(None, description="Ошибка выполнения")
    created_at: Optional[datetime] = Field(None, description="Время создания")
    started_at: Optional[datetime] = Field(
        None, description="Время начала выполнения"
    )
    finished_at: Optional[datetime] = Field(
        None, description="Время завершения"
    )
    function: Optional[str] = Field(None, description="Имя функции")
    args: Optional[List[Any]] = Field(None, description="Аргументы функции")
    kwargs: Optional[Dict[str, Any]] = Field(
        None, description="Именованные аргументы"
    )


class QueueInfoResponse(BaseModel):
    """
    Информация об очереди
    """

    queue_name: str = Field(..., description="Имя очереди")
    queued_jobs_count: int = Field(
        ..., description="Количество задач в очереди"
    )
    max_jobs: int = Field(..., description="Максимальное количество задач")
    job_timeout: int = Field(..., description="Таймаут выполнения задач")
    max_tries: int = Field(..., description="Максимальное количество попыток")


class HealthCheckResponse(BaseModel):
    """
    Ответ проверки здоровья ARQ
    """

    service: str = Field(..., description="Название сервиса")
    healthy: bool = Field(..., description="Статус здоровья")
    timestamp: datetime = Field(..., description="Время проверки")
    details: Dict[str, Any] = Field(..., description="Детали проверки")


class TaskAbortRequest(BaseModel):
    """
    Запрос на отмену задачи
    """

    job_id: str = Field(..., description="ID задачи для отмены")


class TaskResultResponse(BaseModel):
    """
    Ответ с результатом задачи
    """

    job_id: str = Field(..., description="ID задачи")
    result: Optional[Any] = Field(None, description="Результат выполнения")
    status: str = Field(..., description="Статус задачи")


class BatchTaskRequest(BaseModel):
    """
    Запрос на выполнение нескольких задач
    """

    tasks: List[TaskEnqueueRequest] = Field(
        ..., description="Список задач для выполнения"
    )


class BatchTaskResponse(BaseModel):
    """
    Ответ на выполнение нескольких задач
    """

    total_tasks: int = Field(..., description="Общее количество задач")
    successful: int = Field(..., description="Количество успешных задач")
    failed: int = Field(..., description="Количество неудачных задач")
    job_ids: List[str] = Field(..., description="Список ID созданных задач")


class CronJobCreateRequest(BaseModel):
    """
    Запрос на создание cron задачи
    """

    function_name: str = Field(..., description="Имя функции")
    cron_expression: str = Field(..., description="Cron выражение")
    args: Optional[List[Any]] = Field(
        default_factory=list, description="Аргументы"
    )
    kwargs: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Именованные аргументы"
    )
    job_id: Optional[str] = Field(None, description="ID задачи")
    unique: bool = Field(default=True, description="Уникальность выполнения")


class CronJobResponse(BaseModel):
    """
    Ответ о cron задаче
    """

    name: str = Field(..., description="Имя задачи")
    cron_expression: str = Field(..., description="Cron выражение")
    function_name: str = Field(..., description="Имя функции")
    next_run: Optional[datetime] = Field(
        None, description="Следующее выполнение"
    )
    enabled: bool = Field(default=True, description="Включена ли задача")
