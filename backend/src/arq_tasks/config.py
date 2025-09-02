"""
Конфигурация ARQ модуля

Содержит настройки для работы с асинхронными задачами через ARQ.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class ArqConfig(BaseSettings):
    """
    Конфигурация ARQ для асинхронных задач
    """

    # Основные настройки
    enabled: bool = Field(
        default=True, description="Включены ли асинхронные задачи ARQ"
    )

    # Настройки воркера
    max_jobs: int = Field(
        default=10,
        description="Максимальное количество одновременно выполняемых задач",
    )
    job_timeout: int = Field(
        default=300,
        description="Таймаут выполнения задачи в секундах (5 минут)",
    )
    max_tries: int = Field(
        default=3,
        description="Максимальное количество попыток выполнения задачи",
    )

    # Настройки очереди
    queue_name: str = Field(default="arq:queue", description="Имя очереди ARQ")
    poll_delay: float = Field(
        default=0.5, description="Задержка между опросами очереди в секундах"
    )

    # Настройки результатов
    keep_result: int = Field(
        default=3600,
        description="Время хранения результатов задач в секундах (1 час)",
    )
    keep_result_forever: bool = Field(
        default=False, description="Хранить результаты задач вечно"
    )

    # Настройки здоровья
    health_check_interval: int = Field(
        default=60, description="Интервал проверки здоровья в секундах"
    )
    health_check_key: Optional[str] = Field(
        default="arq:health-check",
        description="Ключ Redis для проверки здоровья",
    )

    # Настройки burst режима
    burst_mode: bool = Field(
        default=False,
        description="Режим burst - остановка после обработки всех задач",
    )
    max_burst_jobs: int = Field(
        default=-1,
        description="Максимальное количество задач в burst режиме (-1 = без ограничений)",
    )

    # Cron задачи
    cron_enabled: bool = Field(
        default=True, description="Включены ли cron задачи"
    )

    class Config:
        """Конфигурация Pydantic"""

        env_prefix = "ARQ_"
        case_sensitive = False


# Глобальный объект конфигурации ARQ
arq_config = ArqConfig()
