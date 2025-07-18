"""
Сервис для работы с моделью VKGroup.
"""

import re
from typing import Optional

import structlog
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.vk_group import VKGroup
from app.schemas.vk_group import VKGroupCreate, VKGroupUpdate
from app.services.base import BaseService
from app.services.vkbottle_service import VKBottleService


class GroupService(BaseService[VKGroup, VKGroupCreate, VKGroupUpdate]):
    def __init__(self):
        super().__init__(VKGroup)
        self.logger = structlog.get_logger(__name__)

    async def get_by_screen_name(
        self, db: AsyncSession, *, screen_name: str
    ) -> Optional[VKGroup]:
        """Получить группу по ее короткому имени."""
        result = await db.execute(
            select(self.model).filter(self.model.screen_name == screen_name)
        )
        return result.scalar_one_or_none()

    async def get_by_vk_id(
        self, db: AsyncSession, *, vk_id: int
    ) -> Optional[VKGroup]:
        """Получить группу по ее VK ID."""
        result = await db.execute(
            select(self.model).filter(self.model.vk_id == vk_id)
        )
        return result.scalar_one_or_none()

    async def create_group_with_vk(
        self, db: AsyncSession, group_data: VKGroupCreate
    ) -> VKGroup:
        """Создать группу через VK API с полной валидацией и фильтрацией."""
        screen_name = self._extract_screen_name(
            group_data.vk_id_or_screen_name
        )
        if not screen_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан ID или короткое имя группы.",
            )
        vk_service = VKBottleService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )
        vk_group_data = await vk_service.get_group_info(screen_name)
        if not vk_group_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Группа ВКонтакте не найдена.",
            )
        # Проверка на существование группы в БД (case-insensitive)
        existing_group_result = await db.execute(
            select(VKGroup).where(
                func.lower(VKGroup.screen_name) == screen_name.lower()
            )
        )
        existing_group = existing_group_result.scalar_one_or_none()
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Группа '{existing_group.name}' ({screen_name}) уже существует в системе.",
            )
        # Фильтрация только нужных полей для VKGroup
        vk_group_fields = {c.name for c in VKGroup.__table__.columns}
        filtered_data = {
            k: v for k, v in vk_group_data.items() if k in vk_group_fields
        }
        # Маппинг id -> vk_id
        if "id" in vk_group_data:
            filtered_data["vk_id"] = vk_group_data["id"]
        new_group = VKGroup(**filtered_data)
        db.add(new_group)
        await db.commit()
        await db.refresh(new_group)
        return new_group

    async def update_group(
        self, db: AsyncSession, group_id: int, group_update: VKGroupUpdate
    ) -> VKGroup:
        group = await db.get(VKGroup, group_id)
        if not group:
            self.logger.warning(f"Группа не найдена: id={group_id}")
            raise HTTPException(status_code=404, detail="Группа не найдена")
        update_data = group_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(group, key, value)
        await db.commit()
        await db.refresh(group)
        self.logger.info(f"Группа обновлена: id={group_id}")
        return group

    async def delete_group(self, db: AsyncSession, group_id: int) -> None:
        group = await db.get(VKGroup, group_id)
        if not group:
            self.logger.warning(
                f"Группа не найдена для удаления: id={group_id}"
            )
            return
        await db.delete(group)
        await db.commit()
        self.logger.info(f"Группа удалена: id={group_id}")

    def _extract_screen_name(self, url_or_name: str) -> Optional[str]:
        if not url_or_name:
            return None
        match = re.search(r"(?:vk\\.com/)?([\\w.-]+)$", url_or_name)
        return match.group(1) if match else url_or_name


group_service = GroupService()
