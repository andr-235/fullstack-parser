"""
Celery Application Instance

Основное приложение Celery для обработки асинхронных задач.
"""

from celery import Celery
from .config import config_service as settings

# Настройка Celery приложения
app = Celery(
    "vk_parser",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.celery_tasks.service"],  # Подключаем наши задачи
)

# Настройки Celery
app.conf.update(
    # Основные настройки
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Настройки воркера
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    # Настройки результатов
    result_expires=3600,  # 1 час
    result_backend_transport_options={"master_name": "mymaster"},
    # Настройки очередей
    task_default_queue="vk_parser",
    task_queues={
        "vk_parser": {
            "exchange": "vk_parser",
            "exchange_type": "direct",
            "routing_key": "vk_parser",
        },
    },
    # Настройки задач
    task_routes={
        "celery_tasks.service.parse_vk_comments_task": {"queue": "vk_parser"},
        "celery_tasks.service.analyze_text_morphology_task": {
            "queue": "vk_parser"
        },
        "celery_tasks.service.extract_keywords_task": {"queue": "vk_parser"},
        "celery_tasks.service.send_notification_task": {"queue": "vk_parser"},
        "celery_tasks.service.generate_report_task": {"queue": "vk_parser"},
        "celery_tasks.service.cleanup_old_data_task": {"queue": "vk_parser"},
        "celery_tasks.service.process_batch_comments_task": {
            "queue": "vk_parser"
        },
        "celery_tasks.service.update_statistics_task": {"queue": "vk_parser"},
        "celery_tasks.service.backup_database_task": {"queue": "vk_parser"},
    },
)

app.autodiscover_tasks()

if __name__ == "__main__":
    app.start()
