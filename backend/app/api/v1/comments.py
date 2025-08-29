"""
API эндпоинты для работы с комментариями через CommentService
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.base import PaginatedResponse, PaginationParams
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentUpdateRequest,
    CommentWithKeywords,
    VKCommentResponse,
)
from app.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/", response_model=PaginatedResponse[VKCommentResponse])
async def get_comments(
    group_id: Optional[int] = Query(None, description="ID группы VK"),
    limit: int = Query(
        50, ge=1, le=100, description="Количество комментариев"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),
    include_group: bool = Query(
        False, description="Включить информацию о группе"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить комментарии с фильтрацией и пагинацией.

    - **group_id**: ID группы VK для фильтрации
    - **limit**: Максимальное количество комментариев (1-100)
    - **offset**: Смещение для пагинации
    - **include_group**: Включить информацию о группе в ответ
    """
    if not group_id:
        raise HTTPException(
            status_code=400, detail="Parameter 'group_id' is required"
        )

    service = CommentService(db)

    try:
        comments = await service.get_comments_by_group(
            group_id=group_id,
            limit=limit,
            offset=offset,
            include_group=include_group,
        )

        # Вычисляем общее количество для пагинации
        # В реальном приложении здесь был бы отдельный запрос для подсчета
        total = len(comments) + offset  # Упрощенная логика для демонстрации

        return PaginatedResponse(
            total=total, page=(offset // limit) + 1, size=limit, items=comments
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[CommentWithKeywords])
async def search_comments(
    text: Optional[str] = Query(None, description="Текст для поиска"),
    group_id: Optional[int] = Query(None, description="ID группы VK"),
    author_id: Optional[int] = Query(None, description="ID автора"),
    date_from: Optional[str] = Query(
        None, description="Дата начала (ISO format)"
    ),
    date_to: Optional[str] = Query(
        None, description="Дата окончания (ISO format)"
    ),
    is_viewed: Optional[bool] = Query(
        None, description="Просмотрен ли комментарий"
    ),
    limit: int = Query(50, ge=1, le=100, description="Количество результатов"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    """
    Поиск комментариев по различным критериям.

    - **text**: Текст для поиска в комментариях
    - **group_id**: ID группы VK
    - **author_id**: ID автора комментария
    - **date_from/date_to**: Диапазон дат
    - **is_viewed**: Статус просмотра
    """
    # Преобразуем параметры в объект CommentSearchParams
    from datetime import datetime

    search_params = CommentSearchParams(
        text=text,
        group_id=group_id,
        author_id=author_id,
        date_from=datetime.fromisoformat(date_from) if date_from else None,
        date_to=datetime.fromisoformat(date_to) if date_to else None,
        is_viewed=is_viewed,
    )

    service = CommentService(db)

    try:
        comments = await service.search_comments(
            search_params=search_params, limit=limit, offset=offset
        )

        return comments

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{comment_id}", response_model=VKCommentResponse)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить комментарий по ID.

    - **comment_id**: ID комментария в базе данных
    """
    service = CommentService(db)

    try:
        comment = await service.get_comment_by_id(comment_id)

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        return comment

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{comment_id}", response_model=VKCommentResponse)
async def update_comment(
    comment_id: int,
    update_data: CommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Обновить статус комментария.

    - **comment_id**: ID комментария
    - **update_data**: Данные для обновления (is_viewed, is_archived)
    """
    service = CommentService(db)

    try:
        comment = await service.update_comment(comment_id, update_data)

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        return comment

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_comment_stats(
    group_id: Optional[int] = Query(
        None, description="ID группы VK (если None - статистика по всем)"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить статистику по комментариям.

    - **group_id**: ID группы VK для фильтрации статистики
    """
    service = CommentService(db)

    try:
        stats = await service.get_comment_stats(group_id)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
