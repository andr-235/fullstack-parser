"""
Настройки ARQ Worker

Содержит WorkerSettings для запуска ARQ воркера.
"""

import logging
from arq import Worker
from arq.connections import RedisSettings

from .service import ALL_TASKS
from .config import arq_config
from ..config import settings

logger = logging.getLogger(__name__)


class ArqWorkerSettings:
    """
    Настройки для ARQ воркера

    Используется CLI командой arq для запуска воркера.
    """

    # Список функций, которые может выполнять воркер
    functions = ALL_TASKS

    # Настройки Redis подключения
    redis_settings = RedisSettings.from_dsn(settings.redis_url)

    # Настройки воркера
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

    # Настройки логирования
    @classmethod
    def logging_config(cls, verbose: bool) -> dict:
        """
        Конфигурация логирования для воркера

        Args:
            verbose: Включить verbose режим

        Returns:
            Конфигурация логирования
        """
        from arq.logs import default_log_config

        return default_log_config(verbose)


# Экземпляр настроек для использования в CLI
worker_settings = ArqWorkerSettings()


def create_worker_settings(**overrides) -> ArqWorkerSettings:
    """
    Создание настроек воркера с переопределениями

    Args:
        **overrides: Параметры для переопределения

    Returns:
        ArqWorkerSettings с переопределенными параметрами
    """
    settings = ArqWorkerSettings()

    # Применяем переопределения
    for key, value in overrides.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
            logger.info(f"Переопределен параметр {key} = {value}")

    return settings
