"""
Router для ARQ API

Содержит эндпоинты для управления асинхронными задачами через REST API.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from ..infrastructure.arq_service import arq_service
from .schemas import (
    TaskEnqueueRequest,
    TaskStatusResponse,
    QueueInfoResponse,
    HealthCheckResponse,
    TaskAbortRequest,
    TaskResultResponse,
    BatchTaskRequest,
    BatchTaskResponse,
    CronJobCreateRequest,
    CronJobResponse,
)
from ..config import config_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/arq",
    tags=["ARQ Tasks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/enqueue", response_model=str)
async def enqueue_task(request: TaskEnqueueRequest) -> str:
    """
    Добавление задачи в очередь

    - **function_name**: Имя функции для выполнения
    - **args**: Позиционные аргументы (опционально)
    - **kwargs**: Именованные аргументы (опционально)
    - **job_id**: Уникальный ID задачи (опционально)
    - **defer_until**: Отложить до указанного времени (опционально)
    - **defer_by**: Отложить на указанное время (опционально)

    Возвращает ID созданной задачи
    """
    try:
        # Преобразование defer_by в timedelta если это строка
        defer_by = None
        if request.defer_by:
            if isinstance(request.defer_by, str):
                # Предполагаем формат "HH:MM:SS"
                try:
                    h, m, s = map(int, request.defer_by.split(":"))
                    defer_by = timedelta(hours=h, minutes=m, seconds=s)
                except ValueError:
                    defer_by = timedelta(seconds=int(request.defer_by))
            elif isinstance(request.defer_by, int):
                defer_by = timedelta(seconds=request.defer_by)

        job_id = await arq_service.enqueue_job(
            request.function_name,
            *request.args,
            job_id=request.job_id,
            defer_until=request.defer_until,
            defer_by=defer_by,
            **request.kwargs,
        )

        if not job_id:
            raise HTTPException(
                status_code=500, detail="Не удалось добавить задачу в очередь"
            )

        return job_id

    except Exception as e:
        logger.error(f"Ошибка добавления задачи в очередь: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=TaskStatusResponse)
async def get_task_status(job_id: str) -> TaskStatusResponse:
    """
    Получение статуса задачи по ID

    - **job_id**: ID задачи
    """
    try:
        status_info = await arq_service.get_job_status(job_id)

        if not status_info:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        return TaskStatusResponse(**status_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения статуса задачи {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{job_id}", response_model=TaskResultResponse)
async def get_task_result(job_id: str) -> TaskResultResponse:
    """
    Получение результата выполнения задачи

    - **job_id**: ID задачи
    """
    try:
        result = await arq_service.get_job_result(job_id)

        # Получаем статус для дополнительной информации
        status_info = await arq_service.get_job_status(job_id)
        status = (
            status_info.get("status", "unknown") if status_info else "unknown"
        )

        return TaskResultResponse(job_id=job_id, result=result, status=status)

    except Exception as e:
        logger.error(f"Ошибка получения результата задачи {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/abort/{job_id}")
async def abort_task(job_id: str) -> Dict[str, Any]:
    """
    Отмена выполнения задачи

    - **job_id**: ID задачи для отмены
    """
    try:
        success = await arq_service.abort_job(job_id)

        if not success:
            raise HTTPException(
                status_code=400, detail="Не удалось отменить задачу"
            )

        return {
            "message": f"Задача {job_id} успешно отменена",
            "job_id": job_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка отмены задачи {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/info", response_model=QueueInfoResponse)
async def get_queue_info() -> QueueInfoResponse:
    """
    Получение информации об очереди задач
    """
    try:
        queue_info = await arq_service.get_queue_info()

        if not queue_info:
            raise HTTPException(
                status_code=500,
                detail="Не удалось получить информацию об очереди",
            )

        return QueueInfoResponse(**queue_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения информации об очереди: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Проверка здоровья ARQ сервиса
    """
    try:
        health_info = await arq_service.health_check()
        return HealthCheckResponse(**health_info)

    except Exception as e:
        logger.error(f"Ошибка проверки здоровья ARQ: {e}")
        return HealthCheckResponse(
            service="ARQ",
            healthy=False,
            timestamp=datetime.now(),
            details={"error": str(e)},
        )


@router.post("/batch", response_model=BatchTaskResponse)
async def enqueue_batch_tasks(request: BatchTaskRequest) -> BatchTaskResponse:
    """
    Добавление нескольких задач в очередь

    - **tasks**: Список задач для выполнения
    """
    try:
        job_ids = []
        successful = 0
        failed = 0

        for task_request in request.tasks:
            try:
                job_id = await enqueue_task(task_request)
                job_ids.append(job_id)
                successful += 1
            except Exception as e:
                logger.error(
                    f"Ошибка добавления задачи {task_request.function_name}: {e}"
                )
                failed += 1

        return BatchTaskResponse(
            total_tasks=len(request.tasks),
            successful=successful,
            failed=failed,
            job_ids=job_ids,
        )

    except Exception as e:
        logger.error(f"Ошибка пакетного добавления задач: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def list_queued_tasks(
    limit: int = Query(
        50, description="Максимальное количество задач для возврата"
    ),
    offset: int = Query(0, description="Смещение для пагинации"),
) -> Dict[str, Any]:
    """
    Получение списка задач в очереди

    - **limit**: Максимальное количество задач (по умолчанию 50)
    - **offset**: Смещение для пагинации (по умолчанию 0)
    """
    try:
        queue_info = await arq_service.get_queue_info()

        return {
            "total_queued": (
                queue_info.get("queued_jobs_count", 0) if queue_info else 0
            ),
            "limit": limit,
            "offset": offset,
            "tasks": [],  # ARQ не предоставляет простой способ получить список задач
            "note": "Полный список задач недоступен через ARQ API. Используйте статус отдельных задач.",
        }

    except Exception as e:
        logger.error(f"Ошибка получения списка задач: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_arq_config() -> Dict[str, Any]:
    """
    Получение текущей конфигурации ARQ
    """
    try:
        return config_service.get_arq_config()

    except Exception as e:
        logger.error(f"Ошибка получения конфигурации ARQ: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cron", response_model=CronJobResponse)
async def create_cron_job(request: CronJobCreateRequest) -> CronJobResponse:
    """
    Создание cron задачи (пока не реализовано в полном объеме)

    - **function_name**: Имя функции
    - **cron_expression**: Cron выражение
    - **args**: Аргументы (опционально)
    - **kwargs**: Именованные аргументы (опционально)
    - **job_id**: ID задачи (опционально)
    - **unique**: Уникальность выполнения (по умолчанию True)
    """
    try:
        # Пока возвращаем моковый ответ
        # В будущем нужно реализовать создание cron задач
        return CronJobResponse(
            name=f"cron:{request.function_name}",
            cron_expression=request.cron_expression,
            function_name=request.function_name,
            next_run=None,  # Нужно рассчитать на основе cron выражения
            enabled=True,
        )

    except Exception as e:
        logger.error(f"Ошибка создания cron задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))
