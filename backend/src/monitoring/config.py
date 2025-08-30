"""
Конфигурация модуля Monitoring

Содержит настройки специфичные для модуля мониторинга групп
"""

from typing import Optional, List

from ..config import settings


class MonitoringConfig:
    """Конфигурация для модуля мониторинга"""

    # Настройки интервалов
    DEFAULT_INTERVAL_MINUTES = 5
    MIN_INTERVAL_MINUTES = 1
    MAX_INTERVAL_MINUTES = 1440  # 24 часа

    # Настройки параллелизма
    DEFAULT_MAX_CONCURRENT = 10
    MAX_CONCURRENT_LIMIT = 100
    MIN_CONCURRENT_LIMIT = 1

    # Настройки повторных попыток
    DEFAULT_MAX_RETRIES = 3
    MAX_RETRIES_LIMIT = 10
    MIN_RETRIES_LIMIT = 0

    # Настройки таймаутов
    DEFAULT_TIMEOUT_SECONDS = 30
    MIN_TIMEOUT_SECONDS = 5
    MAX_TIMEOUT_SECONDS = 300

    # Настройки очередей
    MAX_QUEUE_SIZE = 1000
    MAX_ACTIVE_TASKS = 50

    # Настройки уведомлений
    DEFAULT_NOTIFICATION_CHANNELS = ["email", "webhook", "telegram"]
    SUPPORTED_NOTIFICATION_CHANNELS = ["email", "webhook", "telegram", "slack"]

    # Настройки планировщика
    SCHEDULER_CHECK_INTERVAL = 30  # секунд
    SCHEDULER_MAX_DELAY = 3600  # 1 час

    # Настройки хранения результатов
    RESULTS_RETENTION_DAYS = 30
    MAX_RESULTS_PER_MONITORING = 1000

    # Настройки здоровья системы
    HEALTH_CHECK_INTERVAL = 60
    HEALTH_FAILURE_THRESHOLD = 3

    @classmethod
    def get_default_config(cls) -> dict:
        """Получить конфигурацию по умолчанию"""
        return {
            "interval_minutes": cls.DEFAULT_INTERVAL_MINUTES,
            "max_concurrent_groups": cls.DEFAULT_MAX_CONCURRENT,
            "enable_auto_retry": True,
            "max_retries": cls.DEFAULT_MAX_RETRIES,
            "timeout_seconds": cls.DEFAULT_TIMEOUT_SECONDS,
            "enable_notifications": False,
            "notification_channels": [],
        }

    @classmethod
    def get_scheduler_config(cls) -> dict:
        """Получить конфигурацию планировщика"""
        return {
            "check_interval": cls.SCHEDULER_CHECK_INTERVAL,
            "max_delay": cls.SCHEDULER_MAX_DELAY,
            "max_queue_size": cls.MAX_QUEUE_SIZE,
            "max_active_tasks": cls.MAX_ACTIVE_TASKS,
        }

    @classmethod
    def get_limits_config(cls) -> dict:
        """Получить конфигурацию лимитов"""
        return {
            "min_interval": cls.MIN_INTERVAL_MINUTES,
            "max_interval": cls.MAX_INTERVAL_MINUTES,
            "min_concurrent": cls.MIN_CONCURRENT_LIMIT,
            "max_concurrent": cls.MAX_CONCURRENT_LIMIT,
            "min_retries": cls.MIN_RETRIES_LIMIT,
            "max_retries": cls.MAX_RETRIES_LIMIT,
            "min_timeout": cls.MIN_TIMEOUT_SECONDS,
            "max_timeout": cls.MAX_TIMEOUT_SECONDS,
        }

    @classmethod
    def get_notification_config(cls) -> dict:
        """Получить конфигурацию уведомлений"""
        return {
            "default_channels": cls.DEFAULT_NOTIFICATION_CHANNELS,
            "supported_channels": cls.SUPPORTED_NOTIFICATION_CHANNELS,
        }

    @classmethod
    def get_storage_config(cls) -> dict:
        """Получить конфигурацию хранения"""
        return {
            "results_retention_days": cls.RESULTS_RETENTION_DAYS,
            "max_results_per_monitoring": cls.MAX_RESULTS_PER_MONITORING,
        }

    @classmethod
    def get_health_config(cls) -> dict:
        """Получить конфигурацию здоровья"""
        return {
            "check_interval": cls.HEALTH_CHECK_INTERVAL,
            "failure_threshold": cls.HEALTH_FAILURE_THRESHOLD,
        }

    @classmethod
    def validate_config(cls, config: dict) -> List[str]:
        """
        Валидировать конфигурацию мониторинга

        Args:
            config: Конфигурация для валидации

        Returns:
            List[str]: Список ошибок валидации
        """
        errors = []

        # Валидация интервала
        if "interval_minutes" in config:
            interval = config["interval_minutes"]
            if not (
                cls.MIN_INTERVAL_MINUTES
                <= interval
                <= cls.MAX_INTERVAL_MINUTES
            ):
                errors.append(
                    f"interval_minutes должен быть от {cls.MIN_INTERVAL_MINUTES} до {cls.MAX_INTERVAL_MINUTES}"
                )

        # Валидация максимального количества одновременных задач
        if "max_concurrent_groups" in config:
            concurrent = config["max_concurrent_groups"]
            if not (
                cls.MIN_CONCURRENT_LIMIT
                <= concurrent
                <= cls.MAX_CONCURRENT_LIMIT
            ):
                errors.append(
                    f"max_concurrent_groups должен быть от {cls.MIN_CONCURRENT_LIMIT} до {cls.MAX_CONCURRENT_LIMIT}"
                )

        # Валидация максимального количества повторных попыток
        if "max_retries" in config:
            retries = config["max_retries"]
            if not (cls.MIN_RETRIES_LIMIT <= retries <= cls.MAX_RETRIES_LIMIT):
                errors.append(
                    f"max_retries должен быть от {cls.MIN_RETRIES_LIMIT} до {cls.MAX_RETRIES_LIMIT}"
                )

        # Валидация таймаута
        if "timeout_seconds" in config:
            timeout = config["timeout_seconds"]
            if not (
                cls.MIN_TIMEOUT_SECONDS <= timeout <= cls.MAX_TIMEOUT_SECONDS
            ):
                errors.append(
                    f"timeout_seconds должен быть от {cls.MIN_TIMEOUT_SECONDS} до {cls.MAX_TIMEOUT_SECONDS}"
                )

        # Валидация каналов уведомлений
        if "notification_channels" in config:
            channels = config["notification_channels"]
            if not isinstance(channels, list):
                errors.append("notification_channels должен быть списком")
            else:
                for channel in channels:
                    if channel not in cls.SUPPORTED_NOTIFICATION_CHANNELS:
                        errors.append(
                            f"Неподдерживаемый канал уведомлений: {channel}. "
                            f"Поддерживаемые: {', '.join(cls.SUPPORTED_NOTIFICATION_CHANNELS)}"
                        )

        return errors


# Экземпляр конфигурации
monitoring_config = MonitoringConfig()


# Экспорт
__all__ = [
    "MonitoringConfig",
    "monitoring_config",
]
