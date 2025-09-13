"""
Доменный сервис VK API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID
from vk_api.domain.entities.vk_group import VKGroup
from vk_api.domain.entities.vk_post import VKPost
from vk_api.domain.entities.vk_comment import VKComment
from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface


class VKAPIDomainService:
    """Доменный сервис для бизнес-логики VK API"""
    
    def __init__(self, repository: VKAPIRepositoryInterface):
        self.repository = repository
    
    async def get_group_with_posts(
        self, 
        group_id: VKGroupID, 
        posts_count: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Получить группу с постами"""
        group = await self.repository.get_group_by_id(group_id)
        if not group:
            return None
        
        posts = await self.repository.get_group_posts(
            group_id=group_id,
            count=posts_count
        )
        
        return {
            'group': group,
            'posts': posts,
            'posts_count': len(posts)
        }
    
    async def get_post_with_comments(
        self, 
        group_id: VKGroupID, 
        post_id: VKPostID,
        comments_count: int = 50
    ) -> Optional[Dict[str, Any]]:
        """Получить пост с комментариями"""
        post = await self.repository.get_post_by_id(group_id, post_id)
        if not post:
            return None
        
        comments = await self.repository.get_post_comments(
            group_id=group_id,
            post_id=post_id,
            count=comments_count
        )
        
        return {
            'post': post,
            'comments': comments,
            'comments_count': len(comments)
        }
    
    async def search_groups_with_validation(
        self, 
        query: str, 
        count: int = 20
    ) -> List[VKGroup]:
        """Поиск групп с валидацией"""
        if not query or len(query.strip()) < 2:
            raise ValueError("Query must be at least 2 characters long")
        
        if count <= 0 or count > 1000:
            raise ValueError("Count must be between 1 and 1000")
        
        return await self.repository.search_groups(
            query=query.strip(),
            count=count
        )
    
    async def get_group_analytics(
        self, 
        group_id: VKGroupID, 
        days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """Получить аналитику группы"""
        group = await self.repository.get_group_by_id(group_id)
        if not group:
            return None
        
        end_date = datetime.now()
        start_date = end_date.replace(day=end_date.day - days)
        
        posts = await self.repository.get_group_posts(
            group_id=group_id,
            start_date=start_date,
            end_date=end_date,
            count=1000  # Максимум для анализа
        )
        
        if not posts:
            return {
                'group': group,
                'period_days': days,
                'posts_count': 0,
                'total_likes': 0,
                'total_reposts': 0,
                'total_comments': 0,
                'avg_engagement': 0.0
            }
        
        total_likes = sum(post.likes_count for post in posts)
        total_reposts = sum(post.reposts_count for post in posts)
        total_comments = sum(post.comments_count for post in posts)
        
        # Расчет engagement rate
        if group.members_count and group.members_count > 0:
            total_engagement = total_likes + total_reposts + total_comments
            avg_engagement = (total_engagement / len(posts)) / group.members_count * 100
        else:
            avg_engagement = 0.0
        
        return {
            'group': group,
            'period_days': days,
            'posts_count': len(posts),
            'total_likes': total_likes,
            'total_reposts': total_reposts,
            'total_comments': total_comments,
            'avg_engagement': round(avg_engagement, 2)
        }
    
    async def validate_group_access(self, group_id: VKGroupID) -> bool:
        """Проверить доступность группы"""
        try:
            group = await self.repository.get_group_by_id(group_id)
            return group is not None and group.is_public
        except Exception:
            return False
    
    async def get_user_groups(
        self, 
        user_id: VKUserID, 
        count: int = 20
    ) -> List[VKGroup]:
        """Получить группы пользователя (если доступно)"""
        # Это требует специальных прав доступа
        # В реальном приложении здесь будет вызов API для получения групп пользователя
        raise NotImplementedError("User groups access requires special permissions")
