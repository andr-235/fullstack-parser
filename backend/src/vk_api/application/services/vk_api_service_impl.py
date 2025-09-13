"""
Реализация сервиса VK API
"""

import logging
from typing import List, Optional, Dict, Any

from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.services.vk_api_domain_service import VKAPIDomainService
from vk_api.application.interfaces.vk_api_service_interface import VKAPIServiceInterface
from vk_api.application.dto.vk_api_dto import (
    VKGroupDTO,
    VKPostDTO,
    VKCommentDTO,
    VKUserDTO,
    VKGroupWithPostsDTO,
    VKPostWithCommentsDTO,
    VKGroupAnalyticsDTO,
    VKSearchGroupsRequestDTO,
    VKGetGroupPostsRequestDTO,
    VKGetPostCommentsRequestDTO,
)
from shared.presentation.exceptions import InternalServerException as ServiceUnavailableError, ValidationException as ValidationError


logger = logging.getLogger(__name__)


class VKAPIServiceImpl(VKAPIServiceInterface):
    """Реализация сервиса VK API"""
    
    def __init__(self, repository: VKAPIRepositoryInterface):
        self.repository = repository
        self.domain_service = VKAPIDomainService(repository)
    
    # Groups
    async def get_group(self, group_id: int) -> Optional[VKGroupDTO]:
        """Получить группу по ID"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            
            vk_group_id = VKGroupID(group_id)
            group = await self.repository.get_group_by_id(vk_group_id)
            
            if not group:
                return None
            
            return VKGroupDTO.model_validate(group.to_dict())
            
        except ValueError as e:
            raise ValidationError(f"Invalid group ID: {e}")
        except Exception as e:
            logger.error(f"Failed to get group {group_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get group: {e}")
    
    async def search_groups(self, request: VKSearchGroupsRequestDTO) -> List[VKGroupDTO]:
        """Поиск групп"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            
            groups = await self.repository.search_groups(
                query=request.query,
                count=request.count,
                offset=request.offset
            )
            
            return [VKGroupDTO.model_validate(group.to_dict()) for group in groups]
            
        except Exception as e:
            logger.error(f"Failed to search groups: {e}")
            raise ServiceUnavailableError(f"Failed to search groups: {e}")
    
    async def get_groups_by_ids(self, group_ids: List[int]) -> List[VKGroupDTO]:
        """Получить группы по списку ID"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            
            vk_group_ids = [VKGroupID(group_id) for group_id in group_ids]
            groups = await self.repository.get_groups_by_ids(vk_group_ids)
            
            return [VKGroupDTO.model_validate(group.to_dict()) for group in groups]
            
        except ValueError as e:
            raise ValidationError(f"Invalid group IDs: {e}")
        except Exception as e:
            logger.error(f"Failed to get groups by IDs: {e}")
            raise ServiceUnavailableError(f"Failed to get groups: {e}")
    
    # Posts
    async def get_group_posts(self, request: VKGetGroupPostsRequestDTO) -> List[VKPostDTO]:
        """Получить посты группы"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            
            vk_group_id = VKGroupID(request.group_id)
            posts = await self.repository.get_group_posts(
                group_id=vk_group_id,
                count=request.count,
                offset=request.offset,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            return [VKPostDTO.model_validate(post.to_dict()) for post in posts]
            
        except ValueError as e:
            raise ValidationError(f"Invalid group ID: {e}")
        except Exception as e:
            logger.error(f"Failed to get group posts: {e}")
            raise ServiceUnavailableError(f"Failed to get group posts: {e}")
    
    async def get_post(self, group_id: int, post_id: int) -> Optional[VKPostDTO]:
        """Получить пост по ID"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            from ...domain.value_objects.post_id import VKPostID
            
            vk_group_id = VKGroupID(group_id)
            vk_post_id = VKPostID(post_id)
            
            post = await self.repository.get_post_by_id(vk_group_id, vk_post_id)
            
            if not post:
                return None
            
            return VKPostDTO.model_validate(post.to_dict())
            
        except ValueError as e:
            raise ValidationError(f"Invalid IDs: {e}")
        except Exception as e:
            logger.error(f"Failed to get post {post_id} from group {group_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get post: {e}")
    
    async def get_posts_by_ids(self, group_id: int, post_ids: List[int]) -> List[VKPostDTO]:
        """Получить посты по списку ID"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            from ...domain.value_objects.post_id import VKPostID
            
            vk_group_id = VKGroupID(group_id)
            vk_post_ids = [VKPostID(post_id) for post_id in post_ids]
            
            posts = await self.repository.get_posts_by_ids(vk_group_id, vk_post_ids)
            
            return [VKPostDTO.model_validate(post.to_dict()) for post in posts]
            
        except ValueError as e:
            raise ValidationError(f"Invalid IDs: {e}")
        except Exception as e:
            logger.error(f"Failed to get posts by IDs: {e}")
            raise ServiceUnavailableError(f"Failed to get posts: {e}")
    
    # Comments
    async def get_post_comments(self, request: VKGetPostCommentsRequestDTO) -> List[VKCommentDTO]:
        """Получить комментарии к посту"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            from ...domain.value_objects.post_id import VKPostID
            
            vk_group_id = VKGroupID(request.group_id)
            vk_post_id = VKPostID(request.post_id)
            
            comments = await self.repository.get_post_comments(
                group_id=vk_group_id,
                post_id=vk_post_id,
                count=request.count,
                offset=request.offset,
                sort=request.sort,
                thread_items_count=request.thread_items_count
            )
            
            return [VKCommentDTO.model_validate(comment.to_dict()) for comment in comments]
            
        except ValueError as e:
            raise ValidationError(f"Invalid IDs: {e}")
        except Exception as e:
            logger.error(f"Failed to get post comments: {e}")
            raise ServiceUnavailableError(f"Failed to get post comments: {e}")
    
    async def get_comment(self, group_id: int, post_id: int, comment_id: int) -> Optional[VKCommentDTO]:
        """Получить комментарий по ID"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            from ...domain.value_objects.post_id import VKPostID
            
            vk_group_id = VKGroupID(group_id)
            vk_post_id = VKPostID(post_id)
            
            comment = await self.repository.get_comment_by_id(vk_group_id, vk_post_id, comment_id)
            
            if not comment:
                return None
            
            return VKCommentDTO.model_validate(comment.to_dict())
            
        except ValueError as e:
            raise ValidationError(f"Invalid IDs: {e}")
        except Exception as e:
            logger.error(f"Failed to get comment {comment_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get comment: {e}")
    
    # Users
    async def get_user(self, user_id: int) -> Optional[VKUserDTO]:
        """Получить пользователя по ID"""
        try:
            from ...domain.value_objects.user_id import VKUserID
            
            vk_user_id = VKUserID(user_id)
            user_data = await self.repository.get_user_by_id(vk_user_id)
            
            if not user_data:
                return None
            
            return VKUserDTO.model_validate(user_data)
            
        except ValueError as e:
            raise ValidationError(f"Invalid user ID: {e}")
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get user: {e}")
    
    async def get_users_by_ids(self, user_ids: List[int]) -> List[VKUserDTO]:
        """Получить пользователей по списку ID"""
        try:
            from ...domain.value_objects.user_id import VKUserID
            
            vk_user_ids = [VKUserID(user_id) for user_id in user_ids]
            users_data = await self.repository.get_users_by_ids(vk_user_ids)
            
            return [VKUserDTO.model_validate(user_data) for user_data in users_data]
            
        except ValueError as e:
            raise ValidationError(f"Invalid user IDs: {e}")
        except Exception as e:
            logger.error(f"Failed to get users by IDs: {e}")
            raise ServiceUnavailableError(f"Failed to get users: {e}")
    
    # Complex operations
    async def get_group_with_posts(self, group_id: int, posts_count: int = 10) -> Optional[VKGroupWithPostsDTO]:
        """Получить группу с постами"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            
            vk_group_id = VKGroupID(group_id)
            result = await self.domain_service.get_group_with_posts(vk_group_id, posts_count)
            
            if not result:
                return None
            
            return VKGroupWithPostsDTO(
                group=VKGroupDTO.model_validate(result['group'].to_dict()),
                posts=[VKPostDTO.model_validate(post.to_dict()) for post in result['posts']],
                posts_count=result['posts_count']
            )
            
        except ValueError as e:
            raise ValidationError(f"Invalid group ID: {e}")
        except Exception as e:
            logger.error(f"Failed to get group with posts: {e}")
            raise ServiceUnavailableError(f"Failed to get group with posts: {e}")
    
    async def get_post_with_comments(self, group_id: int, post_id: int, comments_count: int = 50) -> Optional[VKPostWithCommentsDTO]:
        """Получить пост с комментариями"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            from ...domain.value_objects.post_id import VKPostID
            
            vk_group_id = VKGroupID(group_id)
            vk_post_id = VKPostID(post_id)
            
            result = await self.domain_service.get_post_with_comments(vk_group_id, vk_post_id, comments_count)
            
            if not result:
                return None
            
            return VKPostWithCommentsDTO(
                post=VKPostDTO.model_validate(result['post'].to_dict()),
                comments=[VKCommentDTO.model_validate(comment.to_dict()) for comment in result['comments']],
                comments_count=result['comments_count']
            )
            
        except ValueError as e:
            raise ValidationError(f"Invalid IDs: {e}")
        except Exception as e:
            logger.error(f"Failed to get post with comments: {e}")
            raise ServiceUnavailableError(f"Failed to get post with comments: {e}")
    
    async def get_group_analytics(self, group_id: int, days: int = 7) -> Optional[VKGroupAnalyticsDTO]:
        """Получить аналитику группы"""
        try:
            from ...domain.value_objects.group_id import VKGroupID
            
            vk_group_id = VKGroupID(group_id)
            result = await self.domain_service.get_group_analytics(vk_group_id, days)
            
            if not result:
                return None
            
            return VKGroupAnalyticsDTO(
                group=VKGroupDTO.model_validate(result['group'].to_dict()),
                period_days=result['period_days'],
                posts_count=result['posts_count'],
                total_likes=result['total_likes'],
                total_reposts=result['total_reposts'],
                total_comments=result['total_comments'],
                avg_engagement=result['avg_engagement']
            )
            
        except ValueError as e:
            raise ValidationError(f"Invalid group ID: {e}")
        except Exception as e:
            logger.error(f"Failed to get group analytics: {e}")
            raise ServiceUnavailableError(f"Failed to get group analytics: {e}")
    
    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья сервиса"""
        try:
            return await self.repository.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
