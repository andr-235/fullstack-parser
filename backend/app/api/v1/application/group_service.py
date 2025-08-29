"""
Application Service для групп (DDD)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..domain.group import VKGroup, GroupInfo, GroupStatus, MonitoringConfig
from .base import ApplicationService


class GroupApplicationService(ApplicationService):
    """Application Service для работы с группами"""

    def __init__(self, group_repository):
        self.group_repository = group_repository

    async def get_group_by_id(self, group_id: int) -> Optional[VKGroup]:
        """Получить группу по ID"""
        return await self.group_repository.find_by_id(group_id)

    async def get_groups(
        self,
        active_only: bool = True,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[VKGroup]:
        """Получить список групп с фильтрами"""
        groups = await self.group_repository.find_all()

        # Фильтрация по активности
        if active_only:
            groups = [g for g in groups if g.is_active]

        # Фильтрация по поисковому запросу
        if search:
            search_lower = search.lower()
            groups = [
                g
                for g in groups
                if search_lower in g.name.lower()
                or search_lower in g.screen_name.lower()
            ]

        return groups[offset : offset + limit]

    async def create_group(
        self,
        vk_id: int,
        name: str,
        screen_name: str,
        description: Optional[str] = None,
    ) -> VKGroup:
        """Создать новую группу"""
        group_info = GroupInfo(
            name=name, screen_name=screen_name, description=description
        )

        group = VKGroup(vk_id=vk_id, group_info=group_info)

        await self.group_repository.save(group)
        return group

    async def update_group_info(
        self,
        group_id: int,
        name: Optional[str] = None,
        screen_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Обновить информацию о группе"""
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return False

        if name or screen_name or description:
            updated_info = GroupInfo(
                name=name or group.name,
                screen_name=screen_name or group.screen_name,
                description=description or group.group_info.description,
            )
            group.group_info = updated_info
            group.update()
            await self.group_repository.save(group)

        return True

    async def activate_group(self, group_id: int) -> bool:
        """Активировать группу"""
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return False

        group.activate()
        await self.group_repository.save(group)
        return True

    async def deactivate_group(self, group_id: int) -> bool:
        """Деактивировать группу"""
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return False

        group.deactivate()
        await self.group_repository.save(group)
        return True

    async def enable_monitoring(
        self, group_id: int, config: MonitoringConfig
    ) -> bool:
        """Включить мониторинг группы"""
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return False

        group.update_monitoring_config(config)
        group.enable_monitoring()
        group.next_monitoring_at = group.calculate_next_monitoring_time()

        await self.group_repository.save(group)
        return True

    async def disable_monitoring(self, group_id: int) -> bool:
        """Отключить мониторинг группы"""
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return False

        group.disable_monitoring()
        group.next_monitoring_at = None

        await self.group_repository.save(group)
        return True

    async def record_monitoring_success(self, group_id: int) -> bool:
        """Записать успешное выполнение мониторинга"""
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return False

        group.record_monitoring_success()
        group.next_monitoring_at = group.calculate_next_monitoring_time()

        await self.group_repository.save(group)
        return True

    async def record_monitoring_error(self, group_id: int, error: str) -> bool:
        """Записать ошибку мониторинга"""
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return False

        group.record_monitoring_error(error)
        group.next_monitoring_at = group.calculate_next_monitoring_time()

        await self.group_repository.save(group)
        return True

    async def get_groups_statistics(self) -> Dict[str, Any]:
        """Получить статистику по группам"""
        groups = await self.group_repository.find_all()

        total_groups = len(groups)
        active_groups = len([g for g in groups if g.is_active])
        monitoring_enabled = len(
            [g for g in groups if g.is_monitoring_enabled]
        )
        inactive_groups = total_groups - active_groups

        return {
            "total_groups": total_groups,
            "active_groups": active_groups,
            "inactive_groups": inactive_groups,
            "monitoring_enabled": monitoring_enabled,
            "monitoring_disabled": total_groups - monitoring_enabled,
        }

    async def get_groups_for_monitoring(self) -> List[VKGroup]:
        """Получить группы, готовые к мониторингу"""
        groups = await self.group_repository.find_all()

        now = datetime.utcnow()
        ready_groups = []

        for group in groups:
            if (
                group.is_active
                and group.is_monitoring_enabled
                and (
                    not group.next_monitoring_at
                    or group.next_monitoring_at <= now
                )
            ):
                ready_groups.append(group)

        # Сортировка по приоритету
        ready_groups.sort(
            key=lambda g: g.monitoring_config.priority, reverse=True
        )

        return ready_groups
