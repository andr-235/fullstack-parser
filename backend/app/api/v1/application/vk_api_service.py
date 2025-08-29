"""
VKAPIService - DDD Application Service для работы с VK API

Мигрирован из app/services/vk_api_service.py
"""

from typing import Dict, List, Optional, Any, Union
import asyncio
import time
from datetime import datetime


class VKAPIService:
    """
    DDD Application Service для работы с VK API.

    Предоставляет высокоуровневый интерфейс для:
    - Получения постов и комментариев из VK
    - Поиска групп и пользователей
    - Управления rate limiting
    - Обработки ошибок VK API
    """

    # VK API лимиты
    MAX_REQUESTS_PER_SECOND = 3  # Лимит запросов в секунду
    MAX_POSTS_PER_REQUEST = 100  # Максимум постов за запрос
    MAX_COMMENTS_PER_REQUEST = 100  # Максимум комментариев за запрос
    MAX_GROUPS_PER_REQUEST = 1000  # Максимум групп за поиск
    MAX_USERS_PER_REQUEST = 1000  # Максимум пользователей за запрос

    def __init__(self, vk_api_client=None, cache_service=None):
        """
        Инициализация VKAPIService.

        Args:
            vk_api_client: Клиент для работы с VK API
            cache_service: Сервис кеширования
        """
        self.vk_api_client = vk_api_client
        self.cache_service = cache_service

        # Rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset_time = time.time()

    # =============== МИГРАЦИЯ VKAPIService В DDD ===============

    async def get_group_posts(
        self, group_id: int, count: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Получить посты группы (мигрировано из VKAPIService)

        Args:
            group_id: ID группы VK
            count: Количество постов
            offset: Смещение

        Returns:
            Посты группы с метаданными
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Получаем посты через инфраструктурный клиент
        posts_data = await self.vk_api_client.get_group_posts(
            group_id=group_id,
            count=min(count, self.MAX_POSTS_PER_REQUEST),
            offset=offset,
        )

        # Публикуем Domain Event о получении данных
        from ..infrastructure.events.vk_api_events import (
            VKAPIDataFetchedEvent,
            create_vk_api_data_fetched_event,
        )
        from ..infrastructure.events.domain_event_publisher import (
            publish_domain_event,
        )

        data_fetched_event = create_vk_api_data_fetched_event(
            data_type="posts",
            object_id=group_id,
            items_count=len(posts_data.get("items", [])),
            total_count=posts_data.get("count", 0),
            fetch_time=None,  # TODO: измерить время
        )
        await publish_domain_event(data_fetched_event)

        return {
            "posts": posts_data.get("items", []),
            "total_count": posts_data.get("count", 0),
            "group_id": group_id,
            "requested_count": count,
            "offset": offset,
            "has_more": len(posts_data.get("items", [])) == count,
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def get_post_comments(
        self,
        group_id: int,
        post_id: int,
        count: int = 100,
        offset: int = 0,
        sort: str = "asc",
    ) -> Dict[str, Any]:
        """
        Получить комментарии к посту (мигрировано из VKAPIService)

        Args:
            group_id: ID группы VK
            post_id: ID поста
            count: Количество комментариев
            offset: Смещение
            sort: Сортировка (asc, desc)

        Returns:
            Комментарии к посту с метаданными
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Получаем комментарии через инфраструктурный клиент
        comments_data = await self.vk_api_client.get_post_comments(
            group_id=group_id,
            post_id=post_id,
            count=min(count, self.MAX_COMMENTS_PER_REQUEST),
            offset=offset,
            sort=sort,
        )

        return {
            "comments": comments_data.get("items", []),
            "total_count": comments_data.get("count", 0),
            "group_id": group_id,
            "post_id": post_id,
            "requested_count": count,
            "offset": offset,
            "sort": sort,
            "has_more": len(comments_data.get("items", [])) == count,
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def get_group_info(self, group_id: int) -> Dict[str, Any]:
        """
        Получить информацию о группе (мигрировано из VKAPIService)

        Args:
            group_id: ID группы VK

        Returns:
            Информация о группе
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Получаем информацию о группе
        group_data = await self.vk_api_client.get_group_info(group_id)

        if not group_data:
            return {"error": "Group not found", "group_id": group_id}

        return {
            "id": group_data.get("id"),
            "name": group_data.get("name"),
            "screen_name": group_data.get("screen_name"),
            "description": group_data.get("description", ""),
            "members_count": group_data.get("members_count", 0),
            "photo_url": group_data.get("photo_200", ""),
            "is_closed": group_data.get("is_closed", False),
            "type": group_data.get("type", "group"),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def search_groups(
        self,
        query: str,
        count: int = 20,
        offset: int = 0,
        country: Optional[int] = None,
        city: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Поиск групп по запросу (мигрировано из VKAPIService)

        Args:
            query: Поисковый запрос
            count: Количество результатов
            offset: Смещение
            country: ID страны
            city: ID города

        Returns:
            Результаты поиска групп
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Ищем группы через инфраструктурный клиент
        search_data = await self.vk_api_client.search_groups(
            query=query,
            count=min(count, self.MAX_GROUPS_PER_REQUEST),
            offset=offset,
            country=country,
            city=city,
        )

        return {
            "groups": search_data.get("items", []),
            "total_count": search_data.get("count", 0),
            "query": query,
            "requested_count": count,
            "offset": offset,
            "has_more": len(search_data.get("items", [])) == count,
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def get_user_info(
        self, user_ids: Union[int, List[int]]
    ) -> Dict[str, Any]:
        """
        Получить информацию о пользователе(ях) (мигрировано из VKAPIService)

        Args:
            user_ids: ID пользователя или список ID

        Returns:
            Информация о пользователе(ях)
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Получаем информацию о пользователях
        users_data = await self.vk_api_client.get_user_info(user_ids)

        if isinstance(user_ids, int):
            user_ids = [user_ids]

        return {
            "users": users_data,
            "requested_ids": user_ids,
            "found_count": len(users_data),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def get_post_by_id(
        self, group_id: int, post_id: int
    ) -> Dict[str, Any]:
        """
        Получить пост по ID (мигрировано из VKAPIService)

        Args:
            group_id: ID группы VK
            post_id: ID поста

        Returns:
            Информация о посте
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Получаем пост через инфраструктурный клиент
        post_data = await self.vk_api_client.get_post_by_id(group_id, post_id)

        if not post_data:
            return {
                "error": "Post not found",
                "group_id": group_id,
                "post_id": post_id,
            }

        return {
            "id": post_data.get("id"),
            "owner_id": post_data.get("owner_id"),
            "from_id": post_data.get("from_id"),
            "created_by": post_data.get("created_by"),
            "date": post_data.get("date"),
            "text": post_data.get("text", ""),
            "attachments": post_data.get("attachments", []),
            "comments": post_data.get("comments", {}),
            "likes": post_data.get("likes", {}),
            "reposts": post_data.get("reposts", {}),
            "views": post_data.get("views", {}),
            "is_pinned": post_data.get("is_pinned", False),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def validate_access_token(self) -> Dict[str, Any]:
        """
        Проверить валидность токена доступа (мигрировано из VKAPIService)

        Returns:
            Результат проверки токена
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Проверяем токен через инфраструктурный клиент
        try:
            user_info = await self.vk_api_client.get_current_user_info()

            # Публикуем Domain Event о успешной валидации токена
            from ..infrastructure.events.vk_api_events import (
                VKAPITokenValidationEvent,
                create_vk_api_data_fetched_event,
            )
            from ..infrastructure.events.domain_event_publisher import (
                publish_domain_event,
            )

            token_validation_event = VKAPITokenValidationEvent(
                token_valid=True,
                user_id=user_info.get("id"),
                permissions=[],  # TODO: получить разрешения
                validation_error=None,
            )
            await publish_domain_event(token_validation_event)

            return {
                "valid": True,
                "user_id": user_info.get("id"),
                "user_name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
                "checked_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            # Публикуем Domain Event об ошибке валидации токена
            from ..infrastructure.events.vk_api_events import (
                VKAPITokenValidationEvent,
            )
            from ..infrastructure.events.domain_event_publisher import (
                publish_domain_event,
            )

            token_validation_event = VKAPITokenValidationEvent(
                token_valid=False,
                user_id=None,
                permissions=[],
                validation_error=str(e),
            )
            await publish_domain_event(token_validation_event)

            return {
                "valid": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat(),
            }

    async def get_api_limits(self) -> Dict[str, Any]:
        """
        Получить текущие лимиты VK API (мигрировано из VKAPIService)

        Returns:
            Информация о лимитах API
        """
        return {
            "max_requests_per_second": self.MAX_REQUESTS_PER_SECOND,
            "max_posts_per_request": self.MAX_POSTS_PER_REQUEST,
            "max_comments_per_request": self.MAX_COMMENTS_PER_REQUEST,
            "max_groups_per_request": self.MAX_GROUPS_PER_REQUEST,
            "max_users_per_request": self.MAX_USERS_PER_REQUEST,
            "current_request_count": self.request_count,
            "last_request_time": self.last_request_time,
            "rate_limit_reset_time": self.rate_limit_reset_time,
            "time_until_reset": max(
                0, 1.0 - (time.time() - self.rate_limit_reset_time)
            ),
        }

    async def bulk_get_posts(
        self, group_id: int, post_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Массовое получение постов (мигрировано из VKAPIService)

        Args:
            group_id: ID группы VK
            post_ids: Список ID постов

        Returns:
            Посты с метаданными
        """
        posts = []

        # Обрабатываем посты батчами из-за rate limiting
        for i in range(0, len(post_ids), self.MAX_POSTS_PER_REQUEST):
            batch_ids = post_ids[i : i + self.MAX_POSTS_PER_REQUEST]

            for post_id in batch_ids:
                try:
                    post_data = await self.get_post_by_id(group_id, post_id)
                    if "error" not in post_data:
                        posts.append(post_data)
                except Exception as e:
                    self.logger.error(f"Error getting post {post_id}: {e}")

        return {
            "posts": posts,
            "total_requested": len(post_ids),
            "total_found": len(posts),
            "group_id": group_id,
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def get_group_members(
        self, group_id: int, count: int = 1000, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Получить участников группы (мигрировано из VKAPIService)

        Args:
            group_id: ID группы VK
            count: Количество участников
            offset: Смещение

        Returns:
            Участники группы
        """
        # Применяем rate limiting
        await self._rate_limit()

        # Получаем участников через инфраструктурный клиент
        members_data = await self.vk_api_client.get_group_members(
            group_id=group_id,
            count=min(count, self.MAX_USERS_PER_REQUEST),
            offset=offset,
        )

        return {
            "members": members_data.get("items", []),
            "total_count": members_data.get("count", 0),
            "group_id": group_id,
            "requested_count": count,
            "offset": offset,
            "has_more": len(members_data.get("items", [])) == count,
            "fetched_at": datetime.utcnow().isoformat(),
        }

    # =============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===============

    async def _rate_limit(self):
        """
        Применяет rate limiting для VK API
        """
        current_time = time.time()

        # Сброс счетчика каждую секунду
        if current_time - self.rate_limit_reset_time >= 1.0:
            self.request_count = 0
            self.rate_limit_reset_time = current_time

        # Если достигли лимита, ждем
        if self.request_count >= self.MAX_REQUESTS_PER_SECOND:
            wait_time = 1.0 - (current_time - self.rate_limit_reset_time)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.rate_limit_reset_time = time.time()

        self.request_count += 1
        self.last_request_time = time.time()

    def _get_token_preview(self) -> str:
        """
        Возвращает превью токена для логирования

        Returns:
            Превью токена
        """
        if hasattr(self.vk_api_client, "token") and self.vk_api_client.token:
            token = self.vk_api_client.token
            if len(token) > 8:
                return f"{token[:4]}...{token[-4:]}"
        return "***"

    def _ensure_group_owner_id(self, group_id: int) -> int:
        """
        Преобразует ID группы в owner_id для VK API

        Args:
            group_id: ID группы

        Returns:
            owner_id для VK API
        """
        return -abs(group_id)
