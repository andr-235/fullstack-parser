"""
Сервис VK API
"""

from typing import List, Optional

from .client import VKAPIClient
from .exceptions import VKAPIError
from .models import VKComment, VKGroup, VKPost, VKUser
from .schemas import (
    VKGetGroupPostsRequest,
    VKGetPostCommentsRequest,
    VKSearchGroupsRequest,
)


class VKAPIService:
    """Сервис для работы с VK API"""

    def __init__(self, access_token: Optional[str] = None):
        self.client = VKAPIClient(access_token)

    async def get_group(self, group_id: int) -> Optional[VKGroup]:
        """Получить группу по ID"""
        try:
            async with self.client as client:
                data = await client.get_group(group_id)
                if data:
                    return VKGroup(**data)
        except VKAPIError:
            pass
        return None

    async def search_groups(self, request: VKSearchGroupsRequest) -> List[VKGroup]:
        """Поиск групп"""
        try:
            async with self.client as client:
                data = await client.search_groups(
                    request.query,
                    request.count,
                    request.offset
                )
                return [VKGroup(**item) for item in data.get("items", [])]
        except VKAPIError:
            pass
        return []

    async def get_group_posts(self, request: VKGetGroupPostsRequest) -> List[VKPost]:
        """Получить посты группы"""
        try:
            async with self.client as client:
                data = await client.get_group_posts(
                    request.group_id,
                    request.count,
                    request.offset
                )
                return [VKPost(**item) for item in data.get("items", [])]
        except VKAPIError:
            pass
        return []

    async def get_post_comments(self, request: VKGetPostCommentsRequest) -> List[VKComment]:
        """Получить комментарии к посту"""
        try:
            async with self.client as client:
                data = await client.get_post_comments(
                    request.group_id,
                    request.post_id,
                    request.count,
                    request.offset
                )
                return [VKComment(**item) for item in data.get("items", [])]
        except VKAPIError:
            pass
        return []

    async def get_user(self, user_id: int) -> Optional[VKUser]:
        """Получить пользователя по ID"""
        try:
            async with self.client as client:
                data = await client.get_user(user_id)
                if data:
                    return VKUser(**data)
        except VKAPIError:
            pass
        return None


__all__ = ["VKAPIService"]
