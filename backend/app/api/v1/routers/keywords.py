"""
Улучшенный роутер ключевых слов с:
- Стандартизированными ответами
- Улучшенной пагинацией
- Error handling
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request

from app.core.database import get_db
from app.services.keyword_service import keyword_service
from app.api.v1.routers.base import BaseRouter
from app.api.v1.handlers.common import (
    create_success_response,
    create_error_response,
)


router = BaseRouter("/keywords", ["Keywords"])


@router.get("/")
async def get_keywords(
    request: Request,
    active_only: bool = Query(
        True, description="Только активные ключевые слова"
    ),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    q: Optional[str] = Query(None, description="Поисковый запрос"),
    limit: int = Query(
        50, ge=1, le=100, description="Количество ключевых слов"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),
    db=Depends(get_db),
):
    """
    Получить ключевые слова с фильтрацией и пагинацией.

    - **active_only**: Показывать только активные ключевые слова
    - **category**: Фильтр по категории
    - **q**: Поисковый запрос
    - **limit**: Максимальное количество (1-100)
    - **offset**: Смещение для пагинации
    """
    try:
        # Создаем объект пагинации
        class PaginationParams:
            def __init__(self, limit: int, offset: int):
                self.limit = limit
                self.offset = offset

        pagination = PaginationParams(limit=limit, offset=offset)

        result = await keyword_service.get_keywords(
            db, pagination, active_only, category, q
        )

        return await create_success_response(
            request,
            result.items,
            {
                "page": (offset // limit) + 1,
                "size": limit,
                "total": result.total,
                "has_next": result.page < result.total_pages,
                "has_prev": result.page > 1,
                "total_pages": result.total_pages,
            },
        )

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch keywords: {str(e)}",
        )


@router.get("/{keyword_id}")
async def get_keyword(
    request: Request,
    keyword_id: int,
    db=Depends(get_db),
):
    """
    Получить ключевое слово по ID.

    - **keyword_id**: ID ключевого слова
    """
    try:
        keyword = await keyword_service.get_keyword_by_id(db, keyword_id)

        if not keyword:
            return await create_error_response(
                request,
                404,
                "NOT_FOUND",
                f"Keyword with id {keyword_id} not found",
                details={"keyword_id": keyword_id},
            )

        return await create_success_response(request, keyword)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch keyword: {str(e)}",
        )


@router.post("/")
async def create_keyword(
    request: Request,
    keyword_data: dict,  # Здесь должна быть Pydantic схема
    db=Depends(get_db),
):
    """
    Создать новое ключевое слово.

    - **word**: Ключевое слово
    - **category**: Категория
    - **is_active**: Активность
    """
    try:
        keyword = await keyword_service.create_keyword(db, keyword_data)
        return await create_success_response(request, keyword)

    except ValueError as e:
        return await create_error_response(
            request, 400, "VALIDATION_ERROR", str(e)
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to create keyword: {str(e)}",
        )
