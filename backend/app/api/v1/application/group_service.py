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

    # Дополнительные методы из GroupManager для полной миграции

    async def get_group_by_screen_name(
        self, screen_name: str
    ) -> Optional[VKGroup]:
        """
        Получить группу по screen_name (мигрировано из GroupManager)

        Args:
            screen_name: Короткое имя группы

        Returns:
            Группа или None
        """
        groups = await self.group_repository.find_all()
        for group in groups:
            if group.screen_name == screen_name:
                return group
        return None

    async def get_group_by_vk_id(self, vk_id: int) -> Optional[VKGroup]:
        """
        Получить группу по VK ID (мигрировано из GroupManager)

        Args:
            vk_id: VK ID группы

        Returns:
            Группа или None
        """
        groups = await self.group_repository.find_all()
        for group in groups:
            if group.vk_id == vk_id:
                return group
        return None

    async def get_groups_count(
        self, active_only: bool = True, search: Optional[str] = None
    ) -> int:
        """
        Получить количество групп с фильтрами (мигрировано из GroupManager)

        Args:
            active_only: Только активные группы
            search: Поисковый запрос

        Returns:
            Количество групп
        """
        groups = await self.get_groups(
            active_only=active_only, search=search, limit=10000, offset=0
        )
        return len(groups)

    async def get_groups_paginated(
        self,
        active_only: bool = True,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[VKGroup]:
        """
        Получить группы с пагинацией (мигрировано из GroupManager)

        Args:
            active_only: Только активные группы
            search: Поисковый запрос
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Список групп
        """
        return await self.get_groups(
            active_only=active_only, search=search, limit=limit, offset=offset
        )

    async def search_groups(
        self,
        query: str,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> List[VKGroup]:
        """
        Поиск групп по имени или screen_name (мигрировано из GroupManager)

        Args:
            query: Поисковый запрос
            active_only: Только активные группы
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Список найденных групп
        """
        return await self.get_groups(
            active_only=active_only, search=query, limit=limit, offset=offset
        )

    async def toggle_group_status(self, group_id: int) -> Optional[VKGroup]:
        """
        Переключить статус активности группы (мигрировано из GroupManager)

        Args:
            group_id: ID группы

        Returns:
            Обновленная группа или None
        """
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return None

        if group.is_active:
            await self.deactivate_group(group_id)
        else:
            await self.activate_group(group_id)

        return await self.group_repository.find_by_id(group_id)

    # =============== МИГРАЦИЯ GroupManager В DDD ===============

    async def get_group_by_id_detailed(
        self, group_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получить группу по ID с детальной информацией (мигрировано из GroupManager)

        Args:
            group_id: ID группы

        Returns:
            Детальная информация о группе или None
        """
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return None

        return {
            "id": group.id,
            "vk_id": group.vk_id,
            "screen_name": group.screen_name,
            "name": group.name,
            "description": group.description,
            "is_active": group.is_active,
            "member_count": group.member_count,
            "photo_url": group.photo_url,
            "created_at": group.created_at.isoformat(),
            "updated_at": group.updated_at.isoformat(),
            "monitoring_status": group.get_monitoring_status(),
            "is_ready": group.is_ready_for_monitoring(),
            "monitoring_interval": group.monitoring_interval_minutes,
            "monitoring_priority": group.monitoring_priority,
            "last_parsed_at": (
                group.last_parsed_at.isoformat()
                if group.last_parsed_at
                else None
            ),
            "next_monitoring_at": group.calculate_next_monitoring_time().isoformat(),
            "monitoring_runs_count": group.monitoring_runs_count,
            "last_monitoring_success": (
                group.last_monitoring_success.isoformat()
                if group.last_monitoring_success
                else None
            ),
            "last_monitoring_error": group.last_monitoring_error,
        }

    async def get_groups_count_with_filters(
        self, active_only: bool = True, search: Optional[str] = None
    ) -> int:
        """
        Получить количество групп с фильтрами (мигрировано из GroupManager)

        Args:
            active_only: Только активные группы
            search: Поисковый запрос

        Returns:
            Количество групп
        """
        # Получаем все группы
        all_groups = await self.group_repository.find_all()

        # Применяем фильтры
        if active_only:
            all_groups = [g for g in all_groups if g.is_active]

        if search:
            search_lower = search.lower()
            all_groups = [
                g
                for g in all_groups
                if search_lower in (g.name or "").lower()
                or search_lower in (g.screen_name or "").lower()
            ]

        return len(all_groups)

    async def create_group_detailed(
        self, group_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать новую группу с валидацией (мигрировано из GroupManager)

        Args:
            group_data: Данные группы

        Returns:
            Созданная группа
        """
        from ..domain.group import Group
        from datetime import datetime

        # Проверяем существование группы с таким же screen_name
        existing = await self.get_group_by_screen_name(
            group_data.get("screen_name", "")
        )
        if existing:
            raise ValueError(
                f"Group with screen_name '{group_data.get('screen_name')}' already exists"
            )

        # Создаем доменную сущность
        group = Group(
            id=None,  # Будет присвоен при сохранении
            vk_id=group_data.get("vk_id"),
            screen_name=group_data.get("screen_name", ""),
            name=group_data.get("name", ""),
            description=group_data.get("description"),
            is_active=group_data.get("is_active", True),
            member_count=group_data.get("member_count", 0),
            photo_url=group_data.get("photo_url"),
            monitoring_interval_minutes=group_data.get(
                "monitoring_interval_minutes", 60
            ),
            monitoring_priority=group_data.get("monitoring_priority", 1),
        )

        # Валидируем бизнес-правила
        group.validate_business_rules()

        # Сохраняем через репозиторий
        await self.group_repository.save(group)

        return await self.get_group_by_id_detailed(group.id)

    async def update_group_detailed(
        self, group_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить группу с валидацией (мигрировано из GroupManager)

        Args:
            group_id: ID группы
            update_data: Данные для обновления

        Returns:
            Обновленная группа или None
        """
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return None

        # Обновляем поля
        for field, value in update_data.items():
            if hasattr(group, field):
                setattr(group, field, value)

        # Валидируем бизнес-правила после обновления
        group.validate_business_rules()

        # Сохраняем изменения
        await self.group_repository.save(group)

        return await self.get_group_by_id_detailed(group.id)

    async def delete_group_detailed(self, group_id: int) -> Dict[str, Any]:
        """
        Удалить группу с проверками (мигрировано из GroupManager)

        Args:
            group_id: ID группы

        Returns:
            Результат операции
        """
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return {"deleted": False, "reason": "Group not found"}

        group_name = group.screen_name

        # Удаляем через репозиторий
        await self.group_repository.delete(group_id)

        return {
            "deleted": True,
            "group_id": group_id,
            "group_name": group_name,
            "message": f"Group {group_name} deleted successfully",
        }

    async def toggle_group_status_detailed(
        self, group_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Переключить статус активности группы с деталями (мигрировано из GroupManager)

        Args:
            group_id: ID группы

        Returns:
            Обновленная группа или None
        """
        group = await self.group_repository.find_by_id(group_id)
        if not group:
            return None

        # Переключаем статус активности
        if group.is_active:
            group.deactivate()
        else:
            group.activate()

        # Сохраняем изменения
        await self.group_repository.save(group)

        return await self.get_group_by_id_detailed(group.id)

    async def search_groups_detailed(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        active_only: bool = True,
    ) -> Dict[str, Any]:
        """
        Поиск групп по имени или screen_name с деталями (мигрировано из GroupManager)

        Args:
            query: Поисковый запрос
            limit: Максимальное количество
            offset: Смещение
            active_only: Только активные группы

        Returns:
            Детальные результаты поиска
        """
        return await self.get_groups_paginated(
            active_only=active_only, search=query, limit=limit, offset=offset
        )

    # =============== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ GroupManager ===============

    async def get_group_by_vk_id(self, vk_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить группу по VK ID (мигрировано из GroupManager)

        Args:
            vk_id: VK ID группы

        Returns:
            Информация о группе или None
        """
        # Получаем все группы и ищем по vk_id
        all_groups = await self.group_repository.find_all()
        group = next((g for g in all_groups if g.vk_id == vk_id), None)

        if not group:
            return None

        return await self.get_group_by_id_detailed(group.id)

    async def get_groups_paginated_detailed(
        self,
        active_only: bool = True,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Получить группы с пагинацией (мигрировано из GroupManager)

        Args:
            active_only: Только активные группы
            search: Поисковый запрос
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Список групп
        """
        # Получаем все группы
        all_groups = await self.group_repository.find_all()

        # Применяем фильтры
        if active_only:
            all_groups = [g for g in all_groups if g.is_active]

        if search:
            search_lower = search.lower()
            all_groups = [
                g
                for g in all_groups
                if search_lower in (g.name or "").lower()
                or search_lower in (g.screen_name or "").lower()
            ]

        # Пагинация
        paginated_groups = all_groups[offset : offset + limit]

        # Преобразуем в response формат
        groups_response = []
        for group in paginated_groups:
            groups_response.append(
                {
                    "id": group.id,
                    "vk_id": group.vk_id,
                    "screen_name": group.screen_name,
                    "name": group.name,
                    "is_active": group.is_active,
                    "member_count": group.member_count,
                    "created_at": group.created_at.isoformat(),
                }
            )

        return groups_response
