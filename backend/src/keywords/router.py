"""
FastAPI роутер для модуля Keywords

Определяет API эндпоинты для управления ключевыми словами
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from .dependencies import get_keywords_service
from .schemas import (
    KeywordCreate,
    KeywordUpdate,
    KeywordResponse,
    KeywordsListResponse,
    KeywordsSearchRequest,
    KeywordsFilterRequest,
    KeywordBulkAction,
    KeywordBulkCreate,
    KeywordBulkResponse,
    KeywordStats,
    KeywordCategoriesResponse,
    KeywordImportRequest,
    KeywordExportRequest,
    KeywordExportResponse,
    KeywordValidationRequest,
    KeywordValidationResponse,
)
from .service import KeywordsService

router = APIRouter(
    prefix="/keywords",
    tags=["Keywords Management"],
    responses={
        400: {"description": "Bad request - invalid input"},
        404: {"description": "Keyword not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/",
    response_model=KeywordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать ключевое слово",
    description="Создать новое ключевое слово с категорией и описанием",
)
async def create_keyword(
    request: KeywordCreate,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordResponse:
    """Создать ключевое слово"""
    try:
        keyword_data = request.model_dump()
        keyword = await service.create_keyword(keyword_data)
        return KeywordResponse(**keyword)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=KeywordsListResponse,
    summary="Получить ключевые слова",
    description="Получить список ключевых слов с фильтрацией и пагинацией",
)
async def get_keywords(
    active_only: bool = Query(
        True, description="Только активные ключевые слова"
    ),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordsListResponse:
    """Получить ключевые слова с фильтрами"""
    try:
        # Преобразуем page/size в limit/offset
        limit = size
        offset = (page - 1) * size

        result = await service.get_keywords(
            active_only=active_only,
            category=category,
            search=search,
            limit=limit,
            offset=offset,
        )
        return KeywordsListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{keyword_id}",
    response_model=KeywordResponse,
    summary="Получить ключевое слово",
    description="Получить ключевое слово по ID",
)
async def get_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordResponse:
    """Получить ключевое слово по ID"""
    try:
        keyword = await service.get_keyword(keyword_id)
        if not keyword:
            raise HTTPException(
                status_code=404, detail="Ключевое слово не найдено"
            )
        return KeywordResponse(**keyword)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{keyword_id}",
    response_model=KeywordResponse,
    summary="Обновить ключевое слово",
    description="Обновить данные ключевого слова",
)
async def update_keyword(
    keyword_id: int,
    request: KeywordUpdate,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordResponse:
    """Обновить ключевое слово"""
    try:
        update_data = request.model_dump(exclude_unset=True)
        keyword = await service.update_keyword(keyword_id, update_data)
        if not keyword:
            raise HTTPException(
                status_code=404, detail="Ключевое слово не найдено"
            )
        return KeywordResponse(**keyword)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{keyword_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ключевое слово",
    description="Удалить ключевое слово (только неактивные)",
)
async def delete_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
):
    """Удалить ключевое слово"""
    try:
        success = await service.delete_keyword(keyword_id)
        if not success:
            raise HTTPException(
                status_code=404, detail="Ключевое слово не найдено"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{keyword_id}/activate",
    response_model=KeywordResponse,
    summary="Активировать ключевое слово",
    description="Активировать ключевое слово для поиска",
)
async def activate_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordResponse:
    """Активировать ключевое слово"""
    try:
        keyword = await service.activate_keyword(keyword_id)
        if not keyword:
            raise HTTPException(
                status_code=404, detail="Ключевое слово не найдено"
            )
        return KeywordResponse(**keyword)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{keyword_id}/deactivate",
    response_model=KeywordResponse,
    summary="Деактивировать ключевое слово",
    description="Деактивировать ключевое слово",
)
async def deactivate_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordResponse:
    """Деактивировать ключевое слово"""
    try:
        keyword = await service.deactivate_keyword(keyword_id)
        if not keyword:
            raise HTTPException(
                status_code=404, detail="Ключевое слово не найдено"
            )
        return KeywordResponse(**keyword)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/{keyword_id}/archive",
    response_model=KeywordResponse,
    summary="Архивировать ключевое слово",
    description="Архивировать ключевое слово",
)
async def archive_keyword(
    keyword_id: int,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordResponse:
    """Архивировать ключевое слово"""
    try:
        keyword = await service.archive_keyword(keyword_id)
        if not keyword:
            raise HTTPException(
                status_code=404, detail="Ключевое слово не найдено"
            )
        return KeywordResponse(**keyword)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/search",
    response_model=KeywordsListResponse,
    summary="Поиск ключевых слов",
    description="Поиск ключевых слов по запросу",
)
async def search_keywords(
    request: KeywordsSearchRequest,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordsListResponse:
    """Поиск ключевых слов"""
    try:
        keywords = await service.search_keywords(
            query=request.query,
            active_only=request.active_only,
            category=request.category,
            limit=request.limit,
            offset=request.offset,
        )
        # Собираем поля согласно PaginatedResponse: items, total, page, size, pages
        total = len(keywords)
        size = request.limit
        page = (request.offset // size) + 1 if size > 0 else 1
        pages = (total + size - 1) // size if size > 0 else 0
        return KeywordsListResponse(
            items=keywords,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/filter",
    response_model=KeywordsListResponse,
    summary="Фильтрация ключевых слов",
    description="Расширенная фильтрация ключевых слов",
)
async def filter_keywords(
    request: KeywordsFilterRequest,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordsListResponse:
    """Фильтрация ключевых слов"""
    try:
        result = await service.get_keywords(
            active_only=request.active_only,
            category=request.category,
            limit=request.limit,
            offset=request.offset,
            priority_min=request.priority_min,
            priority_max=request.priority_max,
            match_count_min=request.match_count_min,
            match_count_max=request.match_count_max,
        )
        return KeywordsListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/bulk-create",
    response_model=KeywordBulkResponse,
    summary="Массовое создание",
    description="Создать несколько ключевых слов одновременно",
)
async def bulk_create_keywords(
    request: KeywordBulkCreate,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordBulkResponse:
    """Массовая загрузка ключевых слов"""
    try:
        keywords_data = [kw.model_dump() for kw in request.keywords]
        result = await service.bulk_create_keywords(keywords_data)
        return KeywordBulkResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/bulk-action",
    response_model=KeywordBulkResponse,
    summary="Массовые действия",
    description="Выполнить действие над несколькими ключевыми словами",
)
async def bulk_action_keywords(
    request: KeywordBulkAction,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordBulkResponse:
    """Массовая операция с ключевыми словами"""
    try:
        result = await service.bulk_action(request.keyword_ids, request.action)
        return KeywordBulkResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/categories/list",
    summary="Список категорий",
    description="Получить список всех категорий ключевых слов",
)
async def get_categories(
    service: KeywordsService = Depends(get_keywords_service),
) -> dict:
    """Получить список категорий"""
    try:
        categories = await service.get_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/categories/stats",
    response_model=KeywordCategoriesResponse,
    summary="Статистика категорий",
    description="Получить категории со статистикой",
)
async def get_categories_with_stats(
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordCategoriesResponse:
    """Получить категории со статистикой"""
    try:
        categories = await service.get_categories()
        categories_with_stats = await service.get_categories_with_stats()
        return KeywordCategoriesResponse(
            categories=categories, categories_with_stats=categories_with_stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats",
    response_model=KeywordStats,
    summary="Статистика ключевых слов",
    description="Получить общую статистику по ключевым словам",
)
async def get_keywords_stats(
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordStats:
    """Получить статистику"""
    try:
        stats = await service.get_stats()
        return KeywordStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/export",
    response_model=KeywordExportResponse,
    summary="Экспорт ключевых слов",
    description="Экспортировать ключевые слова в различных форматах",
)
async def export_keywords(
    request: KeywordExportRequest,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordExportResponse:
    """Экспорт ключевых слов"""
    try:
        result = await service.export_keywords(
            format_type=request.format,
            active_only=request.active_only,
            category=request.category,
        )
        return KeywordExportResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/import",
    summary="Импорт ключевых слов",
    description="Импортировать ключевые слова из JSON",
)
async def import_keywords(
    request: KeywordImportRequest,
    service: KeywordsService = Depends(get_keywords_service),
) -> dict:
    """Импорт ключевых слов"""
    try:
        result = await service.import_keywords(
            import_data=request.keywords_data,
            update_existing=request.update_existing,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/validate",
    response_model=KeywordValidationResponse,
    summary="Валидация слов",
    description="Проверить список слов на пригодность для использования в качестве ключевых слов",
)
async def validate_keywords(
    request: KeywordValidationRequest,
    service: KeywordsService = Depends(get_keywords_service),
) -> KeywordValidationResponse:
    """Валидация слов"""
    try:
        result = await service.validate_keywords(request.words)
        return KeywordValidationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/health",
    summary="Проверка здоровья",
    description="Проверить доступность сервиса ключевых слов",
)
async def keywords_health_check(
    service: KeywordsService = Depends(get_keywords_service),
):
    """Проверка здоровья модуля"""
    try:
        stats = await service.get_stats()
        return {
            "status": "healthy",
            "total_keywords": stats["total_keywords"],
            "active_keywords": stats["active_keywords"],
            "categories_count": stats["total_categories"],
            "timestamp": "2024-01-01T00:00:00Z",  # В реальности datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z",
        }


# Экспорт роутера
__all__ = ["router"]
