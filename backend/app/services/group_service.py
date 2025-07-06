"""
Сервис для работы с моделью VKGroup.
"""

from typing import Optional

from app.models.vk_group import VKGroup
from app.schemas.vk_group import VKGroupCreate, VKGroupUpdate
from app.services.base import BaseService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class GroupService(BaseService[VKGroup, VKGroupCreate, VKGroupUpdate]):
    def __init__(self):
        super().__init__(VKGroup)

    async def get_by_screen_name(
        self, db: AsyncSession, *, screen_name: str
    ) -> Optional[VKGroup]:
        """Получить группу по ее короткому имени."""
        result = await db.execute(
            select(self.model).filter(self.model.screen_name == screen_name)
        )
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, db: AsyncSession, *, vk_id: int) -> Optional[VKGroup]:
        """Получить группу по ее VK ID."""
        result = await db.execute(select(self.model).filter(self.model.vk_id == vk_id))
        return result.scalar_one_or_none()


group_service = GroupService()
