"""
API роутер для работы с VK постами
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl
from vk_api.application.dto.vk_api_dto import (
    VKPostDTO,
    VKGetGroupPostsRequestDTO,
    VKPostsResponseDTO
)
from vk_api.presentation.dependencies.vk_api_dependencies import VKAPIServiceDep
from shared.presentation.responses.response_utils import PaginationParams
from shared.presentation.exceptions import (
    NotFoundException as NotFoundError,
    ValidationException as APIValidationError,
    InternalServerException as APIServiceUnavailableError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["VK Posts"])


@router.get(
    "/groups/{group_id}",
    response_model=VKPostsResponseDTO,
    summary="Получить посты группы",
    description="Получить посты VK группы с возможностью фильтрации по датам"
)
async def get_group_posts(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    count: int = Query(default=100, ge=1, le=100, description="Количество постов"),
    offset: int = Query(default=0, ge=0, description="Смещение"),
    start_date: Optional[datetime] = Query(None, description="Дата начала (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Дата окончания (ISO 8601)"),
    vk_service = VKAPIServiceDep
) -> VKPostsResponseDTO:
    """Получить посты группы"""
    try:
        request = VKGetGroupPostsRequestDTO(
            group_id=group_id,
            count=count,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        
        posts = await vk_service.get_group_posts(request)
        
        return VKPostsResponseDTO(
            items=posts,
            total=len(posts),
            page=offset // count + 1,
            size=count,
            pages=(len(posts) + count - 1) // count
        )
        
    except Exception as e:
        logger.error(f"Failed to get group posts: {e}")
        raise APIServiceUnavailableError(f"Failed to get group posts: {e}")


@router.get(
    "/groups/{group_id}/posts/{post_id}",
    response_model=VKPostDTO,
    summary="Получить пост по ID",
    description="Получить конкретный пост VK группы по ID"
)
async def get_post(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    post_id: int = Path(..., gt=0, description="ID поста"),
    vk_service = VKAPIServiceDep
) -> VKPostDTO:
    """Получить пост по ID"""
    try:
        post = await vk_service.get_post(group_id, post_id)
        
        if not post:
            raise NotFoundError(f"Post {post_id} not found in group {group_id}")
        
        return post
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get post {post_id} from group {group_id}: {e}")
        raise APIServiceUnavailableError(f"Failed to get post: {e}")


@router.post(
    "/groups/{group_id}/batch",
    response_model=List[VKPostDTO],
    summary="Получить посты по списку ID",
    description="Получить несколько постов VK группы по списку ID"
)
async def get_posts_by_ids(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    post_ids: List[int] = Query(..., description="Список ID постов"),
    vk_service = VKAPIServiceDep
) -> List[VKPostDTO]:
    """Получить посты по списку ID"""
    try:
        if not post_ids:
            return []
        
        if len(post_ids) > 100:
            raise APIValidationError("Maximum 100 post IDs allowed")
        
        posts = await vk_service.get_posts_by_ids(group_id, post_ids)
        
        return posts
        
    except APIValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to get posts by IDs: {e}")
        raise APIServiceUnavailableError(f"Failed to get posts: {e}")


@router.get(
    "/groups/{group_id}/posts/{post_id}/with-comments",
    response_model=dict,
    summary="Получить пост с комментариями",
    description="Получить пост VK группы с комментариями"
)
async def get_post_with_comments(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    post_id: int = Path(..., gt=0, description="ID поста"),
    comments_count: int = Query(default=50, ge=1, le=100, description="Количество комментариев"),
    vk_service = VKAPIServiceDep
) -> dict:
    """Получить пост с комментариями"""
    try:
        result = await vk_service.get_post_with_comments(group_id, post_id, comments_count)
        
        if not result:
            raise NotFoundError(f"Post {post_id} not found in group {group_id}")
        
        return result.model_dump()
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get post with comments: {e}")
        raise APIServiceUnavailableError(f"Failed to get post with comments: {e}")
