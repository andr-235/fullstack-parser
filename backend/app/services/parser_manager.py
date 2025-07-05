from __future__ import annotations

import warnings
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional

from app.schemas.parser import ParserState, ParserStats, ParseStats, ParseTaskResponse

warnings.warn(
    "The in-memory ParserManager is not suitable for production with multiple "
    "workers. Task metadata should be persisted to a shared store like Redis.",
    UserWarning,
    stacklevel=2,
)


class _SingletonMeta(type):
    """Thread-safe singleton metaclass to ensure one manager per process."""

    _instance: Optional[ParserManager] = None
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore[override]
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class ParserManager(metaclass=_SingletonMeta):
    """Keeps track of the current parser task and historical runs."""

    def __init__(self) -> None:
        self._tasks: Dict[str, ParseTaskResponse] = {}
        self._current_task_id: Optional[str] = None
        self._lock: Lock = Lock()

    # ---------------------------------------------------------------------
    # Task lifecycle helpers
    # ---------------------------------------------------------------------
    def start_task(self, task: ParseTaskResponse) -> None:
        """Register a new running task."""
        with self._lock:
            self._tasks[task.task_id] = task
            self._current_task_id = task.task_id

    def complete_task(self, task_id: str, stats: dict[str, int]) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "completed"
                task.completed_at = datetime.now(timezone.utc)
                task.stats = ParseStats(**stats)  # type: ignore[arg-type]
            self._current_task_id = None

    def fail_task(self, task_id: str, error_message: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "failed"
                task.completed_at = datetime.now(timezone.utc)
                task.error_message = error_message
            self._current_task_id = None

    def stop_current_task(self) -> None:
        """Mark current task as stopped from the API perspective."""
        with self._lock:
            if self._current_task_id and self._current_task_id in self._tasks:
                task = self._tasks[self._current_task_id]
                if task.status == "running":
                    task.status = "stopped"
                    task.completed_at = datetime.now(timezone.utc)
            self._current_task_id = None

    # ------------------------------------------------------------------
    # Data access helpers
    # ------------------------------------------------------------------
    def get_state(self) -> ParserState:
        with self._lock:
            if self._current_task_id and self._current_task_id in self._tasks:
                task = self._tasks[self._current_task_id]
                return ParserState(
                    status="running",
                    task={
                        "task_id": task.task_id,
                        "group_id": task.group_id,
                        "group_name": getattr(
                            task,
                            "group_name",
                            None,
                        ),
                        "progress": 0.0,
                        "posts_processed": (
                            task.stats.posts_processed if task.stats else 0
                        ),
                    },
                )
        return ParserState(status="stopped", task=None)

    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ParseTaskResponse]:
        with self._lock:
            tasks = list(self._tasks.values())
            # sort by started_at desc
            tasks.sort(key=lambda t: t.started_at, reverse=True)
            return tasks[skip : skip + limit]

    def get_stats(self) -> ParserStats:
        with self._lock:
            total_runs = len(self._tasks)
            successful_runs = sum(
                1 for t in self._tasks.values() if t.status == "completed"
            )
            failed_runs = sum(1 for t in self._tasks.values() if t.status == "failed")

            durations = [
                t.stats.duration_seconds or 0
                for t in self._tasks.values()
                if t.status == "completed" and t.stats
            ]
            average_duration = sum(durations) / len(durations) if durations else 0

            total_posts_processed = sum(
                t.stats.posts_processed for t in self._tasks.values() if t.stats
            )
            total_comments_found = sum(
                t.stats.comments_found for t in self._tasks.values() if t.stats
            )
            total_comments_with_keywords = sum(
                t.stats.comments_with_keywords for t in self._tasks.values() if t.stats
            )

            return ParserStats(
                total_runs=total_runs,
                successful_runs=successful_runs,
                failed_runs=failed_runs,
                average_duration=average_duration,
                total_posts_processed=total_posts_processed,
                total_comments_found=total_comments_found,
                total_comments_with_keywords=total_comments_with_keywords,
            )


# Public singleton instance
def get_parser_manager() -> ParserManager:
    return ParserManager()
