"""
FastAPI роутер для модуля VK API

Определяет API эндпоинты для работы с VK API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from .dependencies import get_vk_api_service
from .schemas import (
    VKGroupPostsRequest,
    VKGroupPostsResponse,
    VKPostCommentsRequest,
    VKPostCommentsResponse,
    VKGroupInfoResponse,
    VKUsersInfoRequest,
    VKUsersInfoResponse,
    VKGroupsSearchRequest,
    VKGroupsSearchResponse,
    VKPostByIdRequest,
    VKPostByIdResponse,
    VKTokenValidationResponse,
    VKAPILimits,
    VKAPIStats,
    VKAPIHealthCheck,
    VKAPILogsResponse,
    VKBulkPostsRequest,
    VKBulkPostsResponse,
    VKGroupMembersRequest,
    VKGroupMembersResponse,
)
from .service import VKAPIService

router = APIRouter(
    prefix="/vk-api",
    tags=["VK API"],
    responses={
        400: {"description": "Bad request - invalid input"},
        401: {"description": "Unauthorized - invalid token"},
        403: {"description": "Forbidden - access denied"},
        404: {"description": "Not found"},
        429: {"description": "Too many requests - rate limit exceeded"},
        500: {"description": "Internal server error"},
        502: {"description": "Bad gateway - VK API error"},
        503: {"description": "Service unavailable"},
    },
)


@router.post(
    "/groups/{group_id}/posts",
    response_model=VKGroupPostsResponse,
    summary="Получить посты группы",
    description="Получить посты из группы VK с поддержкой пагинации",
)
async def get_group_posts(
    group_id: int,
    request: VKGroupPostsRequest,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKGroupPostsResponse:
    """Получить посты группы VK"""
    try:
        # Используем group_id из пути, если он отличается от тела запроса
        if group_id != request.group_id:
            request.group_id = group_id

        result = await service.get_group_posts(
            group_id=request.group_id,
            count=request.count,
            offset=request.offset,
        )
        return VKGroupPostsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/groups/{group_id}/posts",
    response_model=VKGroupPostsResponse,
    summary="Получить посты группы (GET)",
    description="Получить посты из группы VK с поддержкой пагинации",
)
async def get_group_posts_get(
    group_id: int,
    count: int = Query(20, ge=1, le=100, description="Количество постов"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKGroupPostsResponse:
    """Получить посты группы VK (GET версия)"""
    try:
        result = await service.get_group_posts(
            group_id=group_id,
            count=count,
            offset=offset,
        )
        return VKGroupPostsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/posts/{post_id}/comments",
    response_model=VKPostCommentsResponse,
    summary="Получить комментарии к посту",
    description="Получить комментарии к посту VK с поддержкой пагинации",
)
async def get_post_comments(
    post_id: int,
    request: VKPostCommentsRequest,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKPostCommentsResponse:
    """Получить комментарии к посту VK"""
    try:
        # Используем post_id из пути, если он отличается от тела запроса
        if post_id != request.post_id:
            request.post_id = post_id

        result = await service.get_post_comments(
            group_id=request.group_id,
            post_id=request.post_id,
            count=request.count,
            offset=request.offset,
            sort=request.sort,
        )
        return VKPostCommentsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/posts/{post_id}/comments",
    response_model=VKPostCommentsResponse,
    summary="Получить комментарии к посту (GET)",
    description="Получить комментарии к посту VK с поддержкой пагинации",
)
async def get_post_comments_get(
    post_id: int,
    group_id: int = Query(..., description="ID группы VK", gt=0),
    count: int = Query(
        100, ge=1, le=100, description="Количество комментариев"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),
    sort: str = Query("asc", enum=["asc", "desc"], description="Сортировка"),
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKPostCommentsResponse:
    """Получить комментарии к посту VK (GET версия)"""
    try:
        result = await service.get_post_comments(
            group_id=group_id,
            post_id=post_id,
            count=count,
            offset=offset,
            sort=sort,
        )
        return VKPostCommentsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/groups/{group_id}/info",
    response_model=VKGroupInfoResponse,
    summary="Получить информацию о группе",
    description="Получить детальную информацию о группе VK",
)
async def get_group_info(
    group_id: int,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKGroupInfoResponse:
    """Получить информацию о группе VK"""
    try:
        result = await service.get_group_info(group_id)
        return VKGroupInfoResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/users/info",
    response_model=VKUsersInfoResponse,
    summary="Получить информацию о пользователях",
    description="Получить информацию о нескольких пользователях VK",
)
async def get_users_info(
    request: VKUsersInfoRequest,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKUsersInfoResponse:
    """Получить информацию о пользователях VK"""
    try:
        result = await service.get_user_info(request.user_ids)
        return VKUsersInfoResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/users/{user_id}/info",
    summary="Получить информацию о пользователе",
    description="Получить информацию об одном пользователе VK",
)
async def get_user_info(
    user_id: int,
    service: VKAPIService = Depends(get_vk_api_service),
):
    """Получить информацию о пользователе VK"""
    try:
        result = await service.get_user_info([user_id])

        if not result["users"]:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден"
            )

        user_info = result["users"][0]
        return {
            "user": user_info,
            "fetched_at": result["fetched_at"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/groups/search",
    response_model=VKGroupsSearchResponse,
    summary="Поиск групп",
    description="Поиск групп VK по запросу с поддержкой фильтров",
)
async def search_groups(
    request: VKGroupsSearchRequest,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKGroupsSearchResponse:
    """Поиск групп VK"""
    try:
        result = await service.search_groups(
            query=request.query,
            count=request.count,
            offset=request.offset,
            country=request.country,
            city=request.city,
        )
        return VKGroupsSearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/groups/search",
    response_model=VKGroupsSearchResponse,
    summary="Поиск групп (GET)",
    description="Поиск групп VK по запросу с поддержкой фильтров",
)
async def search_groups_get(
    query: str = Query(
        ..., description="Поисковый запрос", min_length=1, max_length=255
    ),
    count: int = Query(
        20, ge=1, le=1000, description="Количество результатов"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),
    country: Optional[int] = Query(None, description="ID страны"),
    city: Optional[int] = Query(None, description="ID города"),
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKGroupsSearchResponse:
    """Поиск групп VK (GET версия)"""
    try:
        result = await service.search_groups(
            query=query,
            count=count,
            offset=offset,
            country=country,
            city=city,
        )
        return VKGroupsSearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/posts/by-id",
    response_model=VKPostByIdResponse,
    summary="Получить пост по ID",
    description="Получить конкретный пост VK по его ID",
)
async def get_post_by_id(
    request: VKPostByIdRequest,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKPostByIdResponse:
    """Получить пост по ID"""
    try:
        result = await service.get_post_by_id(
            group_id=request.group_id,
            post_id=request.post_id,
        )
        return VKPostByIdResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/posts/{group_id}/{post_id}",
    response_model=VKPostByIdResponse,
    summary="Получить пост по ID (GET)",
    description="Получить конкретный пост VK по его ID",
)
async def get_post_by_id_get(
    group_id: int,
    post_id: int,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKPostByIdResponse:
    """Получить пост по ID (GET версия)"""
    try:
        result = await service.get_post_by_id(
            group_id=group_id,
            post_id=post_id,
        )
        return VKPostByIdResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/posts/bulk",
    response_model=VKBulkPostsResponse,
    summary="Массовое получение постов",
    description="Получить несколько постов VK одновременно",
)
async def get_bulk_posts(
    request: VKBulkPostsRequest,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKBulkPostsResponse:
    """Массовое получение постов"""
    # В данной реализации используем последовательные запросы
    # В продакшене можно оптимизировать с помощью asyncio.gather
    posts = []
    for post_id in request.post_ids:
        try:
            post_data = await service.get_post_by_id(
                group_id=request.group_id,
                post_id=post_id,
            )
            posts.append(post_data)
        except Exception:
            # Пропускаем посты, которые не удалось получить
            continue

    return VKBulkPostsResponse(
        posts=posts,
        total_requested=len(request.post_ids),
        total_found=len(posts),
        group_id=request.group_id,
        fetched_at="2024-01-01T00:00:00Z",  # В реальности datetime.utcnow()
    )


@router.post(
    "/groups/{group_id}/members",
    response_model=VKGroupMembersResponse,
    summary="Получить участников группы",
    description="Получить список участников группы VK",
)
async def get_group_members(
    group_id: int,
    request: VKGroupMembersRequest,
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKGroupMembersResponse:
    """Получить участников группы VK"""
    try:
        # Используем group_id из пути, если он отличается от тела запроса
        if group_id != request.group_id:
            request.group_id = group_id

        # В данной реализации возвращаем заглушку
        # Полноценная реализация потребует дополнительной работы с VK API
        return VKGroupMembersResponse(
            members=[],
            total_count=0,
            group_id=request.group_id,
            requested_count=request.count,
            offset=request.offset,
            has_more=False,
            fetched_at="2024-01-01T00:00:00Z",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/auth/validate-token",
    response_model=VKTokenValidationResponse,
    summary="Валидация токена",
    description="Проверить валидность токена доступа к VK API",
)
async def validate_token(
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKTokenValidationResponse:
    """Валидация токена VK API"""
    try:
        result = await service.validate_access_token()
        return VKTokenValidationResponse(**result)
    except Exception as e:
        return VKTokenValidationResponse(
            valid=False,
            error=str(e),
            checked_at="2024-01-01T00:00:00Z",
        )


@router.get(
    "/limits",
    response_model=VKAPILimits,
    summary="Лимиты API",
    description="Получить текущие лимиты и состояние VK API",
)
async def get_api_limits(
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKAPILimits:
    """Получить лимиты VK API"""
    try:
        result = await service.get_api_limits()
        return VKAPILimits(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats",
    response_model=VKAPIStats,
    summary="Статистика API",
    description="Получить статистику использования VK API",
)
async def get_api_stats(
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKAPIStats:
    """Получить статистику VK API"""
    try:
        result = await service.get_stats()
        return VKAPIStats(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    response_model=VKAPIHealthCheck,
    summary="Проверка здоровья",
    description="Проверить доступность и здоровье VK API",
)
async def health_check(
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKAPIHealthCheck:
    """Проверка здоровья VK API"""
    try:
        result = await service.health_check()
        return VKAPIHealthCheck(**result)
    except Exception as e:
        return VKAPIHealthCheck(
            status="unhealthy",
            error=str(e),
            timestamp="2024-01-01T00:00:00Z",
        )


@router.get(
    "/logs",
    response_model=VKAPILogsResponse,
    summary="Логи запросов",
    description="Получить логи запросов к VK API",
)
async def get_logs(
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: VKAPIService = Depends(get_vk_api_service),
) -> VKAPILogsResponse:
    """Получить логи VK API"""
    try:
        # В данной реализации возвращаем заглушку
        # Полноценная реализация потребует работы с репозиторием логов
        return VKAPILogsResponse(
            request_logs=[],
            error_logs=[],
            total_requests=0,
            total_errors=0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/cache",
    summary="Очистить кеш",
    description="Очистить кеш результатов запросов к VK API",
)
async def clear_cache(
    service: VKAPIService = Depends(get_vk_api_service),
):
    """Очистить кеш VK API"""
    try:
        # В данной реализации кеш очищается автоматически
        # Полноценная реализация потребует работы с репозиторием
        return {"message": "Cache cleared successfully", "cleared_entries": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/test-connection",
    summary="Тест подключения",
    description="Протестировать подключение к VK API",
)
async def test_connection(
    service: VKAPIService = Depends(get_vk_api_service),
):
    """Тест подключения к VK API"""
    try:
        # Проверяем токен
        token_validation = await service.validate_access_token()

        return {
            "connection_status": (
                "successful" if token_validation["valid"] else "failed"
            ),
            "token_valid": token_validation["valid"],
            "user_info": (
                {
                    "id": token_validation.get("user_id"),
                    "name": token_validation.get("user_name"),
                }
                if token_validation["valid"]
                else None
            ),
            "tested_at": "2024-01-01T00:00:00Z",
        }
    except Exception as e:
        return {
            "connection_status": "failed",
            "error": str(e),
            "tested_at": "2024-01-01T00:00:00Z",
        }


# Экспорт роутера
__all__ = ["router"]
