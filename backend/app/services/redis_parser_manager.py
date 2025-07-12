from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import redis.asyncio as redis
from redis.exceptions import ResponseError

from app.core.config import settings
from app.schemas.parser import (
    ParserState,
    ParserStats,
    ParseTaskResponse,
)


class RedisParserManager:
    """Manages parser tasks and their state using Redis for persistence."""

    _redis_client: Optional[redis.Redis] = None
    _instance: Optional["RedisParserManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def _get_redis(self) -> redis.Redis:
        """Initializes and returns the Redis client."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                str(settings.redis_url), decode_responses=True
            )
        return self._redis_client

    # Task lifecycle helpers
    async def start_task(self, task: ParseTaskResponse) -> None:
        """Registers a new running task in Redis."""
        r = await self._get_redis()
        task_key = f"parser:task:{task.task_id}"

        task_data = task.model_dump(mode="json")
        task_data["status"] = "in_progress"

        if task_data.get("stats"):
            task_data["stats"] = json.dumps(task_data["stats"])

        final_task_data = {
            k: str(v) if v is not None else "" for k, v in task_data.items()
        }

        current_task_key = "parser:current_task_id"

        async with r.pipeline() as pipe:
            pipe.set(current_task_key, task.task_id)
            pipe.hset(task_key, mapping=final_task_data)
            await pipe.execute()

    async def complete_task(self, task_id: str, stats: dict[str, int]) -> None:
        """Marks a task as completed in Redis."""
        r = await self._get_redis()
        task_key = f"parser:task:{task_id}"

        update_data = {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "stats": json.dumps(stats),
        }

        async with r.pipeline() as pipe:
            pipe.hset(task_key, mapping=update_data)
            pipe.delete("parser:current_task_id")
            await pipe.execute()

    async def fail_task(self, task_id: str, error_message: str) -> None:
        """Marks a task as failed in Redis."""
        r = await self._get_redis()
        task_key = f"parser:task:{task_id}"

        update_data = {
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": error_message,
        }

        async with r.pipeline() as pipe:
            pipe.hset(task_key, mapping=update_data)
            pipe.delete("parser:current_task_id")
            await pipe.execute()

    async def stop_current_task(self) -> None:
        """Stops the current running task."""
        r = await self._get_redis()
        current_task_id = await r.get("parser:current_task_id")
        if current_task_id:
            task_key = f"parser:task:{current_task_id}"
            async with r.pipeline() as pipe:
                pipe.hset(task_key, "status", "stopped")
                pipe.hset(
                    task_key, "completed_at", datetime.now(timezone.utc).isoformat()
                )
                pipe.delete("parser:current_task_id")
                await pipe.execute()

    async def update_task_progress(self, task_id: str, progress: float) -> None:
        """Updates the progress of a running task."""
        r = await self._get_redis()
        task_key = f"parser:task:{task_id}"
        await r.hset(task_key, "progress", str(progress))

    # Data access helpers
    async def get_state(self) -> ParserState:
        """Retrieves the current parser state from Redis."""
        r = await self._get_redis()
        current_task_id = await r.get("parser:current_task_id")

        if not current_task_id:
            return ParserState(status="stopped", task=None)

        task_key = f"parser:task:{current_task_id}"
        task_data = None
        try:
            task_data = await r.hgetall(task_key)
        except ResponseError:
            pass  # Fallback for old string-based format

        if not task_data:
            task_json = await r.get(task_key)
            if task_json:
                try:
                    task_data = json.loads(task_json)
                except json.JSONDecodeError:
                    task_data = None  # Invalid JSON

        if not task_data:
            return ParserState(status="stopped", task=None)

        if task_data.get("stats") and isinstance(task_data.get("stats"), str):
            try:
                task_data["stats"] = json.loads(task_data["stats"])
            except (json.JSONDecodeError, TypeError):
                task_data["stats"] = None

        task_data.setdefault("task_id", current_task_id)

        try:
            task = ParseTaskResponse(**task_data)
        except Exception:
            return ParserState(status="stopped", task=None)

        return ParserState(
            status="running",
            task={
                "task_id": task.task_id,
                "group_id": task.group_id,
                "group_name": task.group_name,
                "progress": task.progress,
                "posts_processed": task.stats.posts_processed if task.stats else 0,
            },
        )

    async def list_tasks(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ParseTaskResponse], int]:
        """
        Lists all parser tasks from Redis with pagination.

        Returns:
            A tuple containing the list of tasks and the total task count.
        """
        r = await self._get_redis()
        task_keys = await r.keys("parser:task:*")
        total_count = len(task_keys)

        tasks = []
        # Sort keys to handle pagination correctly before fetching data
        # Note: This is not perfectly efficient for large datasets,
        # but acceptable for a few thousand tasks.
        # A more robust solution might involve a sorted set.
        sorted_task_keys = sorted(task_keys, reverse=True)
        paginated_keys = sorted_task_keys[skip : skip + limit]

        for key in paginated_keys:
            task_data = None
            try:
                task_data = await r.hgetall(key)
            except ResponseError:
                pass  # Fallback for old string-based format

            if not task_data:
                task_json = await r.get(key)
                if task_json:
                    try:
                        task_data = json.loads(task_json)
                    except json.JSONDecodeError:
                        continue  # Skip malformed JSON

            if not task_data:
                continue

            task_id = key.split(":")[-1]
            task_data["task_id"] = task_id

            # Handle potential empty strings from Redis hash
            for k, v in list(task_data.items()):
                if v == "":
                    task_data[k] = None

            # Handle nested JSON for stats
            if task_data.get("stats") and isinstance(task_data.get("stats"), str):
                try:
                    task_data["stats"] = json.loads(task_data["stats"])
                except (json.JSONDecodeError, TypeError):
                    task_data["stats"] = None
            try:
                tasks.append(ParseTaskResponse(**task_data))
            except Exception:
                # NOTE: Skipping task with potentially invalid data due to migration
                continue

        # This sorting is not fully accurate due to pagination,
        # but provides sorted results for the current page.
        tasks.sort(key=lambda t: t.started_at, reverse=True)
        return tasks, total_count

    async def get_stats(self) -> ParserStats:
        """Calculates and returns overall parser stats from Redis."""
        tasks, _ = await self.list_tasks(
            limit=1000
        )  # Assuming max 1000 tasks for stats

        total_runs = len(tasks)
        successful_runs = sum(1 for t in tasks if t.status == "completed")
        failed_runs = sum(1 for t in tasks if t.status == "failed")

        durations = [
            t.stats.duration_seconds or 0
            for t in tasks
            if t.status == "completed" and t.stats
        ]
        average_duration = sum(durations) / len(durations) if durations else 0

        total_posts_processed = sum(
            t.stats.posts_processed
            for t in tasks
            if t.stats and t.stats.posts_processed
        )
        total_comments_found = sum(
            t.stats.comments_found for t in tasks if t.stats and t.stats.comments_found
        )
        total_comments_with_keywords = sum(
            t.stats.comments_with_keywords
            for t in tasks
            if t.stats and t.stats.comments_with_keywords
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

    async def close(self) -> None:
        """Closes the Redis connection."""
        if self._redis_client:
            await self._redis_client.close()


def get_redis_parser_manager() -> RedisParserManager:
    """Returns a singleton instance of the RedisParserManager."""
    return RedisParserManager()
