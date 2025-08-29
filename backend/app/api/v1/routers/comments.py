"""
Улучшенный роутер комментариев с:
- Стандартизированными ответами
- Улучшенной обработкой ошибок
- Пагинацией
- Валидацией
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request

from app.core.database import get_db
from app.services.comment_service import CommentService
from app.api.v1.routers.base import BaseRouter
from app.api.v1.handlers.common import (
    create_success_response,
    create_error_response,
)
from app.api.v1.schemas.errors import ValidationError, NotFoundError


router = BaseRouter("/comments", ["Comments"])


@router.get("/")
async def get_comments(
    request: Request,
    group_id: Optional[int] = Query(None, description="ID группы VK"),
    limit: int = Query(
        50, ge=1, le=100, description="Количество комментариев"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),
    include_group: bool = Query(
        False, description="Включить информацию о группе"
    ),
    db=Depends(get_db),
):
    """
    Получить комментарии с фильтрацией и пагинацией.

    - **group_id**: ID группы VK для фильтрации
    - **limit**: Максимальное количество комментариев (1-100)
    - **offset**: Смещение для пагинации
    - **include_group**: Включить информацию о группе в ответ
    """
    if not group_id:
        return await create_error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Parameter 'group_id' is required",
            field="group_id",
        )

    service = CommentService(db)

    try:
        # Получаем общее количество
        total = await service.get_comments_count({"group_id": group_id})

        # Получаем комментарии
        comments = await service.get_comments_paginated(
            group_id=group_id,
            limit=limit,
            offset=offset,
            include_group=include_group,
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

        return await create_success_response(request, comments, pagination)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch comments: {str(e)}",
        )


@router.get("/{comment_id}")
async def get_comment(
    request: Request,
    comment_id: int,
    db=Depends(get_db),
):
    """
    Получение комментария по ID.

    - **comment_id**: ID комментария в системе
    """
    service = CommentService(db)

    try:
        comment = await service.get_comment_by_id(comment_id)

        if not comment:
            return await create_error_response(
                request,
                404,
                "NOT_FOUND",
                f"Comment with id {comment_id} not found",
                details={"comment_id": comment_id},
            )

        return await create_success_response(request, comment)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch comment: {str(e)}",
        )


@router.get("/stats/summary")
async def get_comment_stats(
    request: Request,
    group_id: Optional[int] = Query(
        None, description="ID группы VK (если None - статистика по всем)"
    ),
    db=Depends(get_db),
):
    """
    Получить статистику по комментариям.

    - **group_id**: ID группы VK для фильтрации статистики
    """
    service = CommentService(db)

    try:
        stats = await service.get_comment_stats(group_id)
        return await create_success_response(request, stats)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch comment stats: {str(e)}",
        )
