"""
Сервис для работы с VK API

Содержит бизнес-логику для операций с VK API
"""

import time
import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from ..exceptions import ValidationError, ServiceUnavailableError
from .models import VKAPIRepository
from .client import VKAPIClient
from .config import vk_api_config
from .constants import (
    VK_API_MAX_POSTS_PER_REQUEST,
    VK_API_MAX_COMMENTS_PER_REQUEST,
    VK_API_MAX_GROUPS_PER_REQUEST,
    VK_API_MAX_USERS_PER_REQUEST,
    VK_OBJECT_TYPE_POST,
    VK_OBJECT_TYPE_COMMENT,
    VK_OBJECT_TYPE_GROUP,
    VK_OBJECT_TYPE_USER,
    VK_SORT_ASC,
    VK_SORT_DESC,
)


class VKAPIService:
    """
    Сервис для работы с VK API

    Реализует бизнес-логику для взаимодействия с VK API
    с обработкой ошибок, кешированием и rate limiting
    """

    def __init__(
        self, repository: VKAPIRepository, client: VKAPIClient = None
    ):
        self.repository = repository
        self.client = client or VKAPIClient()
        self.logger = logging.getLogger(__name__)

    async def get_group_posts(
        self, group_id: int, count: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Получить посты группы

        Args:
            group_id: ID группы VK
            count: Количество постов
            offset: Смещение

        Returns:
            Dict[str, Any]: Посты группы с метаданными
        """
        # Валидация входных данных
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("Неверный ID группы", field="group_id")

        count = min(count, VK_API_MAX_POSTS_PER_REQUEST)
        if count <= 0:
            raise ValidationError(
                "Количество постов должно быть положительным", field="count"
            )

        try:
            # Проверяем кеш
            cache_key = f"group:{group_id}:posts:{count}:{offset}"
            cached_result = await self.repository.get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Получаем данные через клиент
            params = {
                "owner_id": -abs(
                    group_id
                ),  # VK API использует отрицательные ID для групп
                "count": count,
                "offset": offset,
            }

            response = await self.client.make_request("wall.get", params)

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            posts_data = response["response"]
            posts = posts_data.get("items", [])

            result = {
                "posts": posts,
                "total_count": posts_data.get("count", 0),
                "group_id": group_id,
                "requested_count": count,
                "offset": offset,
                "has_more": len(posts) == count,
                "fetched_at": datetime.utcnow().isoformat(),
            }

            # Сохраняем в кеш
            await self.repository.save_cached_result(
                cache_key, result, vk_api_config.CACHE_TTL_GROUP_POSTS
            )

            return result

        except Exception as e:
            self.logger.error(f"Error getting group posts for {group_id}: {e}")
            raise ServiceUnavailableError(
                f"Ошибка получения постов группы: {str(e)}"
            )

    async def get_post_comments(
        self,
        group_id: int,
        post_id: int,
        count: int = 100,
        offset: int = 0,
        sort: str = VK_SORT_ASC,
    ) -> Dict[str, Any]:
        """
        Получить комментарии к посту

        Args:
            group_id: ID группы VK
            post_id: ID поста
            count: Количество комментариев
            offset: Смещение
            sort: Сортировка (asc, desc)

        Returns:
            Dict[str, Any]: Комментарии с метаданными
        """
        # Валидация входных данных
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("Неверный ID группы", field="group_id")
        if not isinstance(post_id, int) or post_id <= 0:
            raise ValidationError("Неверный ID поста", field="post_id")

        if sort not in [VK_SORT_ASC, VK_SORT_DESC]:
            raise ValidationError("Неверная сортировка", field="sort")

        count = min(count, VK_API_MAX_COMMENTS_PER_REQUEST)

        try:
            # Проверяем кеш
            cache_key = f"post:{post_id}:comments:{count}:{offset}:{sort}"
            cached_result = await self.repository.get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Получаем данные через клиент
            params = {
                "owner_id": -abs(group_id),
                "post_id": post_id,
                "count": count,
                "offset": offset,
                "sort": sort,
            }

            response = await self.client.make_request(
                "wall.getComments", params
            )

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            comments_data = response["response"]
            comments = comments_data.get("items", [])

            result = {
                "comments": comments,
                "total_count": comments_data.get("count", 0),
                "group_id": group_id,
                "post_id": post_id,
                "requested_count": count,
                "offset": offset,
                "sort": sort,
                "has_more": len(comments) == count,
                "fetched_at": datetime.utcnow().isoformat(),
            }

            # Сохраняем в кеш
            await self.repository.save_cached_result(
                cache_key, result, vk_api_config.CACHE_TTL_POST_COMMENTS
            )

            return result

        except Exception as e:
            self.logger.error(
                f"Error getting post comments for {post_id}: {e}"
            )
            raise ServiceUnavailableError(
                f"Ошибка получения комментариев: {str(e)}"
            )

    async def get_group_info(self, group_id: int) -> Dict[str, Any]:
        """
        Получить информацию о группе

        Args:
            group_id: ID группы VK

        Returns:
            Dict[str, Any]: Информация о группе
        """
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("Неверный ID группы", field="group_id")

        try:
            # Проверяем кеш
            cache_key = f"group:{group_id}:info"
            cached_result = await self.repository.get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Получаем данные через клиент
            params = {
                "group_ids": str(group_id),
                "fields": vk_api_config.GROUP_FIELDS,
            }

            response = await self.client.make_request("groups.getById", params)

            if "response" not in response or not response["response"]:
                raise ServiceUnavailableError(f"Группа {group_id} не найдена")

            group_data = response["response"][0]

            result = {
                "id": group_data.get("id"),
                "name": group_data.get("name", ""),
                "screen_name": group_data.get("screen_name", ""),
                "description": group_data.get("description", ""),
                "members_count": group_data.get("members_count", 0),
                "photo_url": group_data.get("photo_200", ""),
                "is_closed": group_data.get("is_closed", False),
                "type": group_data.get("type", "group"),
                "fetched_at": datetime.utcnow().isoformat(),
            }

            # Сохраняем в кеш
            await self.repository.save_cached_result(
                cache_key, result, vk_api_config.CACHE_TTL_GROUP_INFO
            )

            return result

        except Exception as e:
            self.logger.error(f"Error getting group info for {group_id}: {e}")
            raise ServiceUnavailableError(
                f"Ошибка получения информации о группе: {str(e)}"
            )

    async def search_groups(
        self,
        query: str,
        count: int = 20,
        offset: int = 0,
        country: Optional[int] = None,
        city: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Поиск групп по запросу

        Args:
            query: Поисковый запрос
            count: Количество результатов
            offset: Смещение
            country: ID страны
            city: ID города

        Returns:
            Dict[str, Any]: Результаты поиска
        """
        if not query or not query.strip():
            raise ValidationError(
                "Поисковый запрос не может быть пустым", field="query"
            )

        count = min(count, VK_API_MAX_GROUPS_PER_REQUEST)

        try:
            # Проверяем кеш
            cache_key = (
                f"search:groups:{query}:{count}:{offset}:{country}:{city}"
            )
            cached_result = await self.repository.get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Получаем данные через клиент
            params = {
                "q": query.strip(),
                "count": count,
                "offset": offset,
            }

            if country is not None:
                params["country"] = country
            if city is not None:
                params["city"] = city

            response = await self.client.make_request("groups.search", params)

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            search_data = response["response"]

            result = {
                "groups": search_data.get("items", []),
                "total_count": search_data.get("count", 0),
                "query": query,
                "requested_count": count,
                "offset": offset,
                "has_more": len(search_data.get("items", [])) == count,
                "fetched_at": datetime.utcnow().isoformat(),
            }

            # Сохраняем в кеш
            await self.repository.save_cached_result(
                cache_key, result, vk_api_config.CACHE_TTL_SEARCH
            )

            return result

        except Exception as e:
            self.logger.error(
                f"Error searching groups with query '{query}': {e}"
            )
            raise ServiceUnavailableError(f"Ошибка поиска групп: {str(e)}")

    async def get_user_info(
        self, user_ids: Union[int, List[int]]
    ) -> Dict[str, Any]:
        """
        Получить информацию о пользователе(ях)

        Args:
            user_ids: ID пользователя или список ID

        Returns:
            Dict[str, Any]: Информация о пользователе(ях)
        """
        if isinstance(user_ids, int):
            user_ids = [user_ids]

        if not user_ids:
            raise ValidationError(
                "Список ID пользователей не может быть пустым",
                field="user_ids",
            )

        if len(user_ids) > VK_API_MAX_USERS_PER_REQUEST:
            raise ValidationError(
                f"Слишком много пользователей (макс {VK_API_MAX_USERS_PER_REQUEST})",
                field="user_ids",
            )

        try:
            # Проверяем кеш
            user_ids_str = ",".join(map(str, sorted(user_ids)))
            cache_key = f"users:{user_ids_str}:info"
            cached_result = await self.repository.get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Получаем данные через клиент
            params = {
                "user_ids": ",".join(map(str, user_ids)),
                "fields": vk_api_config.USER_FIELDS,
            }

            response = await self.client.make_request("users.get", params)

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            users_data = response["response"]

            result = {
                "users": users_data,
                "requested_ids": user_ids,
                "found_count": len(users_data),
                "fetched_at": datetime.utcnow().isoformat(),
            }

            # Сохраняем в кеш
            await self.repository.save_cached_result(
                cache_key, result, vk_api_config.CACHE_TTL_USER_INFO
            )

            return result

        except Exception as e:
            self.logger.error(f"Error getting user info for {user_ids}: {e}")
            raise ServiceUnavailableError(
                f"Ошибка получения информации о пользователях: {str(e)}"
            )

    async def get_post_by_id(
        self, group_id: int, post_id: int
    ) -> Dict[str, Any]:
        """
        Получить пост по ID

        Args:
            group_id: ID группы VK
            post_id: ID поста

        Returns:
            Dict[str, Any]: Информация о посте
        """
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("Неверный ID группы", field="group_id")
        if not isinstance(post_id, int) or post_id <= 0:
            raise ValidationError("Неверный ID поста", field="post_id")

        try:
            # Получаем данные через клиент
            params = {
                "posts": f"-{abs(group_id)}_{post_id}",
            }

            response = await self.client.make_request("wall.getById", params)

            if "response" not in response or not response["response"]:
                raise ServiceUnavailableError(f"Пост {post_id} не найден")

            post_data = response["response"][0]

            result = {
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

            return result

        except Exception as e:
            self.logger.error(
                f"Error getting post {post_id} from group {group_id}: {e}"
            )
            raise ServiceUnavailableError(f"Ошибка получения поста: {str(e)}")

    async def validate_access_token(self) -> Dict[str, Any]:
        """
        Проверить валидность токена доступа

        Returns:
            Dict[str, Any]: Результат проверки токена
        """
        try:
            # Проверяем токен через получение информации о текущем пользователе
            params = {"fields": "id,first_name,last_name"}

            response = await self.client.make_request("users.get", params)

            if "response" in response and response["response"]:
                user_info = response["response"][0]
                return {
                    "valid": True,
                    "user_id": user_info.get("id"),
                    "user_name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
                    "checked_at": datetime.utcnow().isoformat(),
                }
            else:
                return {
                    "valid": False,
                    "error": "Invalid response format",
                    "checked_at": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat(),
            }

    async def get_api_limits(self) -> Dict[str, Any]:
        """
        Получить текущие лимиты VK API

        Returns:
            Dict[str, Any]: Информация о лимитах API
        """
        client_stats = self.client.get_stats()

        return {
            "max_requests_per_second": vk_api_config.MAX_REQUESTS_PER_SECOND,
            "max_posts_per_request": VK_API_MAX_POSTS_PER_REQUEST,
            "max_comments_per_request": VK_API_MAX_COMMENTS_PER_REQUEST,
            "max_groups_per_request": VK_API_MAX_GROUPS_PER_REQUEST,
            "max_users_per_request": VK_API_MAX_USERS_PER_REQUEST,
            "current_request_count": client_stats["current_request_count"],
            "last_request_time": client_stats["last_request_time"],
            "time_until_reset": client_stats["time_until_reset"],
        }

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику сервиса

        Returns:
            Dict[str, Any]: Статистика
        """
        client_stats = self.client.get_stats()
        repo_stats = await self.repository.get_stats()

        return {
            "client_stats": client_stats,
            "repository_stats": repo_stats,
            "cache_enabled": vk_api_config.CACHE_ENABLED,
            "token_configured": vk_api_config.is_token_configured(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить здоровье сервиса VK API

        Returns:
            Dict[str, Any]: Результат проверки здоровья
        """
        try:
            # Проверяем клиент
            client_health = await self.client.health_check()

            # Проверяем репозиторий
            repo_health = await self.repository.health_check()

            # Общий статус
            overall_status = (
                "healthy"
                if (
                    client_health["status"] == "healthy"
                    and repo_health["status"] == "healthy"
                )
                else "unhealthy"
            )

            return {
                "status": overall_status,
                "client": client_health,
                "repository": repo_health,
                "cache_enabled": vk_api_config.CACHE_ENABLED,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Экспорт
__all__ = [
    "VKAPIService",
]
