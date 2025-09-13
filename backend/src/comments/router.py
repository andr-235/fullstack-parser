"""
FastAPI роутер для модуля Comments
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from comments.repository import CommentRepository
from comments.schemas import (
    BatchKeywordAnalysisRequest,
    BatchKeywordAnalysisResponse,
    CommentCreate,
    CommentFilter,
    CommentListResponse,
    CommentResponse,
    CommentStats,
    CommentUpdate,
    KeywordAnalysisRequest,
    KeywordAnalysisResponse,
    KeywordSearchRequest,
    KeywordSearchResponse,
    KeywordStatisticsResponse,
)
from comments.service import CommentService
from common.database import get_db_session

router = APIRouter(prefix="/comments", tags=["comments"])


def get_comment_service(db: AsyncSession = Depends(get_db_session)) -> CommentService:
    """Получить сервис комментариев"""
    repository = CommentRepository(db)
    return CommentService(repository)


# Основные CRUD операции
@router.get("/", response_model=CommentListResponse)
async def get_comments(
    group_id: Optional[int] = Query(None, description="ID группы"),
    post_id: Optional[int] = Query(None, description="ID поста"),
    author_id: Optional[int] = Query(None, description="ID автора"),
    search_text: Optional[str] = Query(None, min_length=2, description="Поисковый запрос"),
    is_deleted: Optional[bool] = Query(None, description="Фильтр по удаленным"),
    include_author: bool = Query(False, description="Включить информацию об авторе"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: CommentService = Depends(get_comment_service),
):
    """Получить список комментариев"""
    filters = CommentFilter(
        group_id=group_id, post_id=post_id, author_id=author_id,
        search_text=search_text, is_deleted=is_deleted
    )
    return await service.get_comments(filters, limit, offset, include_author)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    include_author: bool = Query(False, description="Включить информацию об авторе"),
    service: CommentService = Depends(get_comment_service),
):
    """Получить комментарий по ID"""
    comment = await service.get_comment(comment_id, include_author)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return comment


@router.get("/vk/{vk_id}", response_model=CommentResponse)
async def get_comment_by_vk_id(
    vk_id: int,
    service: CommentService = Depends(get_comment_service),
):
    """Получить комментарий по VK ID"""
    comment = await service.get_comment_by_vk_id(vk_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return comment


@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
):
    """Создать комментарий"""
    try:
        return await service.create_comment(comment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
):
    """Обновить комментарий"""
    comment = await service.update_comment(comment_id, update_data)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return comment


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
):
    """Удалить комментарий"""
    success = await service.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return {"message": "Комментарий удален"}


@router.get("/stats/overview", response_model=CommentStats)
async def get_stats(
    service: CommentService = Depends(get_comment_service),
):
    """Получить статистику комментариев"""
    return await service.get_stats()


# Эндпоинты для анализа ключевых слов
@router.post("/keyword-analysis/analyze", response_model=KeywordAnalysisResponse)
async def analyze_keywords(
    request: KeywordAnalysisRequest,
    service: CommentService = Depends(get_comment_service),
):
    """Анализ ключевых слов в комментарии"""
    try:
        return await service.analyze_keywords(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/keyword-analysis/analyze-batch", response_model=BatchKeywordAnalysisResponse)
async def analyze_batch_keywords(
    request: BatchKeywordAnalysisRequest,
    service: CommentService = Depends(get_comment_service),
):
    """Массовый анализ ключевых слов"""
    try:
        return await service.analyze_batch_keywords(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/keyword-analysis/search", response_model=KeywordSearchResponse)
async def search_by_keywords(
    request: KeywordSearchRequest,
    service: CommentService = Depends(get_comment_service),
):
    """Поиск комментариев по ключевым словам"""
    try:
        return await service.search_by_keywords(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/keyword-analysis/statistics", response_model=KeywordStatisticsResponse)
async def get_keyword_statistics(
    service: CommentService = Depends(get_comment_service),
):
    """Получить статистику ключевых слов"""
    return await service.get_keyword_statistics()
