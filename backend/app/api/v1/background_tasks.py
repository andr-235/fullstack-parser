"""
Background tasks API endpoints.
Provides endpoints for submitting, monitoring, and managing background tasks.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.background_tasks import (
    TaskPriority,
    TaskStatus,
    background_task_manager,
    get_background_task,
    get_background_task_result,
    get_background_task_status,
    submit_background_task,
)
from app.core.exceptions import ServiceUnavailableError

router = APIRouter()


class TaskSubmitRequest(BaseModel):
    """Request model for submitting background tasks."""

    name: str
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    max_retries: int = 3
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Response model for task information."""

    id: str
    name: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int
    max_retries: int
    timeout: Optional[float] = None
    metadata: Dict[str, Any]


class TaskStatsResponse(BaseModel):
    """Response model for task manager statistics."""

    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    pending_tasks: int
    running_tasks: int
    queue_size: int
    active_workers: int
    total_tasks_stored: int


@router.post("/tasks", response_model=Dict[str, str])
async def submit_task(request: TaskSubmitRequest):
    """
    Submit a new background task.

    Note: This endpoint is for demonstration. In practice, you would submit
    specific task types with their required parameters.
    """
    try:
        # For demonstration, we'll create a simple task
        async def demo_task():
            import asyncio

            await asyncio.sleep(5)  # Simulate work
            return {"message": "Task completed successfully"}

        task_id = await submit_background_task(
            func=demo_task,
            name=request.name,
            priority=request.priority,
            timeout=request.timeout,
            max_retries=request.max_retries,
            metadata=request.metadata or {},
        )

        return {"task_id": task_id, "status": "submitted"}

    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task information by ID."""
    task = await get_background_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        name=task.name,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        result=task.result,
        error=task.error,
        retry_count=task.retry_count,
        max_retries=task.max_retries,
        timeout=task.timeout,
        metadata=task.metadata,
    )


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get task status by ID."""
    status_value = await get_background_task_status(task_id)

    if status_value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return {"task_id": task_id, "status": status_value.value}


@router.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str):
    """Get task result by ID."""
    result = await get_background_task_result(task_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not completed",
        )

    return {"task_id": task_id, "result": result}


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a pending task."""
    cancelled = await background_task_manager.cancel_task(task_id)

    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be cancelled (not found or already running/completed)",
        )

    return {"task_id": task_id, "status": "cancelled"}


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(status: Optional[TaskStatus] = None, limit: int = 100):
    """List tasks with optional status filter."""
    tasks = await background_task_manager.list_tasks(
        status=status, limit=limit
    )

    return [
        TaskResponse(
            id=task.id,
            name=task.name,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            result=task.result,
            error=task.error,
            retry_count=task.retry_count,
            max_retries=task.max_retries,
            timeout=task.timeout,
            metadata=task.metadata,
        )
        for task in tasks
    ]


@router.get("/tasks/stats", response_model=TaskStatsResponse)
async def get_task_stats():
    """Get background task manager statistics."""
    stats = await background_task_manager.get_stats()

    return TaskStatsResponse(**stats)


@router.post("/tasks/cleanup")
async def cleanup_old_tasks(max_age_hours: int = 24):
    """Clean up old completed/failed tasks."""
    await background_task_manager.cleanup_old_tasks(max_age_hours)

    return {
        "message": f"Cleanup completed for tasks older than {max_age_hours} hours"
    }


# Specific task endpoints for common operations


@router.post("/tasks/parse-comments")
async def submit_parse_comments_task(
    group_id: str,
    post_id: Optional[str] = None,
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = 300.0,  # 5 minutes default
):
    """
    Submit a task to parse comments from a VK group.

    Args:
        group_id: VK group ID
        post_id: Optional specific post ID
        priority: Task priority
        timeout: Task timeout in seconds
    """
    try:
        # Import here to avoid circular imports
        from app.services.vk_service import VKService

        async def parse_comments_task():
            vk_service = VKService()
            if post_id:
                return await vk_service.parse_post_comments(group_id, post_id)
            else:
                return await vk_service.parse_group_comments(group_id)

        task_id = await submit_background_task(
            func=parse_comments_task,
            name=f"parse_comments_{group_id}_{post_id or 'all'}",
            priority=priority,
            timeout=timeout,
            metadata={
                "group_id": group_id,
                "post_id": post_id,
                "task_type": "parse_comments",
            },
        )

        return {"task_id": task_id, "status": "submitted"}

    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.post("/tasks/analyze-comments")
async def submit_analyze_comments_task(
    group_id: str,
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = 600.0,  # 10 minutes default
):
    """
    Submit a task to analyze comments for a VK group.

    Args:
        group_id: VK group ID
        priority: Task priority
        timeout: Task timeout in seconds
    """
    try:
        # Import here to avoid circular imports
        from app.services.analysis_service import AnalysisService

        async def analyze_comments_task():
            analysis_service = AnalysisService()
            return await analysis_service.analyze_group_comments(group_id)

        task_id = await submit_background_task(
            func=analyze_comments_task,
            name=f"analyze_comments_{group_id}",
            priority=priority,
            timeout=timeout,
            metadata={"group_id": group_id, "task_type": "analyze_comments"},
        )

        return {"task_id": task_id, "status": "submitted"}

    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.post("/tasks/export-data")
async def submit_export_data_task(
    group_id: str,
    format: str = "json",
    priority: TaskPriority = TaskPriority.LOW,
    timeout: Optional[float] = 900.0,  # 15 minutes default
):
    """
    Submit a task to export data for a VK group.

    Args:
        group_id: VK group ID
        format: Export format (json, csv, xlsx)
        priority: Task priority
        timeout: Task timeout in seconds
    """
    try:
        # Import here to avoid circular imports
        from app.services.export_service import ExportService

        async def export_data_task():
            export_service = ExportService()
            return await export_service.export_group_data(group_id, format)

        task_id = await submit_background_task(
            func=export_data_task,
            name=f"export_data_{group_id}_{format}",
            priority=priority,
            timeout=timeout,
            metadata={
                "group_id": group_id,
                "format": format,
                "task_type": "export_data",
            },
        )

        return {"task_id": task_id, "status": "submitted"}

    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
