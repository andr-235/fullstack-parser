"""
FastAPI роутер для модуля Groups
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    GroupResponse,
    GroupListResponse,
    GroupCreate,
    GroupUpdate,
    GroupBulkAction,
    GroupBulkResponse,
)
from .service import GroupService
from .dependencies import get_group_service
from shared.presentation.responses.response_utils import (
    PageParam,
    SizeParam,
    SearchParam,
    PaginationParams,
)

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/", response_model=GroupListResponse)
async def get_groups(
    page: PageParam = 1,
    size: SizeParam = 20,
    is_active: Optional[bool] = Query(None, description="Показать только активные группы"),
    search: SearchParam = None,
    service: GroupService = Depends(get_group_service),
) -> GroupListResponse:
    """Получить список групп с фильтрацией и пагинацией"""
    pagination = PaginationParams(page=page, size=size, search=search)
    
    groups = await service.get_groups(
        is_active=is_active,
        search=pagination.search,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    
    total = await service.count_groups(is_active=is_active, search=pagination.search)
    
    return GroupListResponse(
        items=[GroupResponse.model_validate(g) for g in groups],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size if pagination.size > 0 else 0,
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по ID"""
    try:
        group = await service.get_group(group_id)
        return GroupResponse.model_validate(group)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/vk/{vk_id}", response_model=GroupResponse)
async def get_group_by_vk_id(
    vk_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по VK ID"""
    group = await service.get_group_by_vk_id(vk_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"Группа с VK ID {vk_id} не найдена")
    return GroupResponse.model_validate(group)


@router.get("/screen/{screen_name}", response_model=GroupResponse)
async def get_group_by_screen_name(
    screen_name: str,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по screen_name"""
    group = await service.get_group_by_screen_name(screen_name)
    if not group:
        raise HTTPException(status_code=404, detail=f"Группа @{screen_name} не найдена")
    return GroupResponse.model_validate(group)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(
    group_data: GroupCreate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Создать новую группу"""
    try:
        created = await service.create_group(group_data.model_dump())
        return GroupResponse.model_validate(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Обновить группу"""
    try:
        updated = await service.update_group(group_id, group_data.model_dump(exclude_unset=True))
        return GroupResponse.model_validate(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
):
    """Удалить группу"""
    try:
        await service.delete_group(group_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{group_id}/activate", response_model=GroupResponse)
async def activate_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Активировать группу"""
    try:
        activated = await service.activate_group(group_id)
        return GroupResponse.model_validate(activated)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{group_id}/deactivate", response_model=GroupResponse)
async def deactivate_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Деактивировать группу"""
    try:
        deactivated = await service.deactivate_group(group_id)
        return GroupResponse.model_validate(deactivated)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk/activate", response_model=GroupBulkResponse)
async def bulk_activate_groups(
    action_data: GroupBulkAction,
    service: GroupService = Depends(get_group_service),
) -> GroupBulkResponse:
    """Массовое включение групп"""
    try:
        if action_data.action != "activate":
            raise HTTPException(status_code=400, detail="Поддерживается только действие 'activate'")
        
        result = await service.bulk_activate(action_data.group_ids)
        return GroupBulkResponse(
            success_count=result["success_count"],
            error_count=result["total_requested"] - result["success_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk/deactivate", response_model=GroupBulkResponse)
async def bulk_deactivate_groups(
    action_data: GroupBulkAction,
    service: GroupService = Depends(get_group_service),
) -> GroupBulkResponse:
    """Массовое отключение групп"""
    try:
        if action_data.action != "deactivate":
            raise HTTPException(status_code=400, detail="Поддерживается только действие 'deactivate'")
        
        result = await service.bulk_deactivate(action_data.group_ids)
        return GroupBulkResponse(
            success_count=result["success_count"],
            error_count=result["total_requested"] - result["success_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))







__all__ = ["router"]
