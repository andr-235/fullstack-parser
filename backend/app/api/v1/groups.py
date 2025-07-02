"""
API endpoints для управления VK группами
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.vk_group import VKGroup
from app.schemas.base import PaginatedResponse, PaginationParams, StatusResponse
from app.schemas.vk_group import (
    VKGroupCreate,
    VKGroupResponse,
    VKGroupStats,
    VKGroupUpdate,
)
from app.services.vk_api_service import VKAPIService

router = APIRouter(prefix="/groups", tags=["VK Groups"])


@router.post("/", response_model=VKGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: VKGroupCreate, db: AsyncSession = Depends(get_async_session)
) -> VKGroupResponse:
    """Добавить новую VK группу для мониторинга"""

    # Получаем информацию о группе из VK API
    vk_service = VKAPIService()
    group_info = await vk_service.get_group_info(group_data.vk_id_or_screen_name)

    if not group_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Группа '{group_data.vk_id_or_screen_name}' не найдена в ВК",
        )

    # Проверяем, что группа ещё не добавлена
    existing = await db.execute(
        select(VKGroup).where(VKGroup.vk_id == group_info["id"])
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Группа уже добавлена в систему",
        )

    # Создаём новую группу
    new_group = VKGroup(
        vk_id=group_info["id"],
        screen_name=group_info["screen_name"],
        name=group_data.name or group_info["name"],
        description=group_data.description or group_info["description"],
        is_active=group_data.is_active,
        max_posts_to_check=group_data.max_posts_to_check,
        members_count=group_info["members_count"],
        is_closed=group_info["is_closed"],
        photo_url=group_info["photo_url"],
    )

    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)

    return VKGroupResponse.model_validate(new_group)


@router.get("/", response_model=PaginatedResponse)
async def get_groups(
    pagination: PaginationParams = Depends(),
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session),
) -> PaginatedResponse:
    """Получить список VK групп"""

    query = select(VKGroup)
    if active_only:
        query = query.where(VKGroup.is_active)

    # Подсчёт общего количества
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # Получение данных с пагинацией
    paginated_query = query.offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(paginated_query)
    groups = result.scalars().all()

    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=[VKGroupResponse.model_validate(group) for group in groups],
    )


@router.get("/{group_id}", response_model=VKGroupResponse)
async def get_group(
    group_id: int, db: AsyncSession = Depends(get_async_session)
) -> VKGroupResponse:
    """Получить информацию о конкретной группе"""

    result = await db.execute(select(VKGroup).where(VKGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    return VKGroupResponse.model_validate(group)


@router.put("/{group_id}", response_model=VKGroupResponse)
async def update_group(
    group_id: int,
    group_update: VKGroupUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> VKGroupResponse:
    """Обновить настройки группы"""

    result = await db.execute(select(VKGroup).where(VKGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    # Обновляем только указанные поля
    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)

    return VKGroupResponse.model_validate(group)


@router.delete("/{group_id}", response_model=StatusResponse)
async def delete_group(
    group_id: int, db: AsyncSession = Depends(get_async_session)
) -> StatusResponse:
    """Удалить группу из мониторинга"""

    result = await db.execute(select(VKGroup).where(VKGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    await db.delete(group)
    await db.commit()

    return StatusResponse(
        success=True, message=f"Группа '{group.name}' удалена из мониторинга"
    )


@router.get("/{group_id}/stats", response_model=VKGroupStats)
async def get_group_stats(
    group_id: int, db: AsyncSession = Depends(get_async_session)
) -> VKGroupStats:
    """Получить статистику по группе"""

    result = await db.execute(select(VKGroup).where(VKGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    # TODO: Добавить получение детальной статистики из связанных таблиц
    return VKGroupStats(
        group_id=group.id,
        total_posts=group.total_posts_parsed,
        total_comments=group.total_comments_found,
        comments_with_keywords=group.total_comments_found,  # TODO: точная статистика
        last_activity=group.last_parsed_at,
        top_keywords=[],  # TODO: получить из БД
    )
