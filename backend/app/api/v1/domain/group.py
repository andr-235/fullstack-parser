"""
Domain сущности для групп (DDD)
"""

from datetime import datetime
from typing import Optional
from .base import Entity, ValueObject


class GroupStatus(ValueObject):
    """Статус группы"""

    def __init__(
        self, is_active: bool = True, is_monitoring_enabled: bool = False
    ):
        self.is_active = is_active
        self.is_monitoring_enabled = is_monitoring_enabled


class GroupInfo(ValueObject):
    """Информация о группе"""

    def __init__(
        self,
        name: str,
        screen_name: str,
        description: Optional[str] = None,
        members_count: Optional[int] = None,
    ):
        self.name = name
        self.screen_name = screen_name
        self.description = description
        self.members_count = members_count


class MonitoringConfig(ValueObject):
    """Конфигурация мониторинга группы"""

    def __init__(
        self,
        interval_minutes: int = 60,
        priority: int = 5,
        max_posts_to_check: int = 100,
    ):
        self.interval_minutes = interval_minutes
        self.priority = priority
        self.max_posts_to_check = max_posts_to_check


class VKGroup(Entity):
    """Доменная сущность группы VK"""

    def __init__(
        self,
        id: Optional[int] = None,
        vk_id: Optional[int] = None,
        group_info: GroupInfo = None,
        status: GroupStatus = None,
        monitoring_config: MonitoringConfig = None,
    ):
        super().__init__(id)
        self.vk_id = vk_id
        self.group_info = group_info
        self.status = status or GroupStatus()
        self.monitoring_config = monitoring_config or MonitoringConfig()
        self.last_monitoring_at: Optional[datetime] = None
        self.next_monitoring_at: Optional[datetime] = None
        self.monitoring_runs_count = 0
        self.last_error: Optional[str] = None

    def activate(self) -> None:
        """Активировать группу"""
        self.status = GroupStatus(
            is_active=True,
            is_monitoring_enabled=self.status.is_monitoring_enabled,
        )
        self.update()

    def deactivate(self) -> None:
        """Деактивировать группу"""
        self.status = GroupStatus(is_active=False, is_monitoring_enabled=False)
        self.update()

    def enable_monitoring(self) -> None:
        """Включить мониторинг группы"""
        if not self.status.is_active:
            raise ValueError(
                "Нельзя включить мониторинг для неактивной группы"
            )

        self.status = GroupStatus(
            is_active=self.status.is_active, is_monitoring_enabled=True
        )
        self.update()

    def disable_monitoring(self) -> None:
        """Отключить мониторинг группы"""
        self.status = GroupStatus(
            is_active=self.status.is_active, is_monitoring_enabled=False
        )
        self.update()

    def update_monitoring_config(self, config: MonitoringConfig) -> None:
        """Обновить конфигурацию мониторинга"""
        self.monitoring_config = config
        self.update()

    def record_monitoring_success(self) -> None:
        """Записать успешное выполнение мониторинга"""
        self.last_monitoring_at = datetime.utcnow()
        self.monitoring_runs_count += 1
        self.last_error = None
        self.update()

    def record_monitoring_error(self, error: str) -> None:
        """Записать ошибку мониторинга"""
        self.last_monitoring_at = datetime.utcnow()
        self.last_error = error
        self.update()

    def calculate_next_monitoring_time(self) -> datetime:
        """Рассчитать время следующего мониторинга"""
        if not self.last_monitoring_at:
            return datetime.utcnow()

        return self.last_monitoring_at + datetime.timedelta(
            minutes=self.monitoring_config.interval_minutes
        )

    @property
    def is_active(self) -> bool:
        return self.status.is_active

    @property
    def is_monitoring_enabled(self) -> bool:
        return self.status.is_monitoring_enabled

    @property
    def name(self) -> str:
        return self.group_info.name if self.group_info else ""

    @property
    def screen_name(self) -> str:
        return self.group_info.screen_name if self.group_info else ""
