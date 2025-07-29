"""
Unit tests for background tasks service.
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.background_tasks import (
    BackgroundTask,
    BackgroundTaskManager,
    TaskPriority,
    TaskStatus,
    get_background_task,
    get_background_task_result,
    get_background_task_status,
    submit_background_task,
)
from app.core.exceptions import ServiceUnavailableError


class TestBackgroundTask:
    """Test background task data structure."""

    def test_task_creation(self):
        """Test task creation with default values."""
        task = BackgroundTask()

        assert task.id is not None
        assert task.name == ""
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.NORMAL
        assert task.created_at is not None
        assert task.started_at is None
        assert task.completed_at is None
        assert task.result is None
        assert task.error is None
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.timeout is None
        assert task.metadata == {}

    def test_task_creation_with_values(self):
        """Test task creation with specific values."""
        task = BackgroundTask(
            name="test_task",
            status=TaskStatus.RUNNING,
            priority=TaskPriority.HIGH,
            timeout=60.0,
            metadata={"key": "value"},
        )

        assert task.name == "test_task"
        assert task.status == TaskStatus.RUNNING
        assert task.priority == TaskPriority.HIGH
        assert task.timeout == 60.0
        assert task.metadata == {"key": "value"}


class TestBackgroundTaskManager:
    """Test background task manager functionality."""

    @pytest.fixture
    def task_manager(self):
        """Create task manager instance."""
        return BackgroundTaskManager(max_workers=2, max_queue_size=10)

    @pytest.fixture
    def mock_func(self):
        """Create mock async function."""

        async def mock_async_func():
            await asyncio.sleep(0.1)
            return "success"

        return mock_async_func

    @pytest.mark.asyncio
    async def test_start_stop(self, task_manager):
        """Test starting and stopping task manager."""
        assert not task_manager.running

        await task_manager.start()
        assert task_manager.running
        assert len(task_manager.workers) == 2

        await task_manager.stop()
        assert not task_manager.running
        assert len(task_manager.workers) == 0

    @pytest.mark.asyncio
    async def test_submit_task_success(self, task_manager, mock_func):
        """Test successful task submission."""
        await task_manager.start()

        task_id = await task_manager.submit_task(
            func=mock_func,
            name="test_task",
            priority=TaskPriority.HIGH,
            timeout=30.0,
        )

        assert task_id is not None
        assert task_id in task_manager.tasks

        task = task_manager.tasks[task_id]
        assert task.name == "test_task"
        assert task.priority == TaskPriority.HIGH
        assert task.timeout == 30.0

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_submit_task_not_running(self, task_manager, mock_func):
        """Test task submission when manager is not running."""
        with pytest.raises(ServiceUnavailableError, match="not running"):
            await task_manager.submit_task(func=mock_func)

    @pytest.mark.asyncio
    async def test_submit_task_queue_full(self, task_manager, mock_func):
        """Test task submission when queue is full."""
        task_manager.max_queue_size = 1
        await task_manager.start()

        # Fill the queue
        await task_manager.submit_task(func=mock_func, name="task1")

        # Try to submit another task
        with pytest.raises(ServiceUnavailableError, match="queue is full"):
            await task_manager.submit_task(func=mock_func, name="task2")

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_get_task(self, task_manager, mock_func):
        """Test getting task by ID."""
        await task_manager.start()

        task_id = await task_manager.submit_task(
            func=mock_func, name="test_task"
        )
        task = await task_manager.get_task(task_id)

        assert task is not None
        assert task.id == task_id
        assert task.name == "test_task"

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, task_manager):
        """Test getting non-existent task."""
        await task_manager.start()

        task = await task_manager.get_task("non-existent-id")
        assert task is None

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_cancel_task_success(self, task_manager, mock_func):
        """Test successful task cancellation."""
        await task_manager.start()

        task_id = await task_manager.submit_task(
            func=mock_func, name="test_task"
        )

        # Cancel the task
        cancelled = await task_manager.cancel_task(task_id)
        assert cancelled is True

        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.CANCELLED

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_cancel_task_not_found(self, task_manager):
        """Test cancelling non-existent task."""
        await task_manager.start()

        cancelled = await task_manager.cancel_task("non-existent-id")
        assert cancelled is False

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_cancel_running_task(self, task_manager, mock_func):
        """Test cancelling running task (should fail)."""
        await task_manager.start()

        task_id = await task_manager.submit_task(
            func=mock_func, name="test_task"
        )

        # Wait for task to start running
        await asyncio.sleep(0.2)

        cancelled = await task_manager.cancel_task(task_id)
        assert cancelled is False

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_get_task_status(self, task_manager, mock_func):
        """Test getting task status."""
        await task_manager.start()

        task_id = await task_manager.submit_task(
            func=mock_func, name="test_task"
        )
        status = await task_manager.get_task_status(task_id)

        assert status == TaskStatus.PENDING

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_get_task_result(self, task_manager, mock_func):
        """Test getting task result."""
        await task_manager.start()

        task_id = await task_manager.submit_task(
            func=mock_func, name="test_task"
        )

        # Wait for task to complete
        await asyncio.sleep(0.3)

        result = await task_manager.get_task_result(task_id)
        assert result == "success"

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_list_tasks(self, task_manager, mock_func):
        """Test listing tasks."""
        await task_manager.start()

        # Submit multiple tasks
        task_id1 = await task_manager.submit_task(func=mock_func, name="task1")
        task_id2 = await task_manager.submit_task(func=mock_func, name="task2")

        tasks = await task_manager.list_tasks()
        assert len(tasks) >= 2

        # Test filtering by status
        pending_tasks = await task_manager.list_tasks(
            status=TaskStatus.PENDING
        )
        assert len(pending_tasks) >= 2

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_get_stats(self, task_manager, mock_func):
        """Test getting task manager statistics."""
        await task_manager.start()

        # Submit a task
        await task_manager.submit_task(func=mock_func, name="test_task")

        stats = await task_manager.get_stats()

        assert "total_tasks" in stats
        assert "completed_tasks" in stats
        assert "failed_tasks" in stats
        assert "pending_tasks" in stats
        assert "running_tasks" in stats
        assert "queue_size" in stats
        assert "active_workers" in stats
        assert "total_tasks_stored" in stats

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_cleanup_old_tasks(self, task_manager, mock_func):
        """Test cleaning up old tasks."""
        await task_manager.start()

        # Submit a task
        task_id = await task_manager.submit_task(
            func=mock_func, name="test_task"
        )

        # Wait for task to complete
        await asyncio.sleep(0.3)

        # Manually set completion time to old date
        task = task_manager.tasks[task_id]
        task.completed_at = datetime.utcnow() - timedelta(hours=25)

        # Clean up old tasks
        await task_manager.cleanup_old_tasks(max_age_hours=24)

        # Task should be removed
        assert task_id not in task_manager.tasks

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_task_execution_success(self, task_manager):
        """Test successful task execution."""
        await task_manager.start()

        async def test_func():
            return "test_result"

        task_id = await task_manager.submit_task(
            func=test_func, name="test_task"
        )

        # Wait for task to complete
        await asyncio.sleep(0.2)

        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "test_result"
        assert task.error is None

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_task_execution_error(self, task_manager):
        """Test task execution with error."""
        await task_manager.start()

        async def error_func():
            raise Exception("Test error")

        task_id = await task_manager.submit_task(
            func=error_func, name="error_task"
        )

        # Wait for task to complete
        await asyncio.sleep(0.2)

        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.FAILED
        assert task.error == "Test error"

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_task_timeout(self, task_manager):
        """Test task timeout handling."""
        await task_manager.start()

        async def slow_func():
            await asyncio.sleep(1.0)
            return "should_not_reach"

        task_id = await task_manager.submit_task(
            func=slow_func, name="timeout_task", timeout=0.1
        )

        # Wait for task to timeout
        await asyncio.sleep(0.3)

        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.FAILED
        assert "timeout" in task.error.lower()

        await task_manager.stop()

    @pytest.mark.asyncio
    async def test_sync_function_execution(self, task_manager):
        """Test executing synchronous functions."""
        await task_manager.start()

        def sync_func():
            return "sync_result"

        task_id = await task_manager.submit_task(
            func=sync_func, name="sync_task"
        )

        # Wait for task to complete
        await asyncio.sleep(0.2)

        task = task_manager.tasks[task_id]
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "sync_result"

        await task_manager.stop()


class TestBackgroundTaskFunctions:
    """Test background task utility functions."""

    @pytest.fixture
    def mock_task_manager(self):
        """Create mock task manager."""
        mock = AsyncMock()
        mock.submit_task = AsyncMock(return_value="test_task_id")
        mock.get_task = AsyncMock()
        mock.get_task_status = AsyncMock()
        mock.get_task_result = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_submit_background_task(self, mock_task_manager):
        """Test submit_background_task function."""
        with patch(
            "app.core.background_tasks.background_task_manager",
            mock_task_manager,
        ):
            task_id = await submit_background_task(
                func=lambda: "test",
                name="test_task",
                priority=TaskPriority.HIGH,
            )

            assert task_id == "test_task_id"
            mock_task_manager.submit_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_background_task(self, mock_task_manager):
        """Test get_background_task function."""
        mock_task = MagicMock()
        mock_task_manager.get_task.return_value = mock_task

        with patch(
            "app.core.background_tasks.background_task_manager",
            mock_task_manager,
        ):
            result = await get_background_task("test_task_id")

            assert result == mock_task
            mock_task_manager.get_task.assert_called_once_with("test_task_id")

    @pytest.mark.asyncio
    async def test_get_background_task_status(self, mock_task_manager):
        """Test get_background_task_status function."""
        mock_task_manager.get_task_status.return_value = TaskStatus.COMPLETED

        with patch(
            "app.core.background_tasks.background_task_manager",
            mock_task_manager,
        ):
            result = await get_background_task_status("test_task_id")

            assert result == TaskStatus.COMPLETED
            mock_task_manager.get_task_status.assert_called_once_with(
                "test_task_id"
            )

    @pytest.mark.asyncio
    async def test_get_background_task_result(self, mock_task_manager):
        """Test get_background_task_result function."""
        mock_task_manager.get_task_result.return_value = "test_result"

        with patch(
            "app.core.background_tasks.background_task_manager",
            mock_task_manager,
        ):
            result = await get_background_task_result("test_task_id")

            assert result == "test_result"
            mock_task_manager.get_task_result.assert_called_once_with(
                "test_task_id"
            )
