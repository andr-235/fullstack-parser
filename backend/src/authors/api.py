"""
API роутеры для модуля авторов - упрощенная версия
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.database import get_db_session

from .schemas import (
    AuthorBulkAction,
    AuthorCreate,
    AuthorFilter,
    AuthorListResponse,
    AuthorResponse,
    AuthorSearch,
    AuthorStatus,
    AuthorUpdate,
    AuthorWithCommentsResponse,
)
from .services import AuthorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/authors", tags=["authors"])


def get_author_service(db: AsyncSession = Depends(get_db_session)) -> AuthorService:
    """Получает сервис авторов"""
    return AuthorService(db)


@router.post("/", response_model=AuthorResponse, status_code=201)
async def create_author(
    data: AuthorCreate,
    service: AuthorService = Depends(get_author_service)
):
    """Создает автора"""
    try:
        return await service.create_author(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating author: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(
    author_id: int = Path(..., gt=0),
    service: AuthorService = Depends(get_author_service)
):
    """Получает автора по ID"""
    author = await service.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.get("/{author_id}/with-comments", response_model=AuthorWithCommentsResponse)
async def get_author_with_comments(
    author_id: int = Path(..., gt=0),
    comments_limit: int = Query(20, ge=1, le=100, description="Количество комментариев"),
    comments_offset: int = Query(0, ge=0, description="Смещение для комментариев"),
    service: AuthorService = Depends(get_author_service)
):
    """Получает автора с его комментариями"""
    author = await service.get_author_with_comments(
        author_id=author_id,
        comments_limit=comments_limit,
        comments_offset=comments_offset
    )
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.get("/vk/{vk_id}", response_model=AuthorResponse)
async def get_author_by_vk_id(
    vk_id: int = Path(..., gt=0),
    service: AuthorService = Depends(get_author_service)
):
    """Получает автора по VK ID"""
    author = await service.get_by_vk_id(vk_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.get("/screen/{screen_name}", response_model=AuthorResponse)
async def get_author_by_screen_name(
    screen_name: str = Path(..., min_length=1),
    service: AuthorService = Depends(get_author_service)
):
    """Получает автора по screen name"""
    author = await service.get_by_screen_name(screen_name)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int = Path(..., gt=0),
    data: AuthorUpdate = None,
    service: AuthorService = Depends(get_author_service)
):
    """Обновляет автора"""
    author = await service.update_author(author_id, data)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.delete("/{author_id}", status_code=204)
async def delete_author(
    author_id: int = Path(..., gt=0),
    service: AuthorService = Depends(get_author_service)
):
    """Удаляет автора"""
    deleted = await service.delete_author(author_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Author not found")


@router.get("/", response_model=AuthorListResponse)
async def list_authors(
    status: Optional[AuthorStatus] = Query(None, description="Фильтр по статусу"),
    is_verified: Optional[bool] = Query(None, description="Фильтр по верификации"),
    is_closed: Optional[bool] = Query(None, description="Фильтр по закрытости"),
    limit: int = Query(50, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    order_by: str = Query("created_at", description="Поле для сортировки"),
    order_direction: str = Query("desc", description="Направление сортировки"),
    service: AuthorService = Depends(get_author_service)
):
    """Получает список авторов"""
    filter_data = AuthorFilter(
        status=status,
        is_verified=is_verified,
        is_closed=is_closed,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_direction=order_direction
    )
    return await service.list_authors(filter_data)


@router.get("/search/", response_model=AuthorListResponse)
async def search_authors(
    query: str = Query(..., min_length=1, max_length=100, description="Поисковый запрос"),
    limit: int = Query(50, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: AuthorService = Depends(get_author_service)
):
    """Поиск авторов"""
    search_data = AuthorSearch(query=query, limit=limit, offset=offset)
    return await service.search_authors(search_data)


@router.get("/stats/")
async def get_stats(
    service: AuthorService = Depends(get_author_service)
):
    """Получает статистику авторов"""
    return await service.get_stats()


@router.post("/bulk/")
async def bulk_action(
    action_data: AuthorBulkAction,
    service: AuthorService = Depends(get_author_service)
):
    """Выполняет массовое действие"""
    try:
        return await service.bulk_action(action_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health/")
async def health_check():
    """Health check для модуля авторов"""
    return {"status": "healthy", "module": "authors"}
