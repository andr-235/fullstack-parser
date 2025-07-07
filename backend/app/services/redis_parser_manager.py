from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import redis.asyncio as redis
from app.core.config import settings
from app.schemas.parser import ParseTaskResponse, ParserState, ParserStats, ParseStats

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
            self._redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis_client

    # Task lifecycle helpers
    async def start_task(self, task: ParseTaskResponse) -> None:
        """Registers a new running task in Redis."""
        r = await self._get_redis()
        task_key = f"parser:task:{task.task_id}"
        current_task_key = "parser:current_task_id"
        
        async with r.pipeline() as pipe:
            pipe.set(current_task_key, task.task_id)
            pipe.hset(task_key, mapping=json.loads(task.model_dump_json()))
            await pipe.execute()

    async def complete_task(self, task_id: str, stats: dict[str, int]) -> None:
        """Marks a task as completed in Redis."""
        r = await self._get_redis()
        task_key = f"parser:task:{task_id}"
        
        async with r.pipeline() as pipe:
            pipe.hset(task_key, "status", "completed")
            pipe.hset(task_key, "completed_at", datetime.now(timezone.utc).isoformat())
            pipe.hset(task_key, "stats", json.dumps(stats))
            pipe.delete("parser:current_task_id")
            await pipe.execute()

    async def fail_task(self, task_id: str, error_message: str) -> None:
        """Marks a task as failed in Redis."""
        r = await self._get_redis()
        task_key = f"parser:task:{task_id}"
        
        async with r.pipeline() as pipe:
            pipe.hset(task_key, "status", "failed")
            pipe.hset(task_key, "completed_at", datetime.now(timezone.utc).isoformat())
            pipe.hset(task_key, "error_message", error_message)
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
                pipe.hset(task_key, "completed_at", datetime.now(timezone.utc).isoformat())
                pipe.delete("parser:current_task_id")
                await pipe.execute()

    # Data access helpers
    async def get_state(self) -> ParserState:
        """Retrieves the current parser state from Redis."""
        r = await self._get_redis()
        current_task_id = await r.get("parser:current_task_id")
        
        if not current_task_id:
            return ParserState(status="stopped", task=None)
            
        task_data = await r.hgetall(f"parser:task:{current_task_id}")
        if not task_data:
            return ParserState(status="stopped", task=None)
            
        task = ParseTaskResponse(**task_data)
        return ParserState(
            status="running",
            task={
                "task_id": task.task_id,
                "group_id": task.group_id,
                "group_name": task.group_name,
                "progress": 0.0,
                "posts_processed": task.stats.posts_processed if task.stats else 0,
            },
        )

    async def list_tasks(self, skip: int = 0, limit: int = 100) -> List[ParseTaskResponse]:
        """Lists all parser tasks from Redis."""
        r = await self._get_redis()
        task_keys = await r.keys("parser:task:*")
        
        tasks = []
        for key in task_keys:
            task_data = await r.hgetall(key)
            tasks.append(ParseTaskResponse(**task_data))
            
        tasks.sort(key=lambda t: t.started_at, reverse=True)
        return tasks[skip: skip + limit]

    async def get_stats(self) -> ParserStats:
        """Calculates and returns overall parser stats from Redis."""
        tasks = await self.list_tasks(limit=1000) # Assuming max 1000 tasks for stats
        
        total_runs = len(tasks)
        successful_runs = sum(1 for t in tasks if t.status == "completed")
        failed_runs = sum(1 for t in tasks if t.status == "failed")
        
        durations = [t.stats.duration_seconds or 0 for t in tasks if t.status == "completed" and t.stats]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        total_posts_processed = sum(t.stats.posts_processed for t in tasks if t.stats)
        total_comments_found = sum(t.stats.comments_found for t in tasks if t.stats)
        total_comments_with_keywords = sum(t.stats.comments_with_keywords for t in tasks if t.stats)
        
        return ParserStats(
            total_runs=total_runs,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            average_duration=average_duration,
            total_posts_processed=total_posts_processed,
            total_comments_found=total_comments_found,
            total_comments_with_keywords=total_comments_with_keywords,
        )

def get_redis_parser_manager() -> RedisParserManager:
    """Returns a singleton instance of the RedisParserManager."""
    return RedisParserManager() 