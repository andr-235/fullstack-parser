"""
Интерфейс репозитория VK API
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID
from vk_api.domain.entities.vk_group import VKGroup
from vk_api.domain.entities.vk_post import VKPost
from vk_api.domain.entities.vk_comment import VKComment


class VKAPIRepositoryInterface(ABC):
    """Интерфейс репозитория для работы с VK API"""
    
    # Groups
    @abstractmethod
    async def get_group_by_id(self, group_id: VKGroupID) -> Optional[VKGroup]:
        """Получить группу по ID"""
        pass
    
    @abstractmethod
    async def search_groups(
        self, 
        query: str, 
        count: int = 20, 
        offset: int = 0
    ) -> List[VKGroup]:
        """Поиск групп по запросу"""
        pass
    
    @abstractmethod
    async def get_groups_by_ids(self, group_ids: List[VKGroupID]) -> List[VKGroup]:
        """Получить группы по списку ID"""
        pass
    
    # Posts
    @abstractmethod
    async def get_group_posts(
        self, 
        group_id: VKGroupID, 
        count: int = 100, 
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[VKPost]:
        """Получить посты группы"""
        pass
    
    @abstractmethod
    async def get_post_by_id(
        self, 
        group_id: VKGroupID, 
        post_id: VKPostID
    ) -> Optional[VKPost]:
        """Получить пост по ID"""
        pass
    
    @abstractmethod
    async def get_posts_by_ids(
        self, 
        group_id: VKGroupID, 
        post_ids: List[VKPostID]
    ) -> List[VKPost]:
        """Получить посты по списку ID"""
        pass
    
    # Comments
    @abstractmethod
    async def get_post_comments(
        self, 
        group_id: VKGroupID, 
        post_id: VKPostID,
        count: int = 100,
        offset: int = 0,
        sort: str = "asc",
        thread_items_count: int = 0
    ) -> List[VKComment]:
        """Получить комментарии к посту"""
        pass
    
    @abstractmethod
    async def get_comment_by_id(
        self, 
        group_id: VKGroupID, 
        post_id: VKPostID,
        comment_id: int
    ) -> Optional[VKComment]:
        """Получить комментарий по ID"""
        pass
    
    # Users
    @abstractmethod
    async def get_user_by_id(self, user_id: VKUserID) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_users_by_ids(self, user_ids: List[VKUserID]) -> List[Dict[str, Any]]:
        """Получить пользователей по списку ID"""
        pass
    
    # Cache management
    @abstractmethod
    async def cache_set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: int = 300
    ) -> None:
        """Сохранить в кеш"""
        pass
    
    @abstractmethod
    async def cache_get(self, key: str) -> Optional[Any]:
        """Получить из кеша"""
        pass
    
    @abstractmethod
    async def cache_delete(self, key: str) -> None:
        """Удалить из кеша"""
        pass
    
    @abstractmethod
    async def cache_invalidate_pattern(self, pattern: str) -> None:
        """Инвалидировать кеш по паттерну"""
        pass
    
    # Health check
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья репозитория"""
        pass
