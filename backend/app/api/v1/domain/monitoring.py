"""
Domain сущности для системы мониторинга VK групп (DDD)
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from .base import Entity, ValueObject


class MonitoringStatus(ValueObject):
    """Статус мониторинга"""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

    def __init__(self, status: str = ACTIVE):
        if status not in [self.ACTIVE, self.PAUSED, self.STOPPED, self.ERROR]:
            raise ValueError(f"Invalid monitoring status: {status}")
        self.status = status

    def is_active(self) -> bool:
        return self.status == self.ACTIVE

    def is_paused(self) -> bool:
        return self.status == self.PAUSED

    def can_be_started(self) -> bool:
        return self.status in [self.STOPPED, self.ERROR]

    def can_be_paused(self) -> bool:
        return self.status == self.ACTIVE

    def __str__(self) -> str:
        return self.status


class MonitoringConfig(ValueObject):
    """Конфигурация мониторинга"""

    def __init__(
        self,
        interval_seconds: int = 300,
        max_concurrent_groups: int = 10,
        enable_auto_retry: bool = True,
        max_retries: int = 3,
        timeout_seconds: int = 30,
        enable_notifications: bool = False,
        notification_channels: Optional[List[str]] = None,
    ):
        self.interval_seconds = max(30, interval_seconds)  # минимум 30 секунд
        self.max_concurrent_groups = max(1, max_concurrent_groups)
        self.enable_auto_retry = enable_auto_retry
        self.max_retries = max(0, max_retries)
        self.timeout_seconds = max(5, timeout_seconds)
        self.enable_notifications = enable_notifications
        self.notification_channels = notification_channels or []


class MonitoringResult(ValueObject):
    """Результат цикла мониторинга"""

    def __init__(
        self,
        group_id: int,
        posts_found: int = 0,
        comments_found: int = 0,
        keywords_found: Optional[List[str]] = None,
        processing_time: float = 0.0,
        errors: Optional[List[str]] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ):
        self.group_id = group_id
        self.posts_found = posts_found
        self.comments_found = comments_found
        self.keywords_found = keywords_found or []
        self.processing_time = processing_time
        self.errors = errors or []
        self.started_at = started_at or datetime.utcnow()
        self.completed_at = completed_at

    def mark_completed(self) -> None:
        """Отметить как завершенное"""
        self.completed_at = datetime.utcnow()

    def add_error(self, error: str) -> None:
        """Добавить ошибку"""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Проверить наличие ошибок"""
        return len(self.errors) > 0

    def get_duration(self) -> float:
        """Получить длительность выполнения"""
        if not self.completed_at:
            return 0.0
        return (self.completed_at - self.started_at).total_seconds()


class VKGroupMonitoring(Entity):
    """Доменная сущность мониторинга VK группы"""

    def __init__(
        self,
        id: Optional[str] = None,
        group_id: int = None,
        group_name: str = "",
        owner_id: Optional[str] = None,
    ):
        super().__init__(id)
        self.group_id = group_id
        self.group_name = group_name
        self.owner_id = owner_id

        # Статус и конфигурация
        self.status = MonitoringStatus()
        self.config = MonitoringConfig()

        # Статистика
        self.total_cycles = 0
        self.successful_cycles = 0
        self.failed_cycles = 0
        self.last_cycle_at: Optional[datetime] = None
        self.last_successful_cycle_at: Optional[datetime] = None
        self.last_error_at: Optional[datetime] = None
        self.last_error_message: Optional[str] = None

        # Результаты последнего цикла
        self.last_result: Optional[MonitoringResult] = None

    def start_monitoring(self) -> None:
        """Запустить мониторинг"""
        if not self.status.can_be_started():
            raise ValueError(
                f"Cannot start monitoring in status: {self.status}"
            )

        self.status = MonitoringStatus(self.status.ACTIVE)
        self.update()

    def pause_monitoring(self) -> None:
        """Приостановить мониторинг"""
        if not self.status.can_be_paused():
            raise ValueError(
                f"Cannot pause monitoring in status: {self.status}"
            )

        self.status = MonitoringStatus(self.status.PAUSED)
        self.update()

    def stop_monitoring(self) -> None:
        """Остановить мониторинг"""
        self.status = MonitoringStatus(self.status.STOPPED)
        self.update()

    def record_cycle_result(self, result: MonitoringResult) -> None:
        """Записать результат цикла мониторинга"""
        self.last_result = result
        self.last_cycle_at = result.completed_at or datetime.utcnow()
        self.total_cycles += 1

        if result.has_errors():
            self.failed_cycles += 1
            self.last_error_at = result.completed_at
            self.last_error_message = (
                result.errors[0] if result.errors else None
            )
            # Автоматическая пауза при множественных ошибках
            if self.failed_cycles >= 3 and self.successful_cycles == 0:
                self.status = MonitoringStatus(self.status.ERROR)
        else:
            self.successful_cycles += 1
            self.last_successful_cycle_at = result.completed_at
            # Сброс счетчика ошибок при успешном цикле
            if self.successful_cycles >= 1:
                self.failed_cycles = 0

        self.update()

    def update_config(self, new_config: MonitoringConfig) -> None:
        """Обновить конфигурацию мониторинга"""
        self.config = new_config
        self.update()

    def reset_statistics(self) -> None:
        """Сбросить статистику"""
        self.total_cycles = 0
        self.successful_cycles = 0
        self.failed_cycles = 0
        self.last_cycle_at = None
        self.last_successful_cycle_at = None
        self.last_error_at = None
        self.last_error_message = None
        self.last_result = None
        self.update()

    @property
    def success_rate(self) -> float:
        """Рассчитать процент успешности"""
        if self.total_cycles == 0:
            return 0.0
        return (self.successful_cycles / self.total_cycles) * 100

    @property
    def is_healthy(self) -> bool:
        """Проверить здоровье мониторинга"""
        if self.status.status != MonitoringStatus.ACTIVE:
            return False

        # Если есть недавние ошибки
        if self.last_error_at:
            hours_since_error = (
                datetime.utcnow() - self.last_error_at
            ).total_seconds() / 3600
            if hours_since_error < 1 and self.failed_cycles >= 3:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "owner_id": self.owner_id,
            "status": str(self.status),
            "config": {
                "interval_seconds": self.config.interval_seconds,
                "max_concurrent_groups": self.config.max_concurrent_groups,
                "enable_auto_retry": self.config.enable_auto_retry,
                "max_retries": self.config.max_retries,
                "timeout_seconds": self.config.timeout_seconds,
                "enable_notifications": self.config.enable_notifications,
                "notification_channels": self.config.notification_channels,
            },
            "statistics": {
                "total_cycles": self.total_cycles,
                "successful_cycles": self.successful_cycles,
                "failed_cycles": self.failed_cycles,
                "success_rate": self.success_rate,
                "last_cycle_at": (
                    self.last_cycle_at.isoformat()
                    if self.last_cycle_at
                    else None
                ),
                "last_successful_cycle_at": (
                    self.last_successful_cycle_at.isoformat()
                    if self.last_successful_cycle_at
                    else None
                ),
                "last_error_at": (
                    self.last_error_at.isoformat()
                    if self.last_error_at
                    else None
                ),
                "last_error_message": self.last_error_message,
            },
            "last_result": (
                self.last_result.to_dict() if self.last_result else None
            ),
            "is_healthy": self.is_healthy,
            "timestamps": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            },
        }


class MonitoringStats(ValueObject):
    """Статистика мониторинга системы"""

    def __init__(
        self,
        total_groups: int = 0,
        active_groups: int = 0,
        paused_groups: int = 0,
        error_groups: int = 0,
        total_cycles_today: int = 0,
        successful_cycles_today: int = 0,
        average_processing_time: float = 0.0,
        total_comments_found_today: int = 0,
        total_posts_processed_today: int = 0,
    ):
        self.total_groups = total_groups
        self.active_groups = active_groups
        self.paused_groups = paused_groups
        self.error_groups = error_groups
        self.total_cycles_today = total_cycles_today
        self.successful_cycles_today = successful_cycles_today
        self.average_processing_time = average_processing_time
        self.total_comments_found_today = total_comments_found_today
        self.total_posts_processed_today = total_posts_processed_today

    @property
    def success_rate_today(self) -> float:
        """Процент успешности за сегодня"""
        if self.total_cycles_today == 0:
            return 0.0
        return (self.successful_cycles_today / self.total_cycles_today) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "groups": {
                "total": self.total_groups,
                "active": self.active_groups,
                "paused": self.paused_groups,
                "error": self.error_groups,
            },
            "performance_today": {
                "total_cycles": self.total_cycles_today,
                "successful_cycles": self.successful_cycles_today,
                "success_rate": self.success_rate_today,
                "average_processing_time": self.average_processing_time,
                "total_comments_found": self.total_comments_found_today,
                "total_posts_processed": self.total_posts_processed_today,
            },
        }
