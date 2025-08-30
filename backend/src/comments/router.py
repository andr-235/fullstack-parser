"""
FastAPI роутер для модуля Comments

Определяет API эндпоинты для работы с комментариями
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request

from .dependencies import get_comment_service
from .schemas import (
    CommentResponse,
    CommentListResponse,
    CommentCreate,
    CommentUpdate,
    CommentFilter,
    CommentStats,
    CommentBulkAction,
    CommentBulkResponse,
)
from .service import CommentService
from ..pagination import (
    get_pagination_params,
    PaginationParams,
    create_paginated_response,
    PageParam,
    SizeParam,
    SearchParam,
)

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
    responses={
        404: {"description": "Комментарий не найден"},
        422: {"description": "Ошибка валидации данных"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)


@router.get(
    "/",
    response_model=CommentListResponse,
    summary="Получить список комментариев",
    description="Получить список комментариев с фильтрацией и пагинацией"
)
async def get_comments(
    # Параметры пагинации
    page: PageParam = 1,
    size: SizeParam = 20,
    # Параметры фильтрации
    group_id: Optional[str] = Query(None, description="ID группы VK для фильтрации"),
    post_id: Optional[str] = Query(None, description="ID поста для фильтрации"),
    search: SearchParam = None,
    # Сервисы
    service: CommentService = Depends(get_comment_service),
) -> CommentListResponse:
    """Получить список комментариев с фильтрацией и пагинацией"""

    pagination = PaginationParams(
        page=page,
        size=size,
        search=search,
    )

    # Определяем тип запроса
    if post_id:
        # Комментарии к конкретному посту
        comments = await service.get_comments_by_post(
            post_id=post_id,
            limit=pagination.limit,
            offset=pagination.offset
        )
        # Для поста получаем общее количество комментариев
        total = len(comments)  # В реальности нужно получить из БД

    elif group_id:
        # Комментарии группы
        comments = await service.get_comments_by_group(
            group_id=group_id,
            limit=pagination.limit,
            offset=pagination.offset,
            search_text=pagination.search
        )
        # Получаем общее количество для пагинации
        stats = await service.get_group_stats(group_id)
        total = stats["total_comments"]

    else:
        # Общий поиск по всем комментариям
        if not pagination.search:
            raise HTTPException(
                status_code=400,
                detail="Необходимо указать group_id, post_id или поисковый запрос"
            )

        comments = await service.search_comments(
            query=pagination.search,
            limit=pagination.limit,
            offset=pagination.offset
        )
        total = len(comments)  # В реальности нужно получить из БД

    return create_paginated_response(comments, total, pagination)


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Получить комментарий по ID",
    description="Получить детальную информацию о комментарии"
)
async def get_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
) -> CommentResponse:
    """Получить комментарий по ID"""
    try:
        return await service.get_comment(comment_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=201,
    summary="Создать новый комментарий",
    description="Создать новый комментарий в системе"
)
async def create_comment(
    comment_data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
) -> CommentResponse:
    """Создать новый комментарий"""
    try:
        return await service.create_comment(comment_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Обновить комментарий",
    description="Обновить информацию о комментарии"
)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
) -> CommentResponse:
    """Обновить комментарий"""
    try:
        return await service.update_comment(comment_id, comment_data.model_dump(exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{comment_id}",
    status_code=204,
    summary="Удалить комментарий",
    description="Удалить комментарий из системы"
)
async def delete_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
):
    """Удалить комментарий"""
    try:
        success = await service.delete_comment(comment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Комментарий не найден")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{comment_id}/view",
    response_model=CommentResponse,
    summary="Отметить комментарий как просмотренный",
    description="Отметить комментарий как просмотренный и обновить время обработки"
)
async def mark_comment_as_viewed(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
) -> CommentResponse:
    """Отметить комментарий как просмотренный"""
    try:
        return await service.mark_as_viewed(comment_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/bulk/view",
    response_model=CommentBulkResponse,
    summary="Массовое отмечание комментариев",
    description="Отметить несколько комментариев как просмотренные"
)
async def bulk_mark_as_viewed(
    action_data: CommentBulkAction,
    service: CommentService = Depends(get_comment_service),
) -> CommentBulkResponse:
    """Массовое отмечание комментариев как просмотренные"""
    try:
        if action_data.action != "view":
            raise HTTPException(status_code=400, detail="Поддерживается только действие 'view'")

        result = await service.bulk_mark_as_viewed(action_data.comment_ids)
        return CommentBulkResponse(
            success_count=result["success_count"],
            error_count=result["total_requested"] - result["success_count"],
            errors=[]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/stats/{group_id}",
    response_model=CommentStats,
    summary="Получить статистику комментариев группы",
    description="Получить статистику комментариев для указанной группы"
)
async def get_group_stats(
    group_id: str,
    service: CommentService = Depends(get_comment_service),
) -> CommentStats:
    """Получить статистику комментариев группы"""
    try:
        stats = await service.get_group_stats(group_id)
        return CommentStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/search/",
    response_model=CommentListResponse,
    summary="Поиск комментариев",
    description="Поиск комментариев по тексту с фильтрацией"
)
async def search_comments(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    group_id: Optional[str] = Query(None, description="Ограничить поиск группой"),
    page: PageParam = 1,
    size: SizeParam = 20,
    service: CommentService = Depends(get_comment_service),
) -> CommentListResponse:
    """Поиск комментариев по тексту"""
    try:
        pagination = PaginationParams(page=page, size=size)
        comments = await service.search_comments(
            query=q,
            group_id=group_id,
            limit=pagination.limit,
            offset=pagination.offset
        )

        # В реальности нужно получить total из БД
        total = len(comments)
        return create_paginated_response(comments, total, pagination)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Экспорт роутера
__all__ = ["router"]
