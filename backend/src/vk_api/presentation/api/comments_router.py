"""
API роутер для работы с VK комментариями
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl
from vk_api.application.dto.vk_api_dto import (
    VKCommentDTO,
    VKGetPostCommentsRequestDTO,
    VKCommentsResponseDTO
)
from vk_api.presentation.dependencies.vk_api_dependencies import VKAPIServiceDep
from shared.presentation.responses.response_utils import PaginationParams
from shared.presentation.exceptions import (
    NotFoundException as NotFoundError,
    ValidationException as APIValidationError,
    InternalServerException as APIServiceUnavailableError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comments", tags=["VK Comments"])


@router.get(
    "/groups/{group_id}/posts/{post_id}",
    response_model=VKCommentsResponseDTO,
    summary="Получить комментарии к посту",
    description="Получить комментарии к посту VK группы"
)
async def get_post_comments(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    post_id: int = Path(..., gt=0, description="ID поста"),
    count: int = Query(default=100, ge=1, le=100, description="Количество комментариев"),
    offset: int = Query(default=0, ge=0, description="Смещение"),
    sort: str = Query(default="asc", description="Порядок сортировки (asc/desc)"),
    thread_items_count: int = Query(default=0, ge=0, description="Количество элементов в треде"),
    vk_service: VKAPIServiceImpl = VKAPIServiceDep
) -> VKCommentsResponseDTO:
    """Получить комментарии к посту"""
    try:
        if sort not in ["asc", "desc"]:
            raise APIValidationError("Sort must be 'asc' or 'desc'")
        
        request = VKGetPostCommentsRequestDTO(
            group_id=group_id,
            post_id=post_id,
            count=count,
            offset=offset,
            sort=sort,
            thread_items_count=thread_items_count
        )
        
        comments = await vk_service.get_post_comments(request)
        
        return VKCommentsResponseDTO(
            items=comments,
            total=len(comments),
            page=offset // count + 1,
            size=count,
            pages=(len(comments) + count - 1) // count
        )
        
    except APIValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to get post comments: {e}")
        raise APIServiceUnavailableError(f"Failed to get post comments: {e}")


@router.get(
    "/groups/{group_id}/posts/{post_id}/comments/{comment_id}",
    response_model=VKCommentDTO,
    summary="Получить комментарий по ID",
    description="Получить конкретный комментарий к посту VK группы по ID"
)
async def get_comment(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    post_id: int = Path(..., gt=0, description="ID поста"),
    comment_id: int = Path(..., gt=0, description="ID комментария"),
    vk_service: VKAPIServiceImpl = VKAPIServiceDep
) -> VKCommentDTO:
    """Получить комментарий по ID"""
    try:
        comment = await vk_service.get_comment(group_id, post_id, comment_id)
        
        if not comment:
            raise NotFoundError(f"Comment {comment_id} not found in post {post_id} of group {group_id}")
        
        return comment
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get comment {comment_id}: {e}")
        raise APIServiceUnavailableError(f"Failed to get comment: {e}")
