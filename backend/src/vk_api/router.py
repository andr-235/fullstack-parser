"""
API роутер для VK API
"""

from typing import List, Optional

from .service import VKAPIService
from .schemas import (
    VKSearchGroupsRequest,
    VKGetGroupPostsRequest,
    VKGetPostCommentsRequest,
    VKGroupResponse,
    VKPostResponse,
    VKCommentResponse,
    VKUserResponse
)


def get_vk_service() -> VKAPIService:
    """Получить сервис VK API"""
    return VKAPIService()


# Для совместимости с FastAPI
try:
    from fastapi import APIRouter, Depends
    
    router = APIRouter(prefix="/vk-api", tags=["VK API"])
    
    @router.get("/groups/{group_id}", response_model=VKGroupResponse)
    async def get_group(group_id: int, vk_service: VKAPIService = Depends(get_vk_service)):
        """Получить группу по ID"""
        try:
            group = await vk_service.get_group(group_id)
            if group:
                return VKGroupResponse(group=group.model_dump())
            else:
                return VKGroupResponse(error="Group not found")
        except Exception as e:
            return VKGroupResponse(error=str(e))
    
    @router.post("/groups/search", response_model=VKPostResponse)
    async def search_groups(request: VKSearchGroupsRequest, vk_service: VKAPIService = Depends(get_vk_service)):
        """Поиск групп"""
        try:
            groups = await vk_service.search_groups(request)
            return VKPostResponse(posts=[group.model_dump() for group in groups])
        except Exception as e:
            return VKPostResponse(error=str(e))
    
    @router.post("/groups/{group_id}/posts", response_model=VKPostResponse)
    async def get_group_posts(group_id: int, request: VKGetGroupPostsRequest, vk_service: VKAPIService = Depends(get_vk_service)):
        """Получить посты группы"""
        try:
            request.group_id = group_id
            posts = await vk_service.get_group_posts(request)
            return VKPostResponse(posts=[post.model_dump() for post in posts])
        except Exception as e:
            return VKPostResponse(error=str(e))
    
    @router.post("/groups/{group_id}/posts/{post_id}/comments", response_model=VKCommentResponse)
    async def get_post_comments(group_id: int, post_id: int, request: VKGetPostCommentsRequest, vk_service: VKAPIService = Depends(get_vk_service)):
        """Получить комментарии к посту"""
        try:
            request.group_id = group_id
            request.post_id = post_id
            comments = await vk_service.get_post_comments(request)
            return VKCommentResponse(comments=[comment.model_dump() for comment in comments])
        except Exception as e:
            return VKCommentResponse(error=str(e))
    
    @router.get("/users/{user_id}", response_model=VKUserResponse)
    async def get_user(user_id: int, vk_service: VKAPIService = Depends(get_vk_service)):
        """Получить пользователя по ID"""
        try:
            user = await vk_service.get_user(user_id)
            if user:
                return VKUserResponse(user=user.model_dump())
            else:
                return VKUserResponse(error="User not found")
        except Exception as e:
            return VKUserResponse(error=str(e))

except ImportError:
    router = None

__all__ = ["router", "get_vk_service"]
