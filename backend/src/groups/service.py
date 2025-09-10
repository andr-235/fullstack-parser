"""
Сервис для работы с группами VK

Содержит бизнес-логику для операций с группами VK
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import GroupRepository
from ..exceptions import GroupNotFoundError, ValidationError
from ..infrastructure import cache_service
from ..infrastructure.logging import get_loguru_logger


class GroupService:
    """
    Сервис для работы с группами VK

    Реализует бизнес-логику для операций CRUD с группами VK
    """

    def __init__(self, repository: GroupRepository):
        self.repository = repository
        self.logger = get_loguru_logger("groups")

    async def get_group(self, group_id: int) -> Dict[str, Any]:
        """Получить группу по ID"""
        group = await self.repository.get_by_id(group_id)
        if not group:
            raise GroupNotFoundError(group_id)

        return {
            "id": group.id,
            "vk_id": group.vk_id,
            "screen_name": group.screen_name,
            "name": group.name,
            "description": group.description,
            "is_active": group.is_active,
            "max_posts_to_check": group.max_posts_to_check,
            "members_count": group.members_count,
            "photo_url": group.photo_url,
            "is_closed": group.is_closed,
            "total_posts_parsed": group.total_posts_parsed,
            "total_comments_found": group.total_comments_found,
            "last_parsed_at": group.last_parsed_at,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
        }

    async def get_groups(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Получить список групп с фильтрацией"""
        groups = await self.repository.get_all(
            is_active=is_active, search=search, limit=limit, offset=offset
        )

        return [
            {
                "id": group.id,
                "vk_id": group.vk_id,
                "screen_name": group.screen_name,
                "name": group.name,
                "description": group.description,
                "is_active": group.is_active,
                "max_posts_to_check": group.max_posts_to_check,
                "members_count": group.members_count,
                "photo_url": group.photo_url,
                "is_closed": group.is_closed,
                "total_posts_parsed": group.total_posts_parsed,
                "total_comments_found": group.total_comments_found,
                "last_parsed_at": group.last_parsed_at,
                "created_at": group.created_at,
                "updated_at": group.updated_at,
            }
            for group in groups
        ]

    async def create_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать новую группу"""
        # Валидация данных
        required_fields = ["vk_id", "screen_name", "name"]
        for field in required_fields:
            if field not in group_data or not group_data[field]:
                raise ValidationError(
                    f"Обязательное поле '{field}' не заполнено", field=field
                )

        # Проверяем, что группа с таким VK ID не существует
        existing = await self.repository.get_by_vk_id(group_data["vk_id"])
        if existing:
            raise ValidationError(
                "Группа с таким VK ID уже существует", field="vk_id"
            )

        # Проверяем, что screen_name уникален
        existing_screen = await self.repository.get_by_screen_name(
            group_data["screen_name"]
        )
        if existing_screen:
            raise ValidationError(
                "Группа с таким screen_name уже существует",
                field="screen_name",
            )

        # Создаем группу
        group = await self.repository.create(group_data)
        return await self.get_group(group.id)

    async def update_group(
        self, group_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить группу"""
        # Валидация входных данных
        allowed_fields = [
            "name",
            "screen_name",
            "description",
            "is_active",
            "max_posts_to_check",
            "members_count",
            "photo_url",
            "is_closed",
        ]
        filtered_data = {
            k: v for k, v in update_data.items() if k in allowed_fields
        }

        if not filtered_data:
            raise ValidationError("Нет допустимых полей для обновления")

        # Проверяем уникальность screen_name при обновлении
        if "screen_name" in filtered_data:
            existing = await self.repository.get_by_screen_name(
                filtered_data["screen_name"]
            )
            if existing and existing.id != group_id:
                raise ValidationError(
                    "Группа с таким screen_name уже существует",
                    field="screen_name",
                )

        await self.repository.update(group_id, filtered_data)
        return await self.get_group(group_id)

    async def delete_group(self, group_id: int) -> bool:
        """Удалить группу"""
        return await self.repository.delete(group_id)

    async def activate_group(self, group_id: int) -> Dict[str, Any]:
        """Активировать группу"""
        success = await self.repository.activate(group_id)
        if not success:
            raise GroupNotFoundError(group_id)

        return await self.get_group(group_id)

    async def deactivate_group(self, group_id: int) -> Dict[str, Any]:
        """Деактивировать группу"""
        success = await self.repository.deactivate(group_id)
        if not success:
            raise GroupNotFoundError(group_id)

        return await self.get_group(group_id)

    async def get_group_by_vk_id(self, vk_id: int) -> Optional[Dict[str, Any]]:
        """Получить группу по VK ID"""
        group = await self.repository.get_by_vk_id(vk_id)
        if not group:
            return None

        return await self.get_group(group.id)

    async def get_group_by_screen_name(
        self, screen_name: str
    ) -> Optional[Dict[str, Any]]:
        """Получить группу по screen_name"""
        group = await self.repository.get_by_screen_name(screen_name)
        if not group:
            return None

        return await self.get_group(group.id)

    async def bulk_activate(self, group_ids: List[int]) -> Dict[str, Any]:
        """Массовое включение групп"""
        update_data = {"is_active": True, "updated_at": datetime.utcnow()}
        success_count = await self.repository.bulk_update(
            group_ids, update_data
        )

        return {
            "success_count": success_count,
            "total_requested": len(group_ids),
            "message": f"Успешно активировано {success_count} из {len(group_ids)} групп",
        }

    async def bulk_deactivate(self, group_ids: List[int]) -> Dict[str, Any]:
        """Массовое отключение групп"""
        update_data = {"is_active": False, "updated_at": datetime.utcnow()}
        success_count = await self.repository.bulk_update(
            group_ids, update_data
        )

        return {
            "success_count": success_count,
            "total_requested": len(group_ids),
            "message": f"Успешно деактивировано {success_count} из {len(group_ids)} групп",
        }

    async def get_group_stats(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику группы"""
        return await self.repository.get_stats(group_id)

    async def get_groups_stats(self) -> Dict[str, Any]:
        """Получить общую статистику по группам"""
        return await self.repository.get_overall_stats()

    async def search_groups(
        self,
        query: str,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Поиск групп по названию или screen_name"""
        if not query or len(query.strip()) < 2:
            raise ValidationError(
                "Запрос поиска должен содержать минимум 2 символа",
                field="query",
            )

        return await self.get_groups(
            is_active=is_active,
            search=query.strip(),
            limit=limit,
            offset=offset,
        )

    async def count_groups(
        self, is_active: Optional[bool] = None, search: Optional[str] = None
    ) -> int:
        """Подсчитать количество групп"""
        return await self.repository.count(is_active=is_active, search=search)


# Экспорт
__all__ = [
    "GroupService",
]
