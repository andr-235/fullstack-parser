"""
Celery Worker Settings

Настройки для Celery воркера.
Замена для ARQ worker с более надежной системой очередей.
"""

import logging
from ..celery_app import app

logger = logging.getLogger(__name__)


# Настройки Celery воркера
class CeleryWorkerSettings:
    """
    Настройки для Celery воркера

    Аналог WorkerSettings из ARQ, но для Celery
    """

    # Ссылка на Celery приложение
    app = app

    # Настройки воркера
    worker_prefetch_multiplier = 1
    worker_disable_rate_limits = False
    worker_send_task_events = True
    worker_state_db = None

    # Настройки задач
    task_acks_late = True
    task_reject_on_worker_lost = True
    task_default_rate_limit = None

    # Настройки сериализации
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]

    # Настройки результатов
    result_expires = 3600  # 1 час
    result_backend_transport_options = {"master_name": "mymaster"}

    # Настройки очередей
    task_default_queue = "vk_parser"
    task_queues = {
        "vk_parser": {
            "exchange": "vk_parser",
            "exchange_type": "direct",
            "routing_key": "vk_parser",
        },
    }

    # Настройки маршрутизации задач
    task_routes = {
        "celery_tasks.parse_vk_comments": {"queue": "vk_parser"},
        "celery_tasks.analyze_text_morphology": {"queue": "vk_parser"},
        "celery_tasks.extract_keywords": {"queue": "vk_parser"},
        "celery_tasks.send_notification": {"queue": "vk_parser"},
        "celery_tasks.generate_report": {"queue": "vk_parser"},
        "celery_tasks.cleanup_old_data": {"queue": "vk_parser"},
        "celery_tasks.process_batch_comments": {"queue": "vk_parser"},
        "celery_tasks.update_statistics": {"queue": "vk_parser"},
        "celery_tasks.backup_database": {"queue": "vk_parser"},
    }

    # Настройки логирования
    worker_log_format = (
        "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
    )
    worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s"

    @classmethod
    def logging_config(cls, verbose: bool = False) -> dict:
        """
        Конфигурация логирования для воркера

        Args:
            verbose: Включить verbose режим

        Returns:
            Конфигурация логирования
        """
        import logging

        level = logging.DEBUG if verbose else logging.INFO

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "celery": {
                    "format": cls.worker_log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "celery_task": {
                    "format": cls.worker_task_log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "celery",
                    "level": level,
                },
                "task_console": {
                    "class": "logging.StreamHandler",
                    "formatter": "celery_task",
                    "level": level,
                },
            },
            "loggers": {
                "celery": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "celery.worker": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "celery.task": {
                    "handlers": ["task_console"],
                    "level": level,
                    "propagate": False,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
        }


# Экземпляр настроек для использования
worker_settings = CeleryWorkerSettings()


def create_worker_settings(**overrides):
    """
    Создание настроек воркера с переопределениями

    Args:
        **overrides: Параметры для переопределения

    Returns:
        CeleryWorkerSettings с переопределенными параметрами
    """
    settings_obj = CeleryWorkerSettings()

    # Применяем переопределения
    for key, value in overrides.items():
        if hasattr(settings_obj, key):
            setattr(settings_obj, key, value)
            logger.info(f"Переопределен параметр {key} = {value}")

    return settings_obj


# Экспорт
__all__ = [
    "CeleryWorkerSettings",
    "worker_settings",
    "create_worker_settings",
]
