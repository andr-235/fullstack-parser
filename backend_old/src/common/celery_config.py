"""
Конфигурация Celery
"""

import os
from typing import Any, Dict

from celery import Celery
from kombu import Queue


def get_redis_url() -> str:
    """Получить URL Redis"""
    return os.getenv(
        "REDIS_URL",
        "redis://redis:6379/0"
    )


def get_celery_config() -> Dict[str, Any]:
    """Получить конфигурацию Celery"""
    return {
        # Основные настройки
        "broker_url": get_redis_url(),
        "result_backend": get_redis_url(),
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "UTC",
        "enable_utc": True,
        
        # Настройки задач
        "task_always_eager": os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true",
        "task_eager_propagates": True,
        "task_ignore_result": False,
        "task_store_eager_result": True,
        
        # Настройки очередей
        "task_default_queue": "default",
        "task_queues": (
            Queue("default", routing_key="default"),
            Queue("high_priority", routing_key="high_priority"),
            Queue("low_priority", routing_key="low_priority"),
            Queue("parser", routing_key="parser"),
            Queue("notifications", routing_key="notifications"),
        ),
        "task_routes": {
            "parser.*": {"queue": "parser"},
            "notifications.*": {"queue": "notifications"},
            "high_priority.*": {"queue": "high_priority"},
            "low_priority.*": {"queue": "low_priority"},
        },
        
        # Настройки воркеров
        "worker_prefetch_multiplier": 1,
        "worker_max_tasks_per_child": 1000,
        "worker_disable_rate_limits": False,
        
        # Настройки retry
        "task_acks_late": True,
        "worker_prefetch_multiplier": 1,
        "task_reject_on_worker_lost": True,
        
        # Настройки мониторинга
        "worker_send_task_events": True,
        "task_send_sent_event": True,
        
        # Настройки результата
        "result_expires": 3600,  # 1 час
        "result_cache_max": 10000,
        
        # Настройки безопасности
        "worker_hijack_root_logger": False,
        "worker_log_color": False,
        
        # Настройки производительности
        "task_compression": "gzip",
        "result_compression": "gzip",
        "task_compression_threshold": 1024,
        
        # Настройки отладки
        "task_track_started": True,
        "task_time_limit": 300,  # 5 минут
        "task_soft_time_limit": 240,  # 4 минуты
    }


def create_celery_app() -> Celery:
    """Создать экземпляр Celery"""
    celery_app = Celery("vk_parser")
    celery_app.config_from_object(get_celery_config())
    
    # Автоматическое обнаружение задач
    celery_app.autodiscover_tasks([
        "src.parser.tasks",
        "src.notifications.tasks",
        "src.morphological.tasks",
    ])
    
    return celery_app


# Глобальный экземпляр Celery
celery_app = create_celery_app()
