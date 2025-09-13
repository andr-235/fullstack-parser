"""
Интерфейс сервиса VK API для application layer
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

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


class VKAPIServiceInterface(ABC):
    """Интерфейс сервиса VK API"""
    
    # Groups
    @abstractmethod
    async def get_group(self, group_id: int) -> Optional[VKGroupDTO]:
        """Получить группу по ID"""
        pass
    
    @abstractmethod
    async def search_groups(self, request: VKSearchGroupsRequestDTO) -> List[VKGroupDTO]:
        """Поиск групп"""
        pass
    
    @abstractmethod
    async def get_groups_by_ids(self, group_ids: List[int]) -> List[VKGroupDTO]:
        """Получить группы по списку ID"""
        pass
    
    # Posts
    @abstractmethod
    async def get_group_posts(self, request: VKGetGroupPostsRequestDTO) -> List[VKPostDTO]:
        """Получить посты группы"""
        pass
    
    @abstractmethod
    async def get_post(self, group_id: int, post_id: int) -> Optional[VKPostDTO]:
        """Получить пост по ID"""
        pass
    
    @abstractmethod
    async def get_posts_by_ids(self, group_id: int, post_ids: List[int]) -> List[VKPostDTO]:
        """Получить посты по списку ID"""
        pass
    
    # Comments
    @abstractmethod
    async def get_post_comments(self, request: VKGetPostCommentsRequestDTO) -> List[VKCommentDTO]:
        """Получить комментарии к посту"""
        pass
    
    @abstractmethod
    async def get_comment(self, group_id: int, post_id: int, comment_id: int) -> Optional[VKCommentDTO]:
        """Получить комментарий по ID"""
        pass
    
    # Users
    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[VKUserDTO]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_users_by_ids(self, user_ids: List[int]) -> List[VKUserDTO]:
        """Получить пользователей по списку ID"""
        pass
    
    # Complex operations
    @abstractmethod
    async def get_group_with_posts(self, group_id: int, posts_count: int = 10) -> Optional[VKGroupWithPostsDTO]:
        """Получить группу с постами"""
        pass
    
    @abstractmethod
    async def get_post_with_comments(self, group_id: int, post_id: int, comments_count: int = 50) -> Optional[VKPostWithCommentsDTO]:
        """Получить пост с комментариями"""
        pass
    
    @abstractmethod
    async def get_group_analytics(self, group_id: int, days: int = 7) -> Optional[VKGroupAnalyticsDTO]:
        """Получить аналитику группы"""
        pass
    
    # Health check
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья сервиса"""
        pass
