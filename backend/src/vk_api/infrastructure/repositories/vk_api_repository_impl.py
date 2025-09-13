"""
Реализация репозитория VK API
"""

import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID
from vk_api.domain.entities.vk_group import VKGroup
from vk_api.domain.entities.vk_post import VKPost
from vk_api.domain.entities.vk_comment import VKComment
from shared.infrastructure.cache.redis_cache import RedisCache
from vk_api.infrastructure.clients.vk_api_client_impl import VKAPIClientImpl
from shared.presentation.exceptions import InternalServerException as ServiceUnavailableError, ValidationException as ValidationError


logger = logging.getLogger(__name__)


class VKAPIRepositoryImpl(VKAPIRepositoryInterface):
    """Реализация репозитория VK API"""
    
    def __init__(
        self,
        vk_client: VKAPIClientImpl,
        cache: RedisCache,
        cache_ttl: int = 300
    ):
        self.vk_client = vk_client
        self.cache = cache
        self.cache_ttl = cache_ttl
    
    # Groups
    async def get_group_by_id(self, group_id: VKGroupID) -> Optional[VKGroup]:
        """Получить группу по ID"""
        cache_key = f"vk:group:{group_id}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return VKGroup.from_vk_response(cached_data)
            except Exception as e:
                logger.warning(f"Failed to deserialize cached group data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "groups.getById",
                {"group_id": int(group_id), "fields": "description,members_count,verified"}
            )
            
            if not response or not response.get("response"):
                return None
            
            group_data = response["response"][0]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, group_data, self.cache_ttl)
            
            return VKGroup.from_vk_response(group_data)
            
        except Exception as e:
            logger.error(f"Failed to get group {group_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get group: {e}")
    
    async def search_groups(
        self, 
        query: str, 
        count: int = 20, 
        offset: int = 0
    ) -> List[VKGroup]:
        """Поиск групп по запросу"""
        cache_key = f"vk:search:groups:{query}:{count}:{offset}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return [VKGroup.from_vk_response(group_data) for group_data in cached_data]
            except Exception as e:
                logger.warning(f"Failed to deserialize cached search data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "groups.search",
                {
                    "q": query,
                    "count": count,
                    "offset": offset,
                    "type": "group",
                    "fields": "description,members_count,verified"
                }
            )
            
            if not response or not response.get("response"):
                return []
            
            groups_data = response["response"]["items"]
            groups = [VKGroup.from_vk_response(group_data) for group_data in groups_data]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, groups_data, self.cache_ttl)
            
            return groups
            
        except Exception as e:
            logger.error(f"Failed to search groups: {e}")
            raise ServiceUnavailableError(f"Failed to search groups: {e}")
    
    async def get_groups_by_ids(self, group_ids: List[VKGroupID]) -> List[VKGroup]:
        """Получить группы по списку ID"""
        if not group_ids:
            return []
        
        cache_key = f"vk:groups:batch:{','.join(map(str, group_ids))}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return [VKGroup.from_vk_response(group_data) for group_data in cached_data]
            except Exception as e:
                logger.warning(f"Failed to deserialize cached groups data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "groups.getById",
                {
                    "group_ids": ",".join(map(str, group_ids)),
                    "fields": "description,members_count,verified"
                }
            )
            
            if not response or not response.get("response"):
                return []
            
            groups_data = response["response"]
            groups = [VKGroup.from_vk_response(group_data) for group_data in groups_data]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, groups_data, self.cache_ttl)
            
            return groups
            
        except Exception as e:
            logger.error(f"Failed to get groups by IDs: {e}")
            raise ServiceUnavailableError(f"Failed to get groups: {e}")
    
    # Posts
    async def get_group_posts(
        self, 
        group_id: VKGroupID, 
        count: int = 100, 
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[VKPost]:
        """Получить посты группы"""
        cache_key = f"vk:group:{group_id}:posts:{count}:{offset}"
        if start_date:
            cache_key += f":{start_date.timestamp()}"
        if end_date:
            cache_key += f":{end_date.timestamp()}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return [VKPost.from_vk_response(post_data) for post_data in cached_data]
            except Exception as e:
                logger.warning(f"Failed to deserialize cached posts data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Параметры запроса
            params = {
                "owner_id": -int(group_id),  # Отрицательный ID для группы
                "count": count,
                "offset": offset,
                "extended": 1
            }
            
            if start_date:
                params["start_time"] = int(start_date.timestamp())
            if end_date:
                params["end_time"] = int(end_date.timestamp())
            
            # Запрос к VK API
            response = await self.vk_client.call_method("wall.get", params)
            
            if not response or not response.get("response"):
                return []
            
            posts_data = response["response"]["items"]
            posts = [VKPost.from_vk_response(post_data) for post_data in posts_data]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, posts_data, self.cache_ttl)
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get group posts: {e}")
            raise ServiceUnavailableError(f"Failed to get group posts: {e}")
    
    async def get_post_by_id(
        self, 
        group_id: VKGroupID, 
        post_id: VKPostID
    ) -> Optional[VKPost]:
        """Получить пост по ID"""
        cache_key = f"vk:group:{group_id}:post:{post_id}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return VKPost.from_vk_response(cached_data)
            except Exception as e:
                logger.warning(f"Failed to deserialize cached post data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "wall.getById",
                {
                    "posts": f"-{group_id}_{post_id}",
                    "extended": 1
                }
            )
            
            if not response or not response.get("response") or not response["response"]["items"]:
                return None
            
            post_data = response["response"]["items"][0]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, post_data, self.cache_ttl)
            
            return VKPost.from_vk_response(post_data)
            
        except Exception as e:
            logger.error(f"Failed to get post {post_id} from group {group_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get post: {e}")
    
    async def get_posts_by_ids(
        self, 
        group_id: VKGroupID, 
        post_ids: List[VKPostID]
    ) -> List[VKPost]:
        """Получить посты по списку ID"""
        if not post_ids:
            return []
        
        cache_key = f"vk:group:{group_id}:posts:batch:{','.join(map(str, post_ids))}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return [VKPost.from_vk_response(post_data) for post_data in cached_data]
            except Exception as e:
                logger.warning(f"Failed to deserialize cached posts data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Формируем строку постов
            posts_string = ",".join(f"-{group_id}_{post_id}" for post_id in post_ids)
            
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "wall.getById",
                {
                    "posts": posts_string,
                    "extended": 1
                }
            )
            
            if not response or not response.get("response"):
                return []
            
            posts_data = response["response"]["items"]
            posts = [VKPost.from_vk_response(post_data) for post_data in posts_data]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, posts_data, self.cache_ttl)
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get posts by IDs: {e}")
            raise ServiceUnavailableError(f"Failed to get posts: {e}")
    
    # Comments
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
        cache_key = f"vk:group:{group_id}:post:{post_id}:comments:{count}:{offset}:{sort}:{thread_items_count}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return [VKComment.from_vk_response(comment_data, post_id) for comment_data in cached_data]
            except Exception as e:
                logger.warning(f"Failed to deserialize cached comments data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "wall.getComments",
                {
                    "owner_id": -int(group_id),
                    "post_id": int(post_id),
                    "count": count,
                    "offset": offset,
                    "sort": sort,
                    "thread_items_count": thread_items_count,
                    "extended": 1
                }
            )
            
            if not response or not response.get("response"):
                return []
            
            comments_data = response["response"]["items"]
            comments = [VKComment.from_vk_response(comment_data, post_id) for comment_data in comments_data]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, comments_data, self.cache_ttl)
            
            return comments
            
        except Exception as e:
            logger.error(f"Failed to get post comments: {e}")
            raise ServiceUnavailableError(f"Failed to get post comments: {e}")
    
    async def get_comment_by_id(
        self, 
        group_id: VKGroupID, 
        post_id: VKPostID,
        comment_id: int
    ) -> Optional[VKComment]:
        """Получить комментарий по ID"""
        cache_key = f"vk:group:{group_id}:post:{post_id}:comment:{comment_id}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return VKComment.from_vk_response(cached_data, post_id)
            except Exception as e:
                logger.warning(f"Failed to deserialize cached comment data: {e}")
                await self.cache.delete(cache_key)
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "wall.getComment",
                {
                    "owner_id": -int(group_id),
                    "comment_id": comment_id,
                    "extended": 1
                }
            )
            
            if not response or not response.get("response"):
                return None
            
            comment_data = response["response"]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, comment_data, self.cache_ttl)
            
            return VKComment.from_vk_response(comment_data, post_id)
            
        except Exception as e:
            logger.error(f"Failed to get comment {comment_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get comment: {e}")
    
    # Users
    async def get_user_by_id(self, user_id: VKUserID) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        cache_key = f"vk:user:{user_id}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "users.get",
                {
                    "user_ids": str(user_id),
                    "fields": "photo_50,photo_100,photo_200,verified,is_closed"
                }
            )
            
            if not response or not response.get("response"):
                return None
            
            user_data = response["response"][0]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, user_data, self.cache_ttl)
            
            return user_data
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise ServiceUnavailableError(f"Failed to get user: {e}")
    
    async def get_users_by_ids(self, user_ids: List[VKUserID]) -> List[Dict[str, Any]]:
        """Получить пользователей по списку ID"""
        if not user_ids:
            return []
        
        cache_key = f"vk:users:batch:{','.join(map(str, user_ids))}"
        
        # Проверяем кеш
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Запрос к VK API
            response = await self.vk_client.call_method(
                "users.get",
                {
                    "user_ids": ",".join(map(str, user_ids)),
                    "fields": "photo_50,photo_100,photo_200,verified,is_closed"
                }
            )
            
            if not response or not response.get("response"):
                return []
            
            users_data = response["response"]
            
            # Сохраняем в кеш
            await self.cache.set(cache_key, users_data, self.cache_ttl)
            
            return users_data
            
        except Exception as e:
            logger.error(f"Failed to get users by IDs: {e}")
            raise ServiceUnavailableError(f"Failed to get users: {e}")
    
    # Cache management
    async def cache_set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Сохранить в кеш"""
        await self.cache.set(key, value, ttl_seconds)
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Получить из кеша"""
        return await self.cache.get(key)
    
    async def cache_delete(self, key: str) -> None:
        """Удалить из кеша"""
        await self.cache.delete(key)
    
    async def cache_invalidate_pattern(self, pattern: str) -> None:
        """Инвалидировать кеш по паттерну"""
        await self.cache.invalidate_pattern(pattern)
    
    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья репозитория"""
        try:
            # Проверяем VK API
            vk_health = await self.vk_client.health_check()
            
            # Проверяем кеш
            cache_health = await self.cache.health_check()
            
            return {
                "status": "healthy" if vk_health["status"] == "healthy" and cache_health["status"] == "healthy" else "unhealthy",
                "vk_api": vk_health,
                "cache": cache_health,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
