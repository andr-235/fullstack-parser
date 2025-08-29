"""
Улучшенный роутер парсера с:
- Стандартизированными ответами
- Error handling
- Улучшенной валидацией
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request

from app.core.database import get_db
from app.services.parsing_manager import ParsingManager
from app.services.comment_service import CommentService
from app.api.v1.routers.base import BaseRouter
from app.api.v1.handlers.common import (
    create_success_response,
    create_error_response,
)


router = BaseRouter("/parser", ["Parser"])


@router.post("/parse")
async def start_parsing(
    request: Request,
    group_ids: list,  # Здесь должна быть Pydantic схема
    db=Depends(get_db),
):
    """
    Запустить парсинг комментариев для групп VK.

    - **group_ids**: Список ID групп для парсинга
    """
    manager = ParsingManager()

    try:
        task = await manager.start_parsing(db, group_ids)
        return await create_success_response(request, task)

    except ValueError as e:
        return await create_error_response(
            request, 400, "VALIDATION_ERROR", str(e)
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to start parsing: {str(e)}",
        )


@router.post("/stop")
async def stop_parsing(
    request: Request,
    task_id: Optional[str] = None,
    db=Depends(get_db),
):
    """
    Остановить парсинг.

    - **task_id**: ID задачи для остановки (опционально)
    """
    manager = ParsingManager()

    try:
        result = await manager.stop_parsing(db, task_id)
        return await create_success_response(request, result)

    except Exception as e:
        return await create_error_response(
            request, 500, "INTERNAL_ERROR", f"Failed to stop parsing: {str(e)}"
        )


@router.get("/state")
async def get_parser_state(
    request: Request,
    db=Depends(get_db),
):
    """
    Получить состояние парсера.
    """
    manager = ParsingManager()

    try:
        state = await manager.get_parser_state(db)
        return await create_success_response(request, state)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to get parser state: {str(e)}",
        )


@router.get("/stats")
async def get_parser_stats(
    request: Request,
    db=Depends(get_db),
):
    """
    Получить статистику парсера.
    """
    manager = ParsingManager()

    try:
        stats = await manager.get_parser_stats(db)
        return await create_success_response(request, stats)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to get parser stats: {str(e)}",
        )


@router.get("/comments")
async def get_parsed_comments(
    request: Request,
    group_id: Optional[int] = Query(None, description="ID группы VK"),
    limit: int = Query(
        50, ge=1, le=100, description="Количество комментариев"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),
    db=Depends(get_db),
):
    """
    Получить распарсенные комментарии с фильтрацией и пагинацией.

    - **group_id**: ID группы VK для фильтрации
    - **limit**: Максимальное количество комментариев (1-100)
    - **offset**: Смещение для пагинации
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
            group_id=group_id, limit=limit, offset=offset
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
            f"Failed to fetch parsed comments: {str(e)}",
        )
