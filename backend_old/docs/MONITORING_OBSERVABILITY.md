# Monitoring & Observability Guide

## Текущие проблемы

- Отсутствует централизованное логирование
- Нет метрик производительности
- Отсутствует трейсинг запросов
- Нет алертинга при проблемах
- Слабая диагностика ошибок

## Рекомендации

### 1. Centralized Logging

```python
# src/monitoring/logging_config.py
import logging
import json
from datetime import datetime
from typing import Dict, Any
import structlog
from pythonjsonlogger import jsonlogger

class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._setup_logging()

    def _setup_logging(self):
        # Настройка structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Настройка JSON formatter для файлов
        json_handler = logging.FileHandler('app.log')
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        json_handler.setFormatter(json_formatter)

        # Настройка root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(json_handler)
        root_logger.setLevel(logging.INFO)

    def get_logger(self, name: str):
        return structlog.get_logger(name).bind(service=self.service_name)

    def log_request(self, request_id: str, method: str, url: str,
                   user_id: str = None, duration: float = None):
        logger = self.get_logger("request")
        logger.info(
            "HTTP request",
            request_id=request_id,
            method=method,
            url=url,
            user_id=user_id,
            duration_ms=duration * 1000 if duration else None
        )

    def log_error(self, request_id: str, error: Exception,
                 context: Dict[str, Any] = None):
        logger = self.get_logger("error")
        logger.error(
            "Application error",
            request_id=request_id,
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {}
        )
```

### 2. Metrics Collection

```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from typing import Dict, Any

class MetricsCollector:
    def __init__(self):
        # HTTP метрики
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )

        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
        )

        # Бизнес метрики
        self.comments_parsed_total = Counter(
            'comments_parsed_total',
            'Total comments parsed',
            ['group_id', 'status']
        )

        self.vk_api_requests_total = Counter(
            'vk_api_requests_total',
            'Total VK API requests',
            ['method', 'status']
        )

        # Системные метрики
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections'
        )

        self.database_connections = Gauge(
            'database_connections',
            'Number of database connections'
        )

        self.redis_connections = Gauge(
            'redis_connections',
            'Number of Redis connections'
        )

        # Ошибки
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'service']
        )

    def record_request(self, method: str, endpoint: str,
                      status_code: int, duration: float):
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def record_comment_parsed(self, group_id: str, status: str):
        self.comments_parsed_total.labels(
            group_id=group_id,
            status=status
        ).inc()

    def record_vk_api_request(self, method: str, status: str):
        self.vk_api_requests_total.labels(
            method=method,
            status=status
        ).inc()

    def record_error(self, error_type: str, service: str):
        self.errors_total.labels(
            error_type=error_type,
            service=service
        ).inc()

    def update_connections(self, active: int, db: int, redis: int):
        self.active_connections.set(active)
        self.database_connections.set(db)
        self.redis_connections.set(redis)

    def start_metrics_server(self, port: int = 8000):
        start_http_server(port)
```

### 3. Distributed Tracing

```python
# src/monitoring/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
import logging

class TracingSetup:
    def __init__(self, service_name: str, jaeger_endpoint: str):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint
        self._setup_tracing()

    def _setup_tracing(self):
        # Настройка Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger",
            agent_port=14268,
        )

        # Настройка tracer provider
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)

        # Добавление span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        # Инструментация библиотек
        FastAPIInstrumentor.instrument_app(self.app)
        SQLAlchemyInstrumentor().instrument()
        RedisInstrumentor().instrument()

    def create_span(self, name: str, attributes: Dict[str, Any] = None):
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span(name)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        return span
```

### 4. Health Checks

```python
# src/monitoring/health_checks.py
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import asyncio
import aiohttp
import redis.asyncio as redis
from sqlalchemy import text

class HealthChecker:
    def __init__(self, database_service, redis_url: str):
        self.database_service = database_service
        self.redis_url = redis_url
        self.checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "external_apis": self._check_external_apis,
            "disk_space": self._check_disk_space,
            "memory": self._check_memory
        }

    async def _check_database(self) -> Dict[str, Any]:
        try:
            async with self.database_service.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                return {
                    "status": "healthy",
                    "response_time_ms": 0,  # Можно измерить
                    "details": "Database connection successful"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connection failed"
            }

    async def _check_redis(self) -> Dict[str, Any]:
        try:
            redis_client = redis.from_url(self.redis_url)
            await redis_client.ping()
            await redis_client.close()
            return {
                "status": "healthy",
                "details": "Redis connection successful"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Redis connection failed"
            }

    async def _check_external_apis(self) -> Dict[str, Any]:
        vk_api_status = await self._check_vk_api()
        return {
            "status": "healthy" if vk_api_status else "degraded",
            "vk_api": vk_api_status,
            "details": "External APIs check completed"
        }

    async def _check_vk_api(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.vk.com/method/users.get",
                    params={"user_ids": "1", "v": "5.199"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception:
            return False

    async def _check_disk_space(self) -> Dict[str, Any]:
        import shutil
        try:
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100

            status = "healthy" if free_percent > 10 else "warning" if free_percent > 5 else "critical"

            return {
                "status": status,
                "free_space_gb": free / (1024**3),
                "free_percent": free_percent,
                "details": f"Disk space: {free_percent:.1f}% free"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Disk space check failed"
            }

    async def _check_memory(self) -> Dict[str, Any]:
        import psutil
        try:
            memory = psutil.virtual_memory()
            status = "healthy" if memory.percent < 80 else "warning" if memory.percent < 90 else "critical"

            return {
                "status": status,
                "used_percent": memory.percent,
                "available_gb": memory.available / (1024**3),
                "details": f"Memory usage: {memory.percent:.1f}%"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Memory check failed"
            }

    async def get_health_status(self) -> Dict[str, Any]:
        results = {}
        overall_status = "healthy"

        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result

                if result["status"] == "unhealthy":
                    overall_status = "unhealthy"
                elif result["status"] == "warning" and overall_status == "healthy":
                    overall_status = "warning"
            except Exception as e:
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }
```

### 5. Alerting System

```python
# src/monitoring/alerting.py
from typing import Dict, Any, List
import asyncio
import aiohttp
from datetime import datetime, timedelta
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertManager:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.alert_history = []
        self.thresholds = {
            "error_rate": 0.05,  # 5% ошибок
            "response_time": 2.0,  # 2 секунды
            "memory_usage": 90,  # 90%
            "disk_usage": 85,  # 85%
            "database_connections": 80  # 80% от пула
        }

    async def check_thresholds(self, metrics: Dict[str, Any]):
        alerts = []

        # Проверка error rate
        if metrics.get("error_rate", 0) > self.thresholds["error_rate"]:
            alerts.append({
                "level": AlertLevel.CRITICAL,
                "message": f"High error rate: {metrics['error_rate']:.2%}",
                "metric": "error_rate",
                "value": metrics["error_rate"]
            })

        # Проверка response time
        if metrics.get("avg_response_time", 0) > self.thresholds["response_time"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "message": f"Slow response time: {metrics['avg_response_time']:.2f}s",
                "metric": "response_time",
                "value": metrics["avg_response_time"]
            })

        # Проверка memory usage
        if metrics.get("memory_usage", 0) > self.thresholds["memory_usage"]:
            alerts.append({
                "level": AlertLevel.CRITICAL,
                "message": f"High memory usage: {metrics['memory_usage']:.1f}%",
                "metric": "memory_usage",
                "value": metrics["memory_usage"]
            })

        # Отправка алертов
        for alert in alerts:
            await self.send_alert(alert)

    async def send_alert(self, alert: Dict[str, Any]):
        alert["timestamp"] = datetime.utcnow().isoformat()
        self.alert_history.append(alert)

        # Отправка в webhook (Slack, Discord, etc.)
        if self.webhook_url:
            await self._send_webhook(alert)

        # Логирование
        print(f"ALERT [{alert['level'].value.upper()}]: {alert['message']}")

    async def _send_webhook(self, alert: Dict[str, Any]):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": f"🚨 {alert['message']}",
                    "attachments": [{
                        "color": "danger" if alert["level"] == AlertLevel.CRITICAL else "warning",
                        "fields": [
                            {"title": "Metric", "value": alert["metric"], "short": True},
                            {"title": "Value", "value": str(alert["value"]), "short": True},
                            {"title": "Time", "value": alert["timestamp"], "short": False}
                        ]
                    }]
                }

                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status != 200:
                        print(f"Failed to send alert: {response.status}")
        except Exception as e:
            print(f"Error sending alert: {e}")
```

### 6. Dashboard Configuration

```yaml
# monitoring/grafana/dashboards/api-dashboard.json
{
  "dashboard":
    {
      "title": "VK Parser API Dashboard",
      "panels":
        [
          {
            "title": "Request Rate",
            "type": "graph",
            "targets":
              [
                {
                  "expr": "rate(http_requests_total[5m])",
                  "legendFormat": "{{method}} {{endpoint}}",
                },
              ],
          },
          {
            "title": "Response Time",
            "type": "graph",
            "targets":
              [
                {
                  "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                  "legendFormat": "95th percentile",
                },
              ],
          },
          {
            "title": "Error Rate",
            "type": "singlestat",
            "targets":
              [
                {
                  "expr": 'rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m])',
                  "format": "percent",
                },
              ],
          },
          {
            "title": "Active Connections",
            "type": "graph",
            "targets":
              [
                { "expr": "active_connections", "legendFormat": "Active" },
                { "expr": "database_connections", "legendFormat": "Database" },
              ],
          },
        ],
    },
}
```

### 7. Log Aggregation

```yaml
# monitoring/fluentd/fluent.conf
<source>
@type tail
path /app/logs/*.log
pos_file /var/log/fluentd/app.log.pos
tag app.logs
format json
</source>

<filter app.logs>
@type record_transformer
<record>
service_name "vk-parser-api"
environment "#{ENV['ENVIRONMENT'] || 'development'}"
</record>
</filter>

<match app.logs>
@type elasticsearch
host elasticsearch
port 9200
index_name vk-parser-logs
type_name _doc
</match>
```

## Implementation Plan

### Phase 1: Basic Monitoring (Week 1-2)

- [ ] Настроить structured logging
- [ ] Добавить базовые метрики
- [ ] Реализовать health checks
- [ ] Настроить log aggregation

### Phase 2: Advanced Observability (Week 3-4)

- [ ] Внедрить distributed tracing
- [ ] Настроить alerting
- [ ] Создать dashboards
- [ ] Добавить business metrics

### Phase 3: Production Ready (Week 5-6)

- [ ] Настроить log retention
- [ ] Оптимизировать performance
- [ ] Добавить SLA monitoring
- [ ] Настроить incident response
