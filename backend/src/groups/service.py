"""
Сервис для работы с группами VK
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.exceptions import NotFoundError, ValidationError

from .models import Group


class GroupService:
    """Сервис для работы с группами VK"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_group(self, group_id: int) -> Group:
        """Получить группу по ID"""
        query = select(Group).where(Group.id == group_id)
        result = await self.db.execute(query)
        group = result.scalar_one_or_none()
        if not group:
            raise NotFoundError(f"Группа с ID {group_id} не найдена")
        return group

    async def get_groups(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Group]:
        """Получить список групп с фильтрацией"""
        query = select(Group)

        if is_active is not None:
            query = query.where(Group.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Group.name.ilike(search_filter),
                    Group.screen_name.ilike(search_filter),
                    Group.description.ilike(search_filter),
                )
            )

        query = query.order_by(desc(Group.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_group(self, group_data: dict) -> Group:
        """Создать новую группу"""
        # Валидация обязательных полей
        required_fields = ["vk_id", "screen_name", "name"]
        for field in required_fields:
            if field not in group_data or not group_data[field]:
                raise ValidationError(f"Обязательное поле '{field}' не заполнено")

        # Проверка уникальности VK ID
        existing = await self._get_by_vk_id(group_data["vk_id"])
        if existing:
            raise ValidationError("Группа с таким VK ID уже существует")

        # Проверка уникальности screen_name
        existing_screen = await self._get_by_screen_name(group_data["screen_name"])
        if existing_screen:
            raise ValidationError("Группа с таким screen_name уже существует")

        # Создание группы
        group = Group(**group_data)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def update_group(self, group_id: int, update_data: dict) -> Group:
        """Обновить группу"""
        group = await self.get_group(group_id)

        # Проверка уникальности screen_name при обновлении
        if "screen_name" in update_data:
            existing = await self._get_by_screen_name(update_data["screen_name"])
            if existing and existing.id != group_id:
                raise ValidationError("Группа с таким screen_name уже существует")

        # Обновление полей
        for key, value in update_data.items():
            if hasattr(group, key):
                setattr(group, key, value)

        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete_group(self, group_id: int) -> bool:
        """Удалить группу"""
        group = await self.get_group(group_id)
        await self.db.delete(group)
        await self.db.commit()
        return True

    async def activate_group(self, group_id: int) -> Group:
        """Активировать группу"""
        return await self.update_group(group_id, {"is_active": True})

    async def deactivate_group(self, group_id: int) -> Group:
        """Деактивировать группу"""
        return await self.update_group(group_id, {"is_active": False})

    async def get_group_by_vk_id(self, vk_id: int) -> Optional[Group]:
        """Получить группу по VK ID"""
        return await self._get_by_vk_id(vk_id)

    async def get_group_by_screen_name(self, screen_name: str) -> Optional[Group]:
        """Получить группу по screen_name"""
        return await self._get_by_screen_name(screen_name)

    async def bulk_activate(self, group_ids: List[int]) -> dict:
        """Массовое включение групп"""
        update_data = {"is_active": True, "updated_at": datetime.utcnow()}
        query = update(Group).where(Group.id.in_(group_ids)).values(**update_data)
        result = await self.db.execute(query)
        await self.db.commit()
        return {
            "success_count": result.rowcount,
            "total_requested": len(group_ids),
        }

    async def bulk_deactivate(self, group_ids: List[int]) -> dict:
        """Массовое отключение групп"""
        update_data = {"is_active": False, "updated_at": datetime.utcnow()}
        query = update(Group).where(Group.id.in_(group_ids)).values(**update_data)
        result = await self.db.execute(query)
        await self.db.commit()
        return {
            "success_count": result.rowcount,
            "total_requested": len(group_ids),
        }

    async def count_groups(
        self, is_active: Optional[bool] = None, search: Optional[str] = None
    ) -> int:
        """Подсчитать количество групп"""
        query = select(func.count()).select_from(Group)

        if is_active is not None:
            query = query.where(Group.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Group.name.ilike(search_filter),
                    Group.screen_name.ilike(search_filter),
                    Group.description.ilike(search_filter),
                )
            )

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def _get_by_vk_id(self, vk_id: int) -> Optional[Group]:
        """Получить группу по VK ID (внутренний метод)"""
        query = select(Group).where(Group.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_by_screen_name(self, screen_name: str) -> Optional[Group]:
        """Получить группу по screen_name (внутренний метод)"""
        query = select(Group).where(Group.screen_name == screen_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_groups_count(self) -> int:
        """Получить количество активных групп"""
        query = select(func.count(Group.id)).where(Group.is_active == True)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_groups_count_by_period(self, days: int = 30) -> int:
        """Получить количество групп за период"""
        since_date = datetime.utcnow() - timedelta(days=days)
        query = select(func.count(Group.id)).where(Group.created_at >= since_date)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_groups_growth_percentage(self, days: int = 30) -> float:
        """Получить процент роста групп за период"""
        current_period = await self.get_groups_count_by_period(days)
        previous_period = await self.get_groups_count_by_period(days * 2) - current_period
        
        if previous_period == 0:
            return 100.0 if current_period > 0 else 0.0
        
        return ((current_period - previous_period) / previous_period) * 100


__all__ = ["GroupService"]
