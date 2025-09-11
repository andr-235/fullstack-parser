# Scalability Architecture Guide

## Текущие ограничения

- Монолитная архитектура
- Отсутствует горизонтальное масштабирование
- Нет load balancing
- Ограниченная обработка concurrent requests

## Рекомендации

### 1. Microservices Architecture

```python
# src/services/service_registry.py
from typing import Dict, Any
import httpx

class ServiceRegistry:
    def __init__(self):
        self.services = {
            "auth": "http://auth-service:8001",
            "comments": "http://comments-service:8002",
            "parser": "http://parser-service:8003",
            "analytics": "http://analytics-service:8004"
        }

    async def call_service(self, service_name: str, endpoint: str, **kwargs):
        base_url = self.services.get(service_name)
        if not base_url:
            raise ValueError(f"Service {service_name} not found")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}{endpoint}", **kwargs)
            return response.json()
```

### 2. Load Balancing Configuration

```yaml
# docker-compose.scale.yml
version: "3.8"
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend-1
      - backend-2
      - backend-3

  backend-1:
    build: .
    environment:
      - INSTANCE_ID=1
    depends_on:
      - postgres
      - redis

  backend-2:
    build: .
    environment:
      - INSTANCE_ID=2
    depends_on:
      - postgres
      - redis

  backend-3:
    build: .
    environment:
      - INSTANCE_ID=3
    depends_on:
      - postgres
      - redis
```

### 3. Database Sharding Strategy

```python
# src/database/sharding.py
from typing import Any, Dict
import hashlib

class DatabaseSharding:
    def __init__(self, shard_configs: list):
        self.shards = shard_configs
        self.shard_count = len(shard_configs)

    def get_shard(self, key: str) -> str:
        """Определение шарда по ключу"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        shard_index = hash_value % self.shard_count
        return self.shards[shard_index]

    def get_shard_for_user(self, user_id: int) -> str:
        """Получение шарда для пользователя"""
        return self.get_shard(f"user_{user_id}")

    def get_shard_for_group(self, group_id: int) -> str:
        """Получение шарда для группы"""
        return self.get_shard(f"group_{group_id}")
```

### 4. Message Queue Integration

```python
# src/queue/message_queue.py
from celery import Celery
from kombu import Queue
import redis

class MessageQueueManager:
    def __init__(self, broker_url: str, result_backend: str):
        self.celery = Celery(
            'vk_parser',
            broker=broker_url,
            backend=result_backend
        )
        self._configure_queues()

    def _configure_queues(self):
        self.celery.conf.task_routes = {
            'parser.tasks.parse_comments': {'queue': 'parser'},
            'analytics.tasks.process_data': {'queue': 'analytics'},
            'notifications.tasks.send_email': {'queue': 'notifications'},
        }

        self.celery.conf.task_queues = (
            Queue('parser', routing_key='parser'),
            Queue('analytics', routing_key='analytics'),
            Queue('notifications', routing_key='notifications'),
        )

    async def enqueue_task(self, task_name: str, *args, **kwargs):
        return self.celery.send_task(task_name, args=args, kwargs=kwargs)
```

### 5. Caching Strategy

```python
# src/cache/distributed_cache.py
import redis.asyncio as redis
from typing import Any, Optional
import json
import pickle

class DistributedCache:
    def __init__(self, redis_cluster_urls: list):
        self.redis_cluster = redis.RedisCluster(
            startup_nodes=redis_cluster_urls,
            decode_responses=True,
            skip_full_coverage_check=True
        )

    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis_cluster.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        try:
            await self.redis_cluster.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception:
            pass  # Graceful degradation

    async def invalidate_pattern(self, pattern: str):
        """Инвалидация по паттерну"""
        keys = await self.redis_cluster.keys(pattern)
        if keys:
            await self.redis_cluster.delete(*keys)
```

### 6. API Gateway Configuration

```python
# src/gateway/api_gateway.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

class APIGateway:
    def __init__(self):
        self.app = FastAPI(title="VK Parser API Gateway")
        self.service_registry = ServiceRegistry()
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        @self.app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_request(service_name: str, path: str, request: Request):
            return await self._forward_request(service_name, path, request)

    async def _forward_request(self, service_name: str, path: str, request: Request):
        try:
            service_url = self.service_registry.get_service_url(service_name)
            if not service_url:
                raise HTTPException(status_code=404, detail="Service not found")

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=f"{service_url}/{path}",
                    headers=dict(request.headers),
                    content=await request.body()
                )
                return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

### 7. Monitoring and Metrics

```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

class MetricsCollector:
    def __init__(self):
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections'
        )
        self.database_connections = Gauge(
            'database_connections',
            'Number of database connections'
        )

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def update_connections(self, active: int, db: int):
        self.active_connections.set(active)
        self.database_connections.set(db)
```

### 8. Auto-scaling Configuration

```yaml
# kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vk-parser-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vk-parser-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## Implementation Roadmap

### Phase 1: Foundation (1-2 месяца)

- Настройка load balancer
- Внедрение Redis для кеширования
- Добавление базового мониторинга

### Phase 2: Microservices (2-3 месяца)

- Выделение auth service
- Выделение parser service
- Настройка service discovery

### Phase 3: Advanced Scaling (3-4 месяца)

- Database sharding
- Message queue implementation
- Auto-scaling configuration

### Phase 4: Optimization (1-2 месяца)

- Performance tuning
- Advanced monitoring
- Disaster recovery setup
