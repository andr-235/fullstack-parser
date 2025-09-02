"""
Настройки ARQ Worker

Содержит WorkerSettings для запуска ARQ воркера.
"""

import logging
from arq import Worker
from arq.connections import RedisSettings

from .service import (
    parse_vk_comments,
    analyze_text_morphology,
    extract_keywords,
    send_notification,
    generate_report,
    cleanup_old_data,
    process_batch_comments,
    update_statistics,
    backup_database,
)
from .config import arq_config
from ..config import settings

logger = logging.getLogger(__name__)


# Настройки ARQ воркера согласно документации Context7

# Настройки Redis подключения для WorkerSettings
redis_settings = RedisSettings.from_dsn(settings.redis_url)


def create_worker_settings(**overrides):
    """
    Создание настроек воркера с переопределениями

    Args:
        **overrides: Параметры для переопределения

    Returns:
        WorkerSettings с переопределенными параметрами
    """
    # Создаем копию настроек
    settings_obj = WorkerSettings()

    # Применяем переопределения
    for key, value in overrides.items():
        if hasattr(settings_obj, key):
            setattr(settings_obj, key, value)
            logger.info(f"Переопределен параметр {key} = {value}")

    return settings_obj


# Экземпляр настроек для использования ARQ CLI
# Согласно документации Context7, WorkerSettings должен быть классом с атрибутами
class WorkerSettings:
    """
    Настройки для ARQ воркера

    Functions должен быть списком функций, а не словарем!
    """

    # Список функций, которые может выполнять воркер (список, не словарь!)
    functions = [
        parse_vk_comments,
        analyze_text_morphology,
        extract_keywords,
        send_notification,
        generate_report,
        cleanup_old_data,
        process_batch_comments,
        update_statistics,
        backup_database,
    ]

    # Настройки Redis подключения
    redis_settings = redis_settings

    # Основные настройки воркера
    max_jobs = arq_config.max_jobs
    job_timeout = arq_config.job_timeout
    keep_result = arq_config.keep_result
    max_tries = arq_config.max_tries
    poll_delay = arq_config.poll_delay
    health_check_interval = arq_config.health_check_interval

    # Настройки очереди
    queue_name = arq_config.queue_name

    # Настройки burst режима
    burst = arq_config.burst_mode
    max_burst_jobs = (
        arq_config.max_burst_jobs if arq_config.max_burst_jobs > 0 else -1
    )

    # Настройки результата
    keep_result_forever = arq_config.keep_result_forever

    # Дополнительные настройки
    job_serializer = None  # Используем pickle по умолчанию
    job_deserializer = None  # Используем pickle по умолчанию


# ARQ ищет эту переменную в модуле
worker_settings = WorkerSettings()
