"""
Background tasks service for asynchronous processing of long-running operations.
Provides task queue management and monitoring.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from structlog import get_logger

from .exceptions import ServiceUnavailableError

logger = get_logger()


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BackgroundTask:
    """Background task data structure."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    func: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BackgroundTaskManager:
    """Manager for background tasks with queue and monitoring."""
    
    def __init__(self, max_workers: int = 10, max_queue_size: int = 1000):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.tasks: Dict[str, BackgroundTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.workers: List[asyncio.Task] = []
        self.running = False
        self._stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "pending_tasks": 0,
            "running_tasks": 0
        }
    
    async def start(self):
        """Start the background task manager."""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting background task manager", max_workers=self.max_workers)
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def stop(self):
        """Stop the background task manager."""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping background task manager")
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        logger.info("Background task manager stopped")
    
    async def submit_task(
        self,
        func: Callable,
        *args,
        name: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Submit a task for background execution.
        
        Args:
            func: Function to execute
            *args: Function arguments
            name: Task name for identification
            priority: Task priority
            timeout: Task timeout in seconds
            max_retries: Maximum retry attempts
            metadata: Additional task metadata
            **kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        if not self.running:
            raise ServiceUnavailableError("Background task manager is not running")
        
        if self.task_queue.qsize() >= self.max_queue_size:
            raise ServiceUnavailableError("Task queue is full")
        
        task = BackgroundTask(
            name=name or func.__name__,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        self.tasks[task.id] = task
        self._stats["total_tasks"] += 1
        self._stats["pending_tasks"] += 1
        
        await self.task_queue.put((priority.value, task))
        
        logger.info(
            "Task submitted",
            task_id=task.id,
            name=task.name,
            priority=priority.name
        )
        
        return task.id
    
    async def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            self._stats["pending_tasks"] -= 1
            logger.info("Task cancelled", task_id=task_id, name=task.name)
            return True
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get task status."""
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    async def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get task result."""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[BackgroundTask]:
        """List tasks with optional status filter."""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[:limit]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get task manager statistics."""
        return {
            **self._stats,
            "queue_size": self.task_queue.qsize(),
            "active_workers": len([w for w in self.workers if not w.done()]),
            "total_tasks_stored": len(self.tasks)
        }
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed/failed tasks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.completed_at and task.completed_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        if tasks_to_remove:
            logger.info("Cleaned up old tasks", count=len(tasks_to_remove))
    
    async def _worker(self, worker_name: str):
        """Worker coroutine for processing tasks."""
        logger.info("Worker started", worker_name=worker_name)
        
        while self.running:
            try:
                # Get task from queue with timeout
                priority, task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                await self._process_task(task, worker_name)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Worker error", worker_name=worker_name, error=str(e))
        
        logger.info("Worker stopped", worker_name=worker_name)
    
    async def _process_task(self, task: BackgroundTask, worker_name: str):
        """Process a single task."""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self._stats["pending_tasks"] -= 1
            self._stats["running_tasks"] += 1
            
            logger.info(
                "Processing task",
                task_id=task.id,
                name=task.name,
                worker=worker_name
            )
            
            # Execute task with timeout
            if task.timeout:
                result = await asyncio.wait_for(
                    self._execute_task(task),
                    timeout=task.timeout
                )
            else:
                result = await self._execute_task(task)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            self._stats["running_tasks"] -= 1
            self._stats["completed_tasks"] += 1
            
            logger.info(
                "Task completed",
                task_id=task.id,
                name=task.name,
                worker=worker_name
            )
            
        except asyncio.TimeoutError:
            task.error = f"Task timeout after {task.timeout} seconds"
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            
            self._stats["running_tasks"] -= 1
            self._stats["failed_tasks"] += 1
            
            logger.error(
                "Task timeout",
                task_id=task.id,
                name=task.name,
                timeout=task.timeout
            )
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            
            self._stats["running_tasks"] -= 1
            self._stats["failed_tasks"] += 1
            
            logger.error(
                "Task failed",
                task_id=task.id,
                name=task.name,
                error=str(e)
            )
    
    async def _execute_task(self, task: BackgroundTask) -> Any:
        """Execute a task function."""
        if asyncio.iscoroutinefunction(task.func):
            return await task.func(*task.args, **task.kwargs)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                task.func,
                *task.args,
                **task.kwargs
            )


# Global background task manager instance
background_task_manager = BackgroundTaskManager()


async def submit_background_task(
    func: Callable,
    *args,
    name: str = "",
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = None,
    max_retries: int = 3,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    Submit a task for background execution.
    
    Args:
        func: Function to execute
        *args: Function arguments
        name: Task name
        priority: Task priority
        timeout: Task timeout
        max_retries: Maximum retries
        metadata: Additional metadata
        **kwargs: Function keyword arguments
        
    Returns:
        Task ID
    """
    return await background_task_manager.submit_task(
        func=func,
        *args,
        name=name,
        priority=priority,
        timeout=timeout,
        max_retries=max_retries,
        metadata=metadata,
        **kwargs
    )


async def get_background_task(task_id: str) -> Optional[BackgroundTask]:
    """Get background task by ID."""
    return await background_task_manager.get_task(task_id)


async def get_background_task_status(task_id: str) -> Optional[TaskStatus]:
    """Get background task status."""
    return await background_task_manager.get_task_status(task_id)


async def get_background_task_result(task_id: str) -> Optional[Any]:
    """Get background task result."""
    return await background_task_manager.get_task_result(task_id) 