"""
Улучшенный роутер групп с:
- Стандартизированными ответами
- Улучшенной валидацией
- Пагинацией
- Error handling
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request

from app.core.database import get_db
from app.services.group_manager import GroupManager
from app.api.v1.routers.base import BaseRouter
from app.api.v1.handlers.common import (
    create_success_response,
    create_error_response,
)


router = BaseRouter("/groups", ["Groups"])


@router.get("/")
async def get_groups(
    request: Request,
    active_only: bool = Query(True, description="Только активные группы"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    limit: int = Query(50, ge=1, le=100, description="Количество групп"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db=Depends(get_db),
):
    """
    Получить список групп VK с фильтрацией и пагинацией.

    - **active_only**: Показывать только активные группы
    - **search**: Поиск по названию группы
    - **limit**: Максимальное количество групп (1-100)
    - **offset**: Смещение для пагинации
    """
    manager = GroupManager()

    try:
        # Получаем общее количество
        total = await manager.get_groups_count(
            db, active_only=active_only, search=search
        )

        # Получаем группы
        groups = await manager.get_groups_paginated(
            db=db,
            active_only=active_only,
            search=search,
            limit=limit,
            offset=offset,
        )

        # Создаем информацию о пагинации
        pagination = {
            "page": (offset // limit) + 1,
            "size": limit,
            "total": total,
            "has_next": (offset + limit) < total,
            "has_prev": offset > 0,
            "total_pages": (total + limit - 1) // limit,
        }

        return await create_success_response(request, groups, pagination)

    except Exception as e:
        return await create_error_response(
            request, 500, "INTERNAL_ERROR", f"Failed to fetch groups: {str(e)}"
        )


@router.get("/{group_id}")
async def get_group(
    request: Request,
    group_id: int,
    db=Depends(get_db),
):
    """
    Получить информацию о конкретной группе.

    - **group_id**: ID группы в системе
    """
    manager = GroupManager()

    try:
        group = await manager.get_by_id(db, group_id)

        if not group:
            return await create_error_response(
                request,
                404,
                "NOT_FOUND",
                f"Group with id {group_id} not found",
                details={"group_id": group_id},
            )

        return await create_success_response(request, group)

    except Exception as e:
        return await create_error_response(
            request, 500, "INTERNAL_ERROR", f"Failed to fetch group: {str(e)}"
        )


@router.put("/{group_id}")
async def update_group(
    request: Request,
    group_id: int,
    group_data: dict,  # Здесь должна быть Pydantic схема
    db=Depends(get_db),
):
    """
    Обновить настройки группы.

    - **group_id**: ID группы в системе
    - **group_data**: Данные для обновления
    """
    manager = GroupManager()

    try:
        group = await manager.update_group(db, group_id, group_data)

        if not group:
            return await create_error_response(
                request,
                404,
                "NOT_FOUND",
                f"Group with id {group_id} not found",
                details={"group_id": group_id},
            )

        return await create_success_response(request, group)

    except ValueError as e:
        return await create_error_response(
            request, 400, "VALIDATION_ERROR", str(e)
        )
    except Exception as e:
        return await create_error_response(
            request, 500, "INTERNAL_ERROR", f"Failed to update group: {str(e)}"
        )


@router.post("/")
async def create_group(
    request: Request,
    group_data: dict,  # Здесь должна быть Pydantic схема
    db=Depends(get_db),
):
    """
    Создать новую группу VK.

    - **vk_id_or_screen_name**: ID или screen_name группы VK
    - **is_active**: Активность группы
    - **max_posts_to_check**: Максимум постов для проверки
    """
    manager = GroupManager()

    try:
        group = await manager.create_group(db, group_data)
        return await create_success_response(request, group)

    except ValueError as e:
        return await create_error_response(
            request, 400, "VALIDATION_ERROR", str(e)
        )
    except Exception as e:
        return await create_error_response(
            request, 500, "INTERNAL_ERROR", f"Failed to create group: {str(e)}"
        )
