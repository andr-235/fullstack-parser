"""
FastAPI роутер для модуля Groups

Определяет API эндпоинты для работы с группами VK
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request

from .dependencies import get_group_service
from .schemas import (
    GroupResponse,
    GroupListResponse,
    GroupCreate,
    GroupUpdate,
    GroupStats,
    GroupsStats,
    GroupBulkAction,
    GroupBulkResponse,
)
from .service import GroupService
from ..pagination import (
    get_pagination_params,
    PaginationParams,
    create_paginated_response,
    PageParam,
    SizeParam,
    SearchParam,
)

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
    responses={
        404: {"description": "Группа не найдена"},
        422: {"description": "Ошибка валидации данных"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)


@router.get(
    "/",
    response_model=GroupListResponse,
    summary="Получить список групп",
    description="Получить список групп VK с фильтрацией и пагинацией",
)
async def get_groups(
    # Параметры пагинации
    page: PageParam = 1,
    size: SizeParam = 20,
    # Параметры фильтрации
    is_active: Optional[bool] = Query(
        None, description="Показать только активные группы"
    ),
    search: SearchParam = None,
    # Сервисы
    service: GroupService = Depends(get_group_service),
) -> GroupListResponse:
    """Получить список групп с фильтрацией и пагинацией"""

    pagination = PaginationParams(
        page=page,
        size=size,
        search=search,
    )

    # Получаем группы
    groups = await service.get_groups(
        is_active=is_active,
        search=pagination.search,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    # Получаем общее количество для пагинации
    total = await service.count_groups(
        is_active=is_active, search=pagination.search
    )

    return create_paginated_response(groups, total, pagination)


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Получить группу по ID",
    description="Получить детальную информацию о группе VK",
)
async def get_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по ID"""
    try:
        return await service.get_group(group_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/vk/{vk_id}",
    response_model=GroupResponse,
    summary="Получить группу по VK ID",
    description="Получить информацию о группе по её VK ID",
)
async def get_group_by_vk_id(
    vk_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по VK ID"""
    group = await service.get_group_by_vk_id(vk_id)
    if not group:
        raise HTTPException(
            status_code=404, detail=f"Группа с VK ID {vk_id} не найдена"
        )
    return group


@router.get(
    "/screen/{screen_name}",
    response_model=GroupResponse,
    summary="Получить группу по screen_name",
    description="Получить информацию о группе по её screen_name",
)
async def get_group_by_screen_name(
    screen_name: str,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по screen_name"""
    group = await service.get_group_by_screen_name(screen_name)
    if not group:
        raise HTTPException(
            status_code=404, detail=f"Группа @{screen_name} не найдена"
        )
    return group


@router.post(
    "/",
    response_model=GroupResponse,
    status_code=201,
    summary="Создать новую группу",
    description="Создать новую группу VK в системе",
)
async def create_group(
    group_data: GroupCreate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Создать новую группу"""
    try:
        return await service.create_group(group_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Обновить группу",
    description="Обновить информацию о группе VK",
)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Обновить группу"""
    try:
        return await service.update_group(
            group_id, group_data.model_dump(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{group_id}",
    status_code=204,
    summary="Удалить группу",
    description="Удалить группу VK из системы",
)
async def delete_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
):
    """Удалить группу"""
    try:
        success = await service.delete_group(group_id)
        if not success:
            raise HTTPException(status_code=404, detail="Группа не найдена")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{group_id}/activate",
    response_model=GroupResponse,
    summary="Активировать группу",
    description="Активировать группу для мониторинга",
)
async def activate_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Активировать группу"""
    try:
        return await service.activate_group(group_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{group_id}/deactivate",
    response_model=GroupResponse,
    summary="Деактивировать группу",
    description="Деактивировать группу и остановить мониторинг",
)
async def deactivate_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Деактивировать группу"""
    try:
        return await service.deactivate_group(group_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/bulk/activate",
    response_model=GroupBulkResponse,
    summary="Массовое включение групп",
    description="Активировать несколько групп одновременно",
)
async def bulk_activate_groups(
    action_data: GroupBulkAction,
    service: GroupService = Depends(get_group_service),
) -> GroupBulkResponse:
    """Массовое включение групп"""
    try:
        if action_data.action != "activate":
            raise HTTPException(
                status_code=400,
                detail="Поддерживается только действие 'activate'",
            )

        result = await service.bulk_activate(action_data.group_ids)
        return GroupBulkResponse(
            success_count=result["success_count"],
            error_count=result["total_requested"] - result["success_count"],
            errors=[],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/bulk/deactivate",
    response_model=GroupBulkResponse,
    summary="Массовое отключение групп",
    description="Деактивировать несколько групп одновременно",
)
async def bulk_deactivate_groups(
    action_data: GroupBulkAction,
    service: GroupService = Depends(get_group_service),
) -> GroupBulkResponse:
    """Массовое отключение групп"""
    try:
        if action_data.action != "deactivate":
            raise HTTPException(
                status_code=400,
                detail="Поддерживается только действие 'deactivate'",
            )

        result = await service.bulk_deactivate(action_data.group_ids)
        return GroupBulkResponse(
            success_count=result["success_count"],
            error_count=result["total_requested"] - result["success_count"],
            errors=[],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{group_id}/stats",
    response_model=GroupStats,
    summary="Получить статистику группы",
    description="Получить детальную статистику группы и её комментариев",
)
async def get_group_stats(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupStats:
    """Получить статистику группы"""
    try:
        stats = await service.get_group_stats(group_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        return GroupStats(**stats)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/stats/overview",
    response_model=GroupsStats,
    summary="Общая статистика по группам",
    description="Получить сводную статистику по всем группам",
)
async def get_groups_overview_stats(
    service: GroupService = Depends(get_group_service),
) -> GroupsStats:
    """Получить общую статистику по группам"""
    try:
        stats = await service.get_groups_stats()
        return GroupsStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/search/",
    response_model=GroupListResponse,
    summary="Поиск групп",
    description="Поиск групп по названию или screen_name",
)
async def search_groups(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    is_active: Optional[bool] = Query(
        None, description="Показать только активные группы"
    ),
    page: PageParam = 1,
    size: SizeParam = 20,
    service: GroupService = Depends(get_group_service),
) -> GroupListResponse:
    """Поиск групп по тексту"""
    try:
        pagination = PaginationParams(page=page, size=size)
        groups = await service.search_groups(
            query=q,
            is_active=is_active,
            limit=pagination.limit,
            offset=pagination.offset,
        )

        # В реальности нужно получить total из БД
        total = await service.count_groups(is_active=is_active, search=q)
        return create_paginated_response(groups, total, pagination)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Экспорт роутера
__all__ = ["router"]
