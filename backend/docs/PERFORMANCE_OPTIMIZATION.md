# Performance Optimization Guide

## Текущие проблемы

- Отсутствует кеширование
- Нет connection pooling оптимизации
- Отсутствует pagination для больших данных
- Нет асинхронной обработки тяжелых операций

## Рекомендации

### 1. Database Optimization

```python
# src/database/optimization.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool

def create_optimized_engine(database_url: str):
    return create_async_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=20,  # Увеличить с 10
        max_overflow=30,  # Увеличить с 20
        pool_pre_ping=True,
        pool_recycle=1800,  # 30 минут
        echo=False,  # Отключить в production
        connect_args={
            "server_settings": {
                "application_name": "vk_parser_backend",
                "statement_timeout": "30000",  # 30 секунд
                "idle_in_transaction_session_timeout": "60000"  # 1 минута
            }
        }
    )
```

### 2. Caching Strategy

```python
# src/infrastructure/cache/redis_cache.py
import redis.asyncio as redis
from typing import Any, Optional
import json
import pickle

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        await self.redis.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def get_or_set(self, key: str, factory, ttl: int = 3600):
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await factory()
        await self.set(key, value, ttl)
        return value
```

### 3. Query Optimization

```python
# src/database/query_optimizer.py
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select

class QueryOptimizer:
    @staticmethod
    def optimize_user_queries():
        # Eager loading для связанных данных
        return select(User).options(
            selectinload(User.comments),
            selectinload(User.groups)
        )

    @staticmethod
    def add_pagination(query, page: int, size: int):
        return query.offset((page - 1) * size).limit(size)

    @staticmethod
    def add_indexing_hints():
        # Добавить индексы для часто используемых полей
        return """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_created_at
        ON comments(created_at);

        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_group_id
        ON comments(group_id);

        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_user_id
        ON comments(user_id);
        """
```

### 4. Async Task Processing

```python
# src/tasks/async_processor.py
from celery import Celery
from typing import Any, Dict
import asyncio

class AsyncTaskProcessor:
    def __init__(self, celery_app: Celery):
        self.celery = celery_app

    @self.celery.task(bind=True, max_retries=3)
    def process_large_dataset(self, data: Dict[str, Any]):
        # Обработка больших данных в фоне
        try:
            result = self._process_data(data)
            return {"status": "success", "result": result}
        except Exception as exc:
            # Retry с экспоненциальной задержкой
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

    def _process_data(self, data: Dict[str, Any]) -> Any:
        # Реальная обработка данных
        pass
```

### 5. Response Compression

```python
# src/middleware/compression.py
from fastapi import Request, Response
from fastapi.middleware.gzip import GZipMiddleware
import gzip

class SmartCompressionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Сжимаем только большие ответы
            if self._should_compress(request):
                # Добавляем заголовки сжатия
                pass

        await self.app(scope, receive, send)

    def _should_compress(self, request: Request) -> bool:
        # Логика определения необходимости сжатия
        return True
```

### 6. Database Indexing

```sql
-- src/database/migrations/add_performance_indexes.sql

-- Индексы для комментариев
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_created_at
ON comments(created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_group_id_created_at
ON comments(group_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_user_id_created_at
ON comments(user_id, created_at DESC);

-- Индексы для групп
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_groups_is_active
ON groups(is_active) WHERE is_active = true;

-- Индексы для пользователей
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at
ON users(created_at DESC);

-- Составные индексы для сложных запросов
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_group_user_date
ON comments(group_id, user_id, created_at DESC);
```

### 7. Memory Optimization

```python
# src/utils/memory_optimizer.py
import gc
import psutil
from typing import Generator

class MemoryOptimizer:
    @staticmethod
    def process_large_dataset_in_chunks(data: list, chunk_size: int = 1000) -> Generator:
        """Обработка больших данных по частям"""
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            yield chunk
            gc.collect()  # Принудительная очистка памяти

    @staticmethod
    def get_memory_usage() -> dict:
        """Мониторинг использования памяти"""
        process = psutil.Process()
        return {
            "rss": process.memory_info().rss,
            "vms": process.memory_info().vms,
            "percent": process.memory_percent()
        }
```

## Implementation Priority

1. **Высокий приоритет**: Database indexing, connection pooling
2. **Средний приоритет**: Caching, query optimization
3. **Низкий приоритет**: Compression, memory optimization
