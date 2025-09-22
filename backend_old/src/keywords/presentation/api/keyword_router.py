"""
FastAPI роутер для модуля Keywords с новой архитектурой
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db_session
from src.keywords.presentation.schemas.keyword_schemas import (
    KeywordCreate,
    KeywordResponse,
    KeywordsListResponse,
    KeywordStats,
    KeywordUpdate,
)
from src.keywords.domain.services.keyword_service import KeywordService
from src.keywords.infrastructure.repositories.keyword_repository import KeywordRepository
from src.keywords.shared.constants import DEFAULT_LIMIT
from src.keywords.shared.exceptions import (
    KeywordNotFoundError,
    KeywordAlreadyExistsError,
    CannotActivateArchivedKeywordError,
    InvalidKeywordDataError,
)


def get_keyword_service(db: AsyncSession = Depends(get_db_session)) -> KeywordService:
    """Получить сервис ключевых слов с зависимостями"""
    repository = KeywordRepository(db)
    return KeywordService(repository)


router = APIRouter(prefix="/keywords", tags=["Keywords Management"])


@router.post("/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword_data: KeywordCreate,
    service: KeywordService = Depends(get_keyword_service),
):
    """Создать ключевое слово"""
    try:
        keyword = await service.create_keyword(
            word=keyword_data.word,
            description=keyword_data.description,
            category=keyword_data.category_name,
            priority=keyword_data.priority,
            group_id=keyword_data.group_id,
        )
        return KeywordResponse.from_orm(keyword)
    except KeywordAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidKeywordDataError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=KeywordsListResponse)
async def get_keywords(
    active_only: bool = Query(True, description="Показывать только активные"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    search: Optional[str] = Query(None, description="Поиск по слову или описанию"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=100, description="Количество элементов"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: KeywordService = Depends(get_keyword_service),
):
    """Получить список ключевых слов с фильтрами"""
    keywords = await service.get_keywords(
        active_only=active_only,
        category=category,
        search=search,
        limit=limit,
        offset=offset,
    )

    # Получаем общее количество для пагинации
    total = await service.repository.count_total()

    return KeywordsListResponse(
        keywords=[KeywordResponse.from_orm(kw) for kw in keywords],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    service: KeywordService = Depends(get_keyword_service),
):
    """Получить ключевое слово по ID"""
    try:
        keyword = await service.get_keyword(keyword_id)
        return KeywordResponse.from_orm(keyword)
    except KeywordNotFoundError:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword_data: KeywordUpdate,
    service: KeywordService = Depends(get_keyword_service),
):
    """Обновить ключевое слово"""
    try:
        success = await service.update_keyword(
            keyword_id=keyword_id,
            word=keyword_data.word,
            description=keyword_data.description,
            category=keyword_data.category_name,
            priority=keyword_data.priority,
            group_id=keyword_data.group_id,
        )
        if not success:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")

        # Получаем обновленное ключевое слово
        keyword = await service.get_keyword(keyword_id)
        return KeywordResponse.from_orm(keyword)
    except KeywordAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidKeywordDataError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: int,
    service: KeywordService = Depends(get_keyword_service),
):
    """Удалить ключевое слово"""
    try:
        success = await service.delete_keyword(keyword_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
    except KeywordNotFoundError:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")


@router.patch("/{keyword_id}/activate", response_model=dict)
async def activate_keyword(
    keyword_id: int,
    service: KeywordService = Depends(get_keyword_service),
):
    """Активировать ключевое слово"""
    try:
        success = await service.activate_keyword(keyword_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
        return {"message": "Ключевое слово активировано"}
    except CannotActivateArchivedKeywordError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{keyword_id}/deactivate", response_model=dict)
async def deactivate_keyword(
    keyword_id: int,
    service: KeywordService = Depends(get_keyword_service),
):
    """Деактивировать ключевое слово"""
    try:
        success = await service.deactivate_keyword(keyword_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
        return {"message": "Ключевое слово деактивировано"}
    except KeywordNotFoundError:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")


@router.patch("/{keyword_id}/archive", response_model=dict)
async def archive_keyword(
    keyword_id: int,
    service: KeywordService = Depends(get_keyword_service),
):
    """Архивировать ключевое слово"""
    try:
        success = await service.archive_keyword(keyword_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
        return {"message": "Ключевое слово архивировано"}
    except KeywordNotFoundError:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")


@router.get("/stats", response_model=KeywordStats)
async def get_keyword_stats(
    service: KeywordService = Depends(get_keyword_service),
):
    """Получить статистику по ключевым словам"""
    return await service.get_keyword_stats()