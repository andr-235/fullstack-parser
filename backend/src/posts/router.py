"""
FastAPI роутер для модуля Posts
"""

from typing import List, Any, Generic, TypeVar
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

T = TypeVar('T')

from .schemas import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostFilter,
    PostListResponse,
    PostStats,
    PostBulkUpdate
)
from .service import PostService
# Простые классы для ответов
class SuccessResponse(BaseModel, Generic[T]):
    data: T
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    error: str
    message: str
    success: bool = False

# Заглушка для get_db_session - должна быть реализована в shared модуле
async def get_db_session():
    # Это должно быть заменено на реальную зависимость
    pass

router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_service(db: AsyncSession = Depends(get_db_session)) -> PostService:
    """Получить сервис постов"""
    return PostService(db)


@router.post(
    "/",
    response_model=SuccessResponse[PostResponse],
    status_code=201,
    summary="Создать пост",
    description="Создает новый пост"
)
async def create_post(
    post_data: PostCreate,
    service: PostService = Depends(get_post_service)
):
    """Создать пост"""
    try:
        post = await service.create_post(post_data)
        return SuccessResponse(
            data=PostResponse.from_orm(post),
            message="Post created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{post_id}",
    response_model=SuccessResponse[PostResponse],
    summary="Получить пост",
    description="Получает пост по ID"
)
async def get_post(
    post_id: int = Path(..., description="ID поста"),
    service: PostService = Depends(get_post_service)
):
    """Получить пост по ID"""
    try:
        post = await service.get_post(post_id)
        return SuccessResponse(
            data=PostResponse.from_orm(post),
            message="Post retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/vk/{vk_id}",
    response_model=SuccessResponse[PostResponse],
    summary="Получить пост по VK ID",
    description="Получает пост по VK ID"
)
async def get_post_by_vk_id(
    vk_id: int = Path(..., description="VK ID поста"),
    service: PostService = Depends(get_post_service)
):
    """Получить пост по VK ID"""
    try:
        post = await service.get_post_by_vk_id(vk_id)
        return SuccessResponse(
            data=PostResponse.from_orm(post),
            message="Post retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/",
    response_model=SuccessResponse[PostListResponse],
    summary="Список постов",
    description="Получает список постов с фильтрацией"
)
async def list_posts(
    group_id: int = Query(None, description="Фильтр по группе"),
    author_id: int = Query(None, description="Фильтр по автору"),
    status: str = Query(None, description="Фильтр по статусу"),
    post_type: str = Query(None, description="Фильтр по типу"),
    search_text: str = Query(None, description="Поиск по тексту"),
    limit: int = Query(50, ge=1, le=1000, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    order_by: str = Query("created_at", description="Поле для сортировки"),
    order_direction: str = Query("desc", description="Направление сортировки"),
    service: PostService = Depends(get_post_service)
):
    """Получить список постов"""
    filters = PostFilter(
        group_id=group_id,
        author_id=author_id,
        status=status,
        post_type=post_type,
        search_text=search_text,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_direction=order_direction
    )
    
    posts, total = await service.list_posts(filters)
    
    return SuccessResponse(
        data=PostListResponse(
            posts=[PostResponse.from_orm(post) for post in posts],
            total=total,
            limit=limit,
            offset=offset
        ),
        message="Posts retrieved successfully"
    )


@router.put(
    "/{post_id}",
    response_model=SuccessResponse[PostResponse],
    summary="Обновить пост",
    description="Обновляет пост"
)
async def update_post(
    post_id: int = Path(..., description="ID поста"),
    update_data: PostUpdate = ...,
    service: PostService = Depends(get_post_service)
):
    """Обновить пост"""
    try:
        post = await service.update_post(post_id, update_data)
        return SuccessResponse(
            data=PostResponse.from_orm(post),
            message="Post updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/{post_id}",
    response_model=SuccessResponse[dict],
    summary="Удалить пост",
    description="Удаляет пост"
)
async def delete_post(
    post_id: int = Path(..., description="ID поста"),
    service: PostService = Depends(get_post_service)
):
    """Удалить пост"""
    success = await service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return SuccessResponse(
        data={"deleted": True},
        message="Post deleted successfully"
    )


@router.post(
    "/upsert",
    response_model=SuccessResponse[PostResponse],
    summary="Создать или обновить пост",
    description="Создает пост или обновляет существующий"
)
async def upsert_post(
    post_data: PostCreate,
    service: PostService = Depends(get_post_service)
):
    """Создать или обновить пост"""
    try:
        post = await service.upsert_post(post_data)
        return SuccessResponse(
            data=PostResponse.from_orm(post),
            message="Post upserted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/stats/overview",
    response_model=SuccessResponse[PostStats],
    summary="Статистика постов",
    description="Получает общую статистику постов"
)
async def get_post_stats(
    service: PostService = Depends(get_post_service)
):
    """Получить статистику постов"""
    stats = await service.get_post_stats()
    return SuccessResponse(
        data=stats,
        message="Stats retrieved successfully"
    )


@router.post(
    "/bulk-update",
    response_model=SuccessResponse[dict],
    summary="Массовое обновление",
    description="Массовое обновление постов"
)
async def bulk_update_posts(
    bulk_data: PostBulkUpdate,
    service: PostService = Depends(get_post_service)
):
    """Массовое обновление постов"""
    try:
        updated_count = await service.bulk_update_posts(bulk_data)
        return SuccessResponse(
            data={"updated_count": updated_count},
            message=f"Updated {updated_count} posts"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/search",
    response_model=SuccessResponse[PostListResponse],
    summary="Поиск постов",
    description="Поиск постов по тексту"
)
async def search_posts(
    q: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(50, ge=1, le=1000, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: PostService = Depends(get_post_service)
):
    """Поиск постов"""
    posts, total = await service.search_posts(q, limit, offset)
    
    return SuccessResponse(
        data=PostListResponse(
            posts=[PostResponse.from_orm(post) for post in posts],
            total=total,
            limit=limit,
            offset=offset
        ),
        message="Search completed successfully"
    )


@router.get(
    "/hashtag/{hashtag}",
    response_model=SuccessResponse[PostListResponse],
    summary="Посты по хештегу",
    description="Получает посты по хештегу"
)
async def get_posts_by_hashtag(
    hashtag: str = Path(..., description="Хештег"),
    limit: int = Query(50, ge=1, le=1000, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: PostService = Depends(get_post_service)
):
    """Получить посты по хештегу"""
    posts, total = await service.get_posts_by_hashtag(hashtag, limit, offset)
    
    return SuccessResponse(
        data=PostListResponse(
            posts=[PostResponse.from_orm(post) for post in posts],
            total=total,
            limit=limit,
            offset=offset
        ),
        message="Posts by hashtag retrieved successfully"
    )


@router.patch(
    "/{post_id}/mark-parsed",
    response_model=SuccessResponse[dict],
    summary="Отметить как распарсенный",
    description="Отмечает пост как распарсенный"
)
async def mark_post_as_parsed(
    post_id: int = Path(..., description="ID поста"),
    service: PostService = Depends(get_post_service)
):
    """Отметить пост как распарсенный"""
    success = await service.mark_as_parsed(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return SuccessResponse(
        data={"marked_as_parsed": True},
        message="Post marked as parsed"
    )


@router.get(
    "/{post_id}/with-comments",
    response_model=SuccessResponse[PostResponse],
    summary="Получить пост с комментариями",
    description="Получает пост по ID вместе с его комментариями"
)
async def get_post_with_comments(
    post_id: int = Path(..., description="ID поста"),
    service: PostService = Depends(get_post_service)
):
    """Получить пост с комментариями"""
    post = await service.get_by_id_with_comments(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return SuccessResponse(
        data=PostResponse.from_orm(post),
        message="Post with comments retrieved successfully"
    )
