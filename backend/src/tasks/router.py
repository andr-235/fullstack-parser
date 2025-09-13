"""
API роутер для управления задачами Celery
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from common.celery_config import celery_app
from common.logging import get_logger
from common.redis_client import redis_client

logger = get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskResponse(BaseModel):
    """Модель ответа задачи"""
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


class TaskInfo(BaseModel):
    """Модель информации о задаче"""
    task_id: str
    name: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    date_done: Optional[str] = None
    worker: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Модель ответа проверки здоровья"""
    status: str
    redis_connected: bool
    active_tasks: int
    scheduled_tasks: int
    reserved_tasks: int


@router.get("/health", response_model=HealthCheckResponse)
async def get_tasks_health():
    """Проверка здоровья системы задач"""
    try:
        # Проверяем Redis
        redis_connected = redis_client.ping()
        
        # Получаем статистику задач
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        active_count = sum(len(tasks) for tasks in (active_tasks or {}).values())
        scheduled_count = sum(len(tasks) for tasks in (scheduled_tasks or {}).values())
        reserved_count = sum(len(tasks) for tasks in (reserved_tasks or {}).values())
        
        return HealthCheckResponse(
            status="healthy" if redis_connected else "unhealthy",
            redis_connected=redis_connected,
            active_tasks=active_count,
            scheduled_tasks=scheduled_count,
            reserved_tasks=reserved_count
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/", response_model=List[TaskInfo])
async def get_active_tasks():
    """Получить список активных задач"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        tasks = []
        for worker, worker_tasks in (active_tasks or {}).items():
            for task in worker_tasks:
                tasks.append(TaskInfo(
                    task_id=task["id"],
                    name=task["name"],
                    status="ACTIVE",
                    worker=worker
                ))
        
        return tasks
    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active tasks: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskInfo)
async def get_task_info(task_id: str):
    """Получить информацию о задаче"""
    try:
        result = celery_app.AsyncResult(task_id)
        
        return TaskInfo(
            task_id=task_id,
            name=result.name or "Unknown",
            status=result.status,
            result=result.result if result.successful() else None,
            error=str(result.result) if result.failed() else None,
            date_done=result.date_done.isoformat() if result.date_done else None,
            worker=result.worker
        )
    except Exception as e:
        logger.error(f"Failed to get task info for {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task info: {str(e)}"
        )


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: str):
    """Отменить задачу"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        
        return TaskResponse(
            task_id=task_id,
            status="CANCELLED"
        )
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str):
    """Повторить задачу"""
    try:
        result = celery_app.AsyncResult(task_id)
        if result.failed():
            result.retry()
            return TaskResponse(
                task_id=task_id,
                status="RETRYING"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is not in failed state"
            )
    except Exception as e:
        logger.error(f"Failed to retry task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry task: {str(e)}"
        )


@router.get("/stats/overview")
async def get_tasks_stats():
    """Получить статистику задач"""
    try:
        inspect = celery_app.control.inspect()
        
        # Получаем статистику по воркерам
        stats = inspect.stats()
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        
        # Подсчитываем общие числа
        total_active = sum(len(tasks) for tasks in (active or {}).values())
        total_scheduled = sum(len(tasks) for tasks in (scheduled or {}).values())
        total_reserved = sum(len(tasks) for tasks in (reserved or {}).values())
        
        # Получаем статистику по очередям
        queue_stats = {}
        for worker, worker_tasks in (active or {}).items():
            for task in worker_tasks:
                queue = task.get("delivery_info", {}).get("routing_key", "default")
                queue_stats[queue] = queue_stats.get(queue, 0) + 1
        
        return {
            "workers": len(stats or {}),
            "total_active": total_active,
            "total_scheduled": total_scheduled,
            "total_reserved": total_reserved,
            "queue_stats": queue_stats,
            "worker_stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get tasks stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tasks stats: {str(e)}"
        )


@router.post("/purge")
async def purge_tasks(
    queue: Optional[str] = Query(None, description="Очередь для очистки")
):
    """Очистить очередь задач"""
    try:
        if queue:
            celery_app.control.purge(queue)
            message = f"Purged queue: {queue}"
        else:
            celery_app.control.purge()
            message = "Purged all queues"
        
        logger.info(message)
        return {"message": message}
    except Exception as e:
        logger.error(f"Failed to purge tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purge tasks: {str(e)}"
        )


@router.post("/shutdown")
async def shutdown_workers():
    """Остановить всех воркеров"""
    try:
        celery_app.control.shutdown()
        logger.info("Workers shutdown requested")
        return {"message": "Workers shutdown requested"}
    except Exception as e:
        logger.error(f"Failed to shutdown workers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to shutdown workers: {str(e)}"
        )
