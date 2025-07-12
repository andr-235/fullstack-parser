"""
API endpoints для управления VK группами
"""

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import VKGroup
from app.schemas.base import PaginatedResponse, PaginationParams
from app.schemas.vk_group import (
    VKGroupCreate,
    VKGroupRead,
    VKGroupStats,
    VKGroupUpdate,
)

# from app.core.config import settings  # Удалено как неиспользуемое
# from app.services.vkbottle_service import VKBottleService  # Удалено как неиспользуемое
from app.services.group_service import group_service

router = APIRouter(tags=["Groups"])


def _extract_screen_name(url_or_name: str) -> Optional[str]:
    """Извлекает screen_name из URL или возвращает само значение."""
    if not url_or_name:
        return None

    # Паттерн для поиска screen_name в URL.
    # Используем [\w.-]+ для предотвращения ReDoS-уязвимости.
    match = re.search(r"(?:vk\.com/)?([\w.-]+)$", url_or_name)
    return match.group(1) if match else url_or_name


@router.post(
    "/", response_model=VKGroupRead, status_code=status.HTTP_201_CREATED
)
async def create_group(
    group_data: VKGroupCreate,
    db: AsyncSession = Depends(get_db),
) -> VKGroupRead:
    """Добавить новую VK группу для мониторинга"""
    group = await group_service.create_group_with_vk(db, group_data)
    return VKGroupRead.model_validate(group)


@router.get("/", response_model=PaginatedResponse[VKGroupRead])
async def get_groups(
    pagination: PaginationParams = Depends(),
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VKGroupRead]:
    """Получить список VK групп"""
    query = select(VKGroup)
    if active_only:
        query = query.filter(VKGroup.is_active.is_(True))

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    result = await db.execute(
        query.offset(pagination.skip).limit(pagination.size)
    )
    groups = result.scalars().all()

    return PaginatedResponse(
        total=total or 0,
        page=pagination.page,
        size=pagination.size,
        items=[VKGroupRead.model_validate(group) for group in groups],
    )


@router.get("/{group_id}", response_model=VKGroupRead)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> VKGroupRead:
    """Получить информацию о конкретной группе"""
    group = await db.get(VKGroup, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    return VKGroupRead.model_validate(group)


@router.put("/{group_id}", response_model=VKGroupRead)
async def update_group(
    group_id: int,
    group_update: VKGroupUpdate,
    db: AsyncSession = Depends(get_db),
) -> VKGroupRead:
    """Обновить настройки группы"""
    group = await group_service.update_group(db, group_id, group_update)
    return VKGroupRead.model_validate(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удалить группу"""
    await group_service.delete_group(db, group_id)
    return


@router.get("/{group_id}/stats", response_model=VKGroupStats)
async def get_group_stats(
    group_id: int, db: AsyncSession = Depends(get_db)
) -> VKGroupStats:
    """Получить статистику по группе"""
    group = await db.get(VKGroup, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    # TODO: Добавить получение детальной статистики из связанных таблиц
    validated_group = VKGroupRead.model_validate(group)
    return VKGroupStats(
        group_id=validated_group.vk_id,
        total_posts=0,
        total_comments=0,
        comments_with_keywords=0,
        last_activity=None,
        top_keywords=[],
    )
