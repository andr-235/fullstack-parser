"""
FastAPI роутеры для модуля авторов

REST API эндпоинты с современной архитектурой
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
import logging

from ..application.services import AuthorService
from ..domain.entities import AuthorEntity
from ..domain.exceptions import AuthorNotFoundError, AuthorValidationError, AuthorAlreadyExistsError
from ..schemas import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    AuthorListResponse,
    AuthorUpsertRequest,
    AuthorGetOrCreateRequest
)
from ..dependencies import get_author_service_dependency

logger = logging.getLogger(__name__)

authors_router = APIRouter(
    prefix="/authors",
    tags=["authors"],
    responses={
        404: {"description": "Author not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@authors_router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать автора",
    description="Создать нового автора VK"
)
async def create_author(
    author_data: AuthorCreate,
    service: AuthorService = Depends(get_author_service_dependency)
) -> AuthorResponse:
    """Создать нового автора."""
    try:
        author = await service.create_author(author_data.model_dump())
        return AuthorResponse.model_validate(author.to_dict())
    except AuthorAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Автор с VK ID {e.vk_id} уже существует"
        )
    except AuthorValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error creating author: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка создания автора"
        )


@authors_router.get(
    "/{vk_id}",
    response_model=AuthorResponse,
    summary="Получить автора",
    description="Получить автора по VK ID"
)
async def get_author(
    vk_id: int,
    service: AuthorService = Depends(get_author_service_dependency)
) -> AuthorResponse:
    """Получить автора по VK ID."""
    try:
        author = await service.get_author(vk_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Автор с VK ID {vk_id} не найден"
            )
        return AuthorResponse.model_validate(author.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting author {vk_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения автора"
        )


@authors_router.put(
    "/{vk_id}",
    response_model=AuthorResponse,
    summary="Обновить автора",
    description="Обновить данные автора"
)
async def update_author(
    vk_id: int,
    update_data: AuthorUpdate,
    service: AuthorService = Depends(get_author_service_dependency)
) -> AuthorResponse:
    """Обновить автора."""
    try:
        # Фильтруем None значения
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Нет данных для обновления"
            )

        author = await service.update_author(vk_id, update_dict)
        return AuthorResponse.model_validate(author.to_dict())
    except AuthorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Автор с VK ID {e.vk_id} не найден"
        )
    except AuthorValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating author {vk_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления автора"
        )


@authors_router.delete(
    "/{vk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить автора",
    description="Удалить автора по VK ID"
)
async def delete_author(
    vk_id: int,
    service: AuthorService = Depends(get_author_service_dependency)
) -> None:
    """Удалить автора."""
    try:
        deleted = await service.delete_author(vk_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Автор с VK ID {vk_id} не найден"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting author {vk_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка удаления автора"
        )


@authors_router.get(
    "/",
    response_model=AuthorListResponse,
    summary="Список авторов",
    description="Получить список авторов с пагинацией"
)
async def list_authors(
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: AuthorService = Depends(get_author_service_dependency)
) -> AuthorListResponse:
    """Получить список авторов."""
    try:
        authors = await service.list_authors(limit, offset)
        total = await service.get_authors_count()
        
        return AuthorListResponse(
            authors=[AuthorResponse.model_validate(author.to_dict()) for author in authors],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error listing authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения списка авторов"
        )


@authors_router.post(
    "/upsert",
    response_model=AuthorResponse,
    summary="Upsert автора",
    description="Создать или обновить автора"
)
async def upsert_author(
    author_data: AuthorUpsertRequest,
    service: AuthorService = Depends(get_author_service_dependency)
) -> AuthorResponse:
    """Создать или обновить автора."""
    try:
        author = await service.upsert_author(author_data.model_dump())
        return AuthorResponse.model_validate(author.to_dict())
    except AuthorValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error upserting author: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка upsert автора"
        )


@authors_router.post(
    "/get-or-create",
    response_model=AuthorResponse,
    summary="Получить или создать автора",
    description="Получить автора или создать его, если не существует"
)
async def get_or_create_author(
    request: AuthorGetOrCreateRequest,
    service: AuthorService = Depends(get_author_service_dependency)
) -> AuthorResponse:
    """Получить автора или создать его, если не существует."""
    try:
        author = await service.get_or_create_author(
            vk_id=request.vk_id,
            author_name=request.author_name,
            author_screen_name=request.author_screen_name,
            author_photo_url=request.author_photo_url,
        )
        return AuthorResponse.model_validate(author.to_dict())
    except AuthorValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error getting or creating author: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения или создания автора"
        )


@authors_router.get(
    "/search",
    response_model=List[AuthorResponse],
    summary="Поиск авторов",
    description="Поиск авторов по имени или screen_name"
)
async def search_authors(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    service: AuthorService = Depends(get_author_service_dependency)
) -> List[AuthorResponse]:
    """Поиск авторов."""
    try:
        authors = await service.search_authors(q, limit)
        return [AuthorResponse.model_validate(author.to_dict()) for author in authors]
    except Exception as e:
        logger.error(f"Error searching authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка поиска авторов"
        )


@authors_router.post(
    "/bulk",
    response_model=List[AuthorResponse],
    summary="Массовое создание авторов",
    description="Создать несколько авторов за один запрос"
)
async def bulk_create_authors(
    authors_data: List[AuthorCreate],
    service: AuthorService = Depends(get_author_service_dependency)
) -> List[AuthorResponse]:
    """Массовое создание авторов."""
    try:
        if len(authors_data) > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Максимум 100 авторов за один запрос"
            )

        authors = await service.bulk_create_authors([data.model_dump() for data in authors_data])
        return [AuthorResponse.model_validate(author.to_dict()) for author in authors]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk creating authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка массового создания авторов"
        )


@authors_router.get(
    "/{vk_id}/comments-count",
    response_model=dict,
    summary="Количество комментариев автора",
    description="Получить количество комментариев конкретного автора"
)
async def get_author_comments_count(
    vk_id: int,
    service: AuthorService = Depends(get_author_service_dependency)
) -> dict:
    """Получить количество комментариев автора."""
    try:
        # Проверяем существование автора
        author = await service.get_author(vk_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Автор с VK ID {vk_id} не найден"
            )

        comments_count = await service.get_author_comments_count(vk_id)
        return {
            "vk_id": vk_id,
            "author_name": author.display_name,
            "comments_count": comments_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comments count for author {vk_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения количества комментариев"
        )


@authors_router.get(
    "/top-by-comments",
    response_model=List[AuthorResponse],
    summary="Топ авторов по комментариям",
    description="Получить авторов с наибольшим количеством комментариев"
)
async def get_top_authors_by_comments(
    limit: int = Query(10, ge=1, le=100, description="Количество авторов"),
    min_comments: int = Query(1, ge=0, description="Минимальное количество комментариев"),
    service: AuthorService = Depends(get_author_service_dependency)
) -> List[AuthorResponse]:
    """Получить топ авторов по количеству комментариев."""
    try:
        authors = await service.get_top_authors_by_comments(limit, min_comments)
        return [AuthorResponse.model_validate(author.to_dict()) for author in authors]
    except Exception as e:
        logger.error(f"Error getting top authors by comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения топ авторов"
        )


@authors_router.get(
    "/with-comments-stats",
    response_model=AuthorListResponse,
    summary="Авторы со статистикой комментариев",
    description="Получить авторов с фильтрацией по количеству комментариев"
)
async def get_authors_with_comments_stats(
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    min_comments: int = Query(0, ge=0, description="Минимальное количество комментариев"),
    service: AuthorService = Depends(get_author_service_dependency)
) -> AuthorListResponse:
    """Получить авторов со статистикой комментариев."""
    try:
        authors = await service.get_authors_with_comments_stats(limit, offset, min_comments)
        total = await service.get_authors_count()
        
        return AuthorListResponse(
            authors=[AuthorResponse.model_validate(author.to_dict()) for author in authors],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error getting authors with comments stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения авторов со статистикой"
        )
