"""
API endpoints для управления VK группами
"""

import re
from typing import Optional

from app.core.database import get_async_session
from app.models import VKGroup
from app.schemas.base import PaginatedResponse, PaginationParams
from app.schemas.vk_group import VKGroupCreate, VKGroupRead, VKGroupStats, VKGroupUpdate
from app.services.vk_api_service import VKAPIService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Groups"])


def _extract_screen_name(url_or_name: str) -> Optional[str]:
    """Извлекает screen_name из URL или возвращает само значение."""
    if not url_or_name:
        return None

    # Паттерн для поиска screen_name в URL.
    # Используем [\w.-]+ для предотвращения ReDoS-уязвимости.
    match = re.search(r"(?:vk\.com/)?([\w.-]+)$", url_or_name)
    return match.group(1) if match else url_or_name


@router.post("/", response_model=VKGroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: VKGroupCreate, db: AsyncSession = Depends(get_async_session)
) -> VKGroupRead:
    """Добавить новую VK группу для мониторинга"""

    vk_api_service = VKAPIService()
    vk_group_data = await vk_api_service.get_group_info(group_data.vk_id_or_screen_name)

    if not vk_group_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа ВКонтакте не найдена.",
        )

    # TODO: Перенести логику в сервис
    new_group = VKGroup(**vk_group_data)
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)

    return VKGroupRead.model_validate(new_group)


@router.get("/", response_model=PaginatedResponse[VKGroupRead])
async def get_groups(
    pagination: PaginationParams = Depends(),
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session),
) -> PaginatedResponse[VKGroupRead]:
    """Получить список VK групп"""
    query = select(VKGroup)
    if active_only:
        query = query.filter(VKGroup.is_active.is_(True))

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    result = await db.execute(query.offset(pagination.skip).limit(pagination.size))
    groups = result.scalars().all()

    return PaginatedResponse(
        total=total or 0,
        page=pagination.page,
        size=pagination.size,
        items=[VKGroupRead.model_validate(group) for group in groups],
    )


@router.get("/{group_id}", response_model=VKGroupRead)
async def get_group(
    group_id: int, db: AsyncSession = Depends(get_async_session)
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
    db: AsyncSession = Depends(get_async_session),
) -> VKGroupRead:
    """Обновить настройки группы"""
    group = await db.get(VKGroup, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    update_data = group_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)

    await db.commit()
    await db.refresh(group)

    return VKGroupRead.model_validate(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: int, db: AsyncSession = Depends(get_async_session)):
    """Удалить группу"""
    group = await db.get(VKGroup, group_id)
    if group:
        await db.delete(group)
        await db.commit()
    return


@router.get("/{group_id}/stats", response_model=VKGroupStats)
async def get_group_stats(
    group_id: int, db: AsyncSession = Depends(get_async_session)
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
        group_id=validated_group.id,
        total_posts=0,
        total_comments=0,
        comments_with_keywords=0,
        last_activity=None,
        top_keywords=[],
    )
