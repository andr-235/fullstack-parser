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

    # =============== МИГРАЦИЯ GroupValidator В DDD ===============

    async def validate_screen_name_ddd(
        self, screen_name: str
    ) -> Dict[str, Any]:
        """
        Проверить существование группы по screen_name (мигрировано из GroupValidator)

        Args:
            screen_name: Короткое имя группы

        Returns:
            Результат валидации
        """
        try:
            # Используем VK API сервис для проверки
            group_data = await self.vk_api_service.get_group_info(screen_name)
            exists = "error" not in group_data

            return {
                "valid": exists,
                "screen_name": screen_name,
                "group_data": group_data if exists else None,
                "validated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating screen_name {screen_name}: {e}")
            return {
                "valid": False,
                "screen_name": screen_name,
                "error": str(e),
                "validated_at": datetime.utcnow().isoformat(),
            }

    async def validate_vk_id_ddd(self, vk_id: int) -> Dict[str, Any]:
        """
        Проверить существование группы по VK ID (мигрировано из GroupValidator)

        Args:
            vk_id: VK ID группы

        Returns:
            Результат валидации
        """
        try:
            # Используем VK API сервис для проверки
            group_data = await self.vk_api_service.get_group_info(str(vk_id))
            exists = "error" not in group_data

            return {
                "valid": exists,
                "vk_id": vk_id,
                "group_data": group_data if exists else None,
                "validated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating VK ID {vk_id}: {e}")
            return {
                "valid": False,
                "vk_id": vk_id,
                "error": str(e),
                "validated_at": datetime.utcnow().isoformat(),
            }

    async def get_group_data_from_vk_ddd(
        self, identifier: str
    ) -> Dict[str, Any]:
        """
        Получить данные группы из VK API (мигрировано из GroupValidator)

        Args:
            identifier: screen_name или VK ID группы

        Returns:
            Данные группы из VK API
        """
        try:
            group_data = await self.vk_api_service.get_group_info(identifier)

            if "error" in group_data:
                return {
                    "found": False,
                    "identifier": identifier,
                    "error": group_data["error"],
                    "retrieved_at": datetime.utcnow().isoformat(),
                }

            return {
                "found": True,
                "identifier": identifier,
                "group_data": group_data,
                "retrieved_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting group data from VK: {e}")
            return {
                "found": False,
                "identifier": identifier,
                "error": str(e),
                "retrieved_at": datetime.utcnow().isoformat(),
            }

    async def extract_screen_name_ddd(self, identifier: str) -> Dict[str, Any]:
        """
        Извлечь screen_name из идентификатора (мигрировано из GroupValidator)

        Args:
            identifier: Идентификатор группы

        Returns:
            Результат извлечения screen_name
        """
        try:
            # Если это числовой ID
            if identifier.isdigit() or (
                identifier.startswith("-") and identifier[1:].isdigit()
            ):
                # Получаем данные группы для извлечения screen_name
                group_data = await self.vk_api_service.get_group_info(
                    identifier
                )

                if "error" not in group_data:
                    screen_name = group_data.get("screen_name")
                    return {
                        "extracted": True,
                        "original_identifier": identifier,
                        "screen_name": screen_name,
                        "type": "vk_id",
                    }

            # Если это уже screen_name
            else:
                return {
                    "extracted": True,
                    "original_identifier": identifier,
                    "screen_name": identifier,
                    "type": "screen_name",
                }

            return {
                "extracted": False,
                "original_identifier": identifier,
                "error": "Could not extract screen_name",
            }

        except Exception as e:
            logger.error(f"Error extracting screen_name: {e}")
            return {
                "extracted": False,
                "original_identifier": identifier,
                "error": str(e),
            }

    async def validate_group_access_ddd(self, group_id: int) -> Dict[str, Any]:
        """
        Проверить доступ к группе (мигрировано из GroupValidator)

        Args:
            group_id: ID группы VK

        Returns:
            Результат проверки доступа
        """
        try:
            # Проверяем существование группы
            group_data = await self.vk_api_service.get_group_info(
                str(group_id)
            )

            if "error" in group_data:
                return {
                    "has_access": False,
                    "group_id": group_id,
                    "error": group_data["error"],
                    "checked_at": datetime.utcnow().isoformat(),
                }

            # Проверяем, можем ли мы получить посты (как индикатор доступа)
            try:
                posts_data = await self.vk_api_service.get_group_posts(
                    group_id=group_id, count=1, offset=0
                )

                has_access = "error" not in posts_data

                return {
                    "has_access": has_access,
                    "group_id": group_id,
                    "group_name": group_data.get("name"),
                    "can_read_posts": has_access,
                    "checked_at": datetime.utcnow().isoformat(),
                }

            except Exception:
                return {
                    "has_access": False,
                    "group_id": group_id,
                    "group_name": group_data.get("name"),
                    "can_read_posts": False,
                    "error": "Cannot access group posts",
                    "checked_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error validating group access: {e}")
            return {
                "has_access": False,
                "group_id": group_id,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat(),
            }

    async def refresh_group_data_ddd(self, group_id: int) -> Dict[str, Any]:
        """
        Обновить данные группы из VK API (мигрировано из GroupValidator)

        Args:
            group_id: ID группы

        Returns:
            Результат обновления данных
        """
        try:
            # Находим группу в БД
            group = await self.group_repository.find_by_id(group_id)
            if not group:
                return {
                    "refreshed": False,
                    "reason": "Group not found in database",
                    "group_id": group_id,
                }

            # Получаем актуальные данные из VK
            vk_data = await self.vk_api_service.get_group_info(
                str(group.content.vk_id)
            )

            if "error" in vk_data:
                return {
                    "refreshed": False,
                    "reason": "Could not get data from VK API",
                    "group_id": group_id,
                    "vk_error": vk_data["error"],
                }

            # Обновляем данные группы
            group.content.name = vk_data.get("name", group.content.name)
            group.content.description = vk_data.get("description", "")
            group.content.members_count = vk_data.get("members_count", 0)
            group.content.photo_url = vk_data.get("photo_200", "")
            group.content.is_closed = vk_data.get("is_closed", False)
            group.updated_at = datetime.utcnow()

            # Сохраняем изменения
            await self.group_repository.save(group)

            return {
                "refreshed": True,
                "group_id": group_id,
                "group_name": group.content.name,
                "updated_fields": [
                    "name",
                    "description",
                    "members_count",
                    "photo_url",
                    "is_closed",
                ],
                "refreshed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error refreshing group data: {e}")
            return {
                "refreshed": False,
                "group_id": group_id,
                "error": str(e),
            }

    async def compare_with_vk_data_ddd(
        self, group_id: int, vk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сравнить данные группы с данными из VK API (мигрировано из GroupValidator)

        Args:
            group_id: ID группы
            vk_data: Данные из VK API

        Returns:
            Результат сравнения
        """
        try:
            # Находим группу в БД
            group = await self.group_repository.find_by_id(group_id)
            if not group:
                return {
                    "compared": False,
                    "reason": "Group not found in database",
                    "group_id": group_id,
                }

            # Сравниваем поля
            differences = {}

            if group.content.name != vk_data.get("name"):
                differences["name"] = {
                    "database": group.content.name,
                    "vk": vk_data.get("name"),
                }

            if group.content.description != vk_data.get("description", ""):
                differences["description"] = {
                    "database": group.content.description,
                    "vk": vk_data.get("description", ""),
                }

            if group.content.members_count != vk_data.get("members_count", 0):
                differences["members_count"] = {
                    "database": group.content.members_count,
                    "vk": vk_data.get("members_count", 0),
                }

            if group.content.is_closed != vk_data.get("is_closed", False):
                differences["is_closed"] = {
                    "database": group.content.is_closed,
                    "vk": vk_data.get("is_closed", False),
                }

            return {
                "compared": True,
                "group_id": group_id,
                "has_differences": len(differences) > 0,
                "differences": differences,
                "differences_count": len(differences),
                "compared_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error comparing with VK data: {e}")
            return {
                "compared": False,
                "group_id": group_id,
                "error": str(e),
            }

    async def validate_multiple_groups_ddd(
        self, group_identifiers: List[str]
    ) -> Dict[str, Any]:
        """
        Проверить несколько групп одновременно (мигрировано из GroupValidator)

        Args:
            group_identifiers: Список идентификаторов групп

        Returns:
            Результаты валидации всех групп
        """
        try:
            results = []
            valid_count = 0
            invalid_count = 0

            for identifier in group_identifiers:
                try:
                    # Определяем тип идентификатора
                    if identifier.isdigit() or (
                        identifier.startswith("-") and identifier[1:].isdigit()
                    ):
                        result = await self.validate_vk_id_ddd(int(identifier))
                    else:
                        result = await self.validate_screen_name_ddd(
                            identifier
                        )

                    results.append(
                        {
                            "identifier": identifier,
                            "valid": result["valid"],
                            "group_data": result.get("group_data"),
                            "error": result.get("error"),
                        }
                    )

                    if result["valid"]:
                        valid_count += 1
                    else:
                        invalid_count += 1

                except Exception as e:
                    results.append(
                        {
                            "identifier": identifier,
                            "valid": False,
                            "error": str(e),
                        }
                    )
                    invalid_count += 1

            return {
                "validated": True,
                "total_groups": len(group_identifiers),
                "valid_groups": valid_count,
                "invalid_groups": invalid_count,
                "results": results,
                "validated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating multiple groups: {e}")
            return {
                "validated": False,
                "error": str(e),
                "total_groups": len(group_identifiers),
                "validated_at": datetime.utcnow().isoformat(),
            }

    async def refresh_group_from_vk_ddd(
        self, identifier: str, create_if_not_exists: bool = False
    ) -> Dict[str, Any]:
        """
        Обновить или создать группу из VK API (мигрировано из GroupValidator)

        Args:
            identifier: Идентификатор группы
            create_if_not_exists: Создать если не существует

        Returns:
            Результат операции
        """
        try:
            # Получаем данные из VK
            vk_result = await self.get_group_data_from_vk_ddd(identifier)

            if not vk_result["found"]:
                return {
                    "refreshed": False,
                    "identifier": identifier,
                    "reason": "Group not found in VK",
                    "vk_error": vk_result.get("error"),
                }

            vk_data = vk_result["group_data"]

            # Ищем существующую группу
            existing_group = None
            if vk_data.get("id"):
                existing_group = await self.group_repository.find_by_vk_id(
                    vk_data["id"]
                )
            elif vk_data.get("screen_name"):
                # Ищем по screen_name среди существующих групп
                all_groups = await self.group_repository.find_all()
                for group in all_groups:
                    if group.content.screen_name == vk_data["screen_name"]:
                        existing_group = group
                        break

            if existing_group:
                # Обновляем существующую группу
                existing_group.content.name = vk_data.get(
                    "name", existing_group.content.name
                )
                existing_group.content.description = vk_data.get(
                    "description", ""
                )
                existing_group.content.members_count = vk_data.get(
                    "members_count", 0
                )
                existing_group.content.photo_url = vk_data.get("photo_200", "")
                existing_group.content.is_closed = vk_data.get(
                    "is_closed", False
                )
                existing_group.updated_at = datetime.utcnow()

                await self.group_repository.save(existing_group)

                return {
                    "refreshed": True,
                    "action": "updated",
                    "group_id": existing_group.id,
                    "group_name": existing_group.content.name,
                    "identifier": identifier,
                }

            elif create_if_not_exists:
                # Создаем новую группу
                from ..domain.group import Group, GroupContent

                content = GroupContent(
                    vk_id=vk_data.get("id"),
                    screen_name=vk_data.get("screen_name", ""),
                    name=vk_data.get("name", ""),
                    description=vk_data.get("description", ""),
                    members_count=vk_data.get("members_count", 0),
                    photo_url=vk_data.get("photo_200", ""),
                    is_closed=vk_data.get("is_closed", False),
                )

                new_group = Group(
                    id=None,
                    content=content,
                )

                await self.group_repository.save(new_group)

                return {
                    "refreshed": True,
                    "action": "created",
                    "group_id": new_group.id,
                    "group_name": new_group.content.name,
                    "identifier": identifier,
                }

            else:
                return {
                    "refreshed": False,
                    "identifier": identifier,
                    "reason": "Group not found in database and create_if_not_exists is False",
                }

        except Exception as e:
            logger.error(f"Error refreshing group from VK: {e}")
            return {
                "refreshed": False,
                "identifier": identifier,
                "error": str(e),
            }

    # =============== МИГРАЦИЯ GroupStatsService В DDD ===============

    async def get_group_stats_ddd(self, group_id: int) -> Dict[str, Any]:
        """
        Получить статистику по группе (мигрировано из GroupStatsService)

        Args:
            group_id: ID группы в базе данных

        Returns:
            Статистика группы
        """
        try:
            from app.models.vk_group import VKGroup
            from app.models.comment_keyword_match import CommentKeywordMatch
            from app.models.keyword import Keyword
            from app.models.vk_comment import VKComment
            from app.models.vk_post import VKPost

            # Находим группу
            group = await self.db.get(VKGroup, group_id)
            if not group:
                return {
                    "error": True,
                    "message": f"Группа с ID {group_id} не найдена",
                    "group_id": group_id,
                }

            # Подсчитываем комментарии с ключевыми словами
            comments_with_keywords_query = (
                select(func.count(VKComment.id))
                .select_from(VKComment)
                .join(VKPost, VKComment.post_id == VKPost.id)
                .where(VKPost.group_id == group_id)
                .where(VKComment.matched_keywords_count > 0)
            )
            comments_with_keywords = (
                await self.db.scalar(comments_with_keywords_query) or 0
            )

            # Получаем топ ключевых слов
            top_keywords = await self._get_top_keywords_ddd(group_id, limit=10)

            return {
                "group_id": group.vk_id,
                "group_name": group.name,
                "total_posts": group.total_posts_parsed or 0,
                "total_comments": group.total_comments_found or 0,
                "comments_with_keywords": comments_with_keywords,
                "last_activity": (
                    group.last_parsed_at.isoformat()
                    if group.last_parsed_at
                    else None
                ),
                "top_keywords": top_keywords,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error getting group stats for group {group_id}: {e}"
            )
            return {
                "error": True,
                "message": str(e),
                "group_id": group_id,
            }

    async def get_groups_overview_ddd(self) -> Dict[str, Any]:
        """
        Получить обзор всех групп (мигрировано из GroupStatsService)

        Returns:
            Обзор статистики всех групп
        """
        try:
            from app.models.vk_group import VKGroup
            from app.models.vk_comment import VKComment
            from app.models.vk_post import VKPost

            # Получаем общее количество групп
            total_groups = await self.db.scalar(select(func.count(VKGroup.id)))

            # Получаем активные группы
            active_groups = await self.db.scalar(
                select(func.count(VKGroup.id)).where(VKGroup.is_active == True)
            )

            # Получаем общее количество постов
            total_posts = (
                await self.db.scalar(
                    select(func.sum(VKGroup.total_posts_parsed)).where(
                        VKGroup.total_posts_parsed.isnot(None)
                    )
                )
                or 0
            )

            # Получаем общее количество комментариев
            total_comments = (
                await self.db.scalar(
                    select(func.sum(VKGroup.total_comments_found)).where(
                        VKGroup.total_comments_found.isnot(None)
                    )
                )
                or 0
            )

            # Получаем группы с наибольшим количеством комментариев
            top_groups_query = (
                select(VKGroup)
                .order_by(VKGroup.total_comments_found.desc().nulls_last())
                .limit(5)
            )
            top_groups_result = await self.db.execute(top_groups_query)
            top_groups = top_groups_result.scalars().all()

            top_groups_list = []
            for group in top_groups:
                top_groups_list.append(
                    {
                        "id": group.id,
                        "vk_id": group.vk_id,
                        "name": group.name,
                        "total_comments": group.total_comments_found or 0,
                        "total_posts": group.total_posts_parsed or 0,
                    }
                )

            return {
                "total_groups": total_groups,
                "active_groups": active_groups,
                "inactive_groups": total_groups - active_groups,
                "total_posts": total_posts,
                "total_comments": total_comments,
                "average_comments_per_group": total_comments
                / max(total_groups, 1),
                "top_groups_by_comments": top_groups_list,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting groups overview: {e}")
            return {
                "error": True,
                "message": str(e),
            }

    async def get_group_activity_trends_ddd(
        self, group_id: int, days: int = 7
    ) -> Dict[str, Any]:
        """
        Получить тренды активности группы (мигрировано из GroupStatsService)

        Args:
            group_id: ID группы
            days: Количество дней для анализа

        Returns:
            Тренды активности группы
        """
        try:
            from app.models.vk_group import VKGroup
            from app.models.vk_comment import VKComment
            from app.models.vk_post import VKPost
            from datetime import timedelta

            # Находим группу
            group = await self.db.get(VKGroup, group_id)
            if not group:
                return {
                    "error": True,
                    "message": f"Группа с ID {group_id} не найдена",
                    "group_id": group_id,
                }

            # Вычисляем дату начала периода
            start_date = datetime.utcnow() - timedelta(days=days)

            # Получаем статистику по дням
            daily_stats = []
            for i in range(days):
                day_start = start_date + timedelta(days=i)
                day_end = day_start + timedelta(days=1)

                # Подсчитываем посты за день
                posts_query = (
                    select(func.count(VKPost.id))
                    .where(VKPost.group_id == group_id)
                    .where(VKPost.published_at >= day_start)
                    .where(VKPost.published_at < day_end)
                )
                posts_count = await self.db.scalar(posts_query) or 0

                # Подсчитываем комментарии за день
                comments_query = (
                    select(func.count(VKComment.id))
                    .select_from(VKComment)
                    .join(VKPost, VKComment.post_id == VKPost.id)
                    .where(VKPost.group_id == group_id)
                    .where(VKComment.published_at >= day_start)
                    .where(VKComment.published_at < day_end)
                )
                comments_count = await self.db.scalar(comments_query) or 0

                daily_stats.append(
                    {
                        "date": day_start.strftime("%Y-%m-%d"),
                        "posts": posts_count,
                        "comments": comments_count,
                        "comments_per_post": comments_count
                        / max(posts_count, 1),
                    }
                )

            # Вычисляем тренды
            total_posts = sum(day["posts"] for day in daily_stats)
            total_comments = sum(day["comments"] for day in daily_stats)
            avg_comments_per_post = total_comments / max(total_posts, 1)

            # Определяем тренд активности
            recent_posts = sum(day["posts"] for day in daily_stats[-3:])
            older_posts = sum(day["posts"] for day in daily_stats[:-3])
            activity_trend = (
                "increasing"
                if recent_posts > older_posts
                else "decreasing" if recent_posts < older_posts else "stable"
            )

            return {
                "group_id": group_id,
                "group_name": group.name,
                "analysis_period_days": days,
                "daily_stats": daily_stats,
                "summary": {
                    "total_posts": total_posts,
                    "total_comments": total_comments,
                    "avg_comments_per_post": avg_comments_per_post,
                    "activity_trend": activity_trend,
                },
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error getting group activity trends for group {group_id}: {e}"
            )
            return {
                "error": True,
                "message": str(e),
                "group_id": group_id,
            }

    # =============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ GroupStatsService ===============

    async def _get_top_keywords_ddd(
        self, group_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получить топ ключевых слов для группы
        """
        try:
            from app.models.comment_keyword_match import CommentKeywordMatch
            from app.models.keyword import Keyword

            # Получаем топ ключевых слов по количеству совпадений
            query = (
                select(
                    Keyword.word,
                    Keyword.category,
                    func.count(CommentKeywordMatch.id).label("matches_count"),
                )
                .select_from(CommentKeywordMatch)
                .join(Keyword, CommentKeywordMatch.keyword_id == Keyword.id)
                .where(CommentKeywordMatch.group_id == group_id)
                .group_by(Keyword.word, Keyword.category)
                .order_by(func.count(CommentKeywordMatch.id).desc())
                .limit(limit)
            )

            result = await self.db.execute(query)
            rows = result.all()

            top_keywords = []
            for row in rows:
                top_keywords.append(
                    {
                        "word": row.word,
                        "category": row.category,
                        "matches_count": row.matches_count,
                    }
                )

            return top_keywords

        except Exception as e:
            logger.error(
                f"Error getting top keywords for group {group_id}: {e}"
            )
            return []
