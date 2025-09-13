"""
FastAPI роутер для модуля Keywords
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.database import get_db_session
from common.exceptions import ValidationError
from keywords.models import KeywordsRepository
from keywords.service import KeywordsService

router = APIRouter(prefix="/keywords", tags=["Keywords Management"])


def get_keywords_service(db: AsyncSession = Depends(get_db_session)) -> KeywordsService:
    """Получить сервис ключевых слов"""
    repository = KeywordsRepository(db)
    return KeywordsService(repository)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_keyword(
    word: str,
    description: str = None,
    category_name: str = None,
    priority: int = 5,
    group_id: int = None,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Создать ключевое слово"""
    try:
        keyword = await service.create_keyword(
            word=word,
            description=description,
            category_name=category_name,
            priority=priority,
            group_id=group_id
        )
        return {
            "id": keyword.id,
            "word": keyword.word,
            "description": keyword.description,
            "category_name": keyword.category_name,
            "priority": keyword.priority,
            "is_active": keyword.is_active,
            "created_at": keyword.created_at
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_keywords(
    active_only: bool = Query(True),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KeywordsService = Depends(get_keywords_service),
):
    """Получить ключевые слова"""
    try:
        keywords = await service.get_keywords(
            active_only=active_only,
            category=category,
            search=search,
            limit=limit,
            offset=offset
        )
        return [
            {
                "id": kw.id,
                "word": kw.word,
                "description": kw.description,
                "category_name": kw.category_name,
                "priority": kw.priority,
                "is_active": kw.is_active,
                "is_archived": kw.is_archived,
                "match_count": kw.match_count,
                "created_at": kw.created_at
            }
            for kw in keywords
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{keyword_id}")
async def get_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Получить ключевое слово по ID"""
    keyword = await service.get_keyword(keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
    
    return {
        "id": keyword.id,
        "word": keyword.word,
        "description": keyword.description,
        "category_name": keyword.category_name,
        "priority": keyword.priority,
        "is_active": keyword.is_active,
        "is_archived": keyword.is_archived,
        "match_count": keyword.match_count,
        "created_at": keyword.created_at
    }


@router.put("/{keyword_id}")
async def update_keyword(
    keyword_id: int,
    word: str = None,
    description: str = None,
    category_name: str = None,
    priority: int = None,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Обновить ключевое слово"""
    try:
        update_data = {}
        if word is not None:
            update_data["word"] = word
        if description is not None:
            update_data["description"] = description
        if category_name is not None:
            update_data["category_name"] = category_name
        if priority is not None:
            update_data["priority"] = priority

        success = await service.update_keyword(keyword_id, **update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
        
        return {"message": "Ключевое слово обновлено"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Удалить ключевое слово"""
    success = await service.delete_keyword(keyword_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")


@router.patch("/{keyword_id}/activate")
async def activate_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Активировать ключевое слово"""
    try:
        success = await service.activate_keyword(keyword_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
        return {"message": "Ключевое слово активировано"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{keyword_id}/deactivate")
async def deactivate_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Деактивировать ключевое слово"""
    success = await service.deactivate_keyword(keyword_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
    return {"message": "Ключевое слово деактивировано"}


@router.patch("/{keyword_id}/archive")
async def archive_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Архивировать ключевое слово"""
    success = await service.archive_keyword(keyword_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ключевое слово не найдено")
    return {"message": "Ключевое слово архивировано"}


@router.get("/metrics")
async def get_keywords_metrics(
    service: KeywordsService = Depends(get_keywords_service)
):
    """Получить метрики ключевых слов"""
    total = await service.get_total_keywords_count()
    active = await service.get_active_keywords_count()
    growth = await service.get_keywords_growth_percentage(30)
    
    return {
        "total_keywords": total,
        "active_keywords": active,
        "growth_percentage": round(growth, 1),
        "trend": "рост с прошлого месяца" if growth > 0 else "снижение с прошлого месяца"
    }
