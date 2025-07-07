"""
VK API Service для получения данных из ВКонтакте
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

import vk_api

from app.core.config import settings

logger = logging.getLogger(__name__)


class VKAPIService:
    """Сервис для работы с VK API"""

    def __init__(self):
        self.session = vk_api.VkApi(token=settings.vk_access_token)
        self.api = self.session.get_api()
        self.last_request_time = 0
        self.requests_count = 0
        self.api_version = settings.vk_api_version

    async def _rate_limit_wait(self) -> None:
        """Контроль rate limit для VK API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        # VK API позволяет 3 запроса в секунду
        min_interval = 1.0 / settings.vk_requests_per_second

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limit: ожидание {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()
        self.requests_count += 1

    async def get_group_info(self, group_id: str) -> Optional[dict[str, Any]]:
        """
        Получить информацию о группе

        Args:
            group_id: ID или короткое имя группы (например, "python" или "12345")

        Returns:
            Словарь с информацией о группе или None
        """
        if not group_id:
            return None

        await self._rate_limit_wait()

        try:
            response = self.api.groups.getById(
                group_ids=group_id,
                fields="description,members_count,photo_50,photo_100,photo_200",
            )

            if response:
                group = response[0]
                return {
                    "vk_id": group["id"],
                    "name": group["name"],
                    "screen_name": group["screen_name"],
                    "description": group.get("description", ""),
                    "members_count": group.get("members_count", 0),
                    "is_closed": group.get("is_closed", 0) == 1,
                    "photo_url": group.get(
                        "photo_200", group.get("photo_100", group.get("photo_50", ""))
                    ),
                }
            return None
        except Exception as e:
            logger.error(f"Ошибка получения информации о группе {group_id}: {e}")
            return None

    async def get_group_posts(
        self, group_id: int, count: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Получить посты группы

        Args:
            group_id: ID группы (положительное число)
            count: Количество постов (максимум 100)
            offset: Смещение

        Returns:
            Список постов
        """
        await self._rate_limit_wait()

        try:
            # Для групп используем отрицательный ID
            owner_id = -abs(group_id)

            response = self.api.wall.get(
                owner_id=owner_id,
                count=min(count, 100),
                offset=offset,
                extended=1,
                fields="name,screen_name,photo_50",
            )

            posts = []
            for item in response["items"]:
                # Пропускаем репосты
                if "copy_history" in item:
                    continue

                post_data = {
                    "id": item["id"],
                    "owner_id": item["owner_id"],
                    "text": item.get("text", ""),
                    "date": datetime.fromtimestamp(item["date"], tz=timezone.utc),
                    "likes": item.get("likes", {}).get("count", 0),
                    "reposts": item.get("reposts", {}).get("count", 0),
                    "comments": item.get("comments", {}).get("count", 0),
                    "views": item.get("views", {}).get("count", 0),
                    "attachments": self._parse_attachments(item.get("attachments", [])),
                }
                posts.append(post_data)

            return posts

        except Exception as e:
            logger.error(f"Ошибка получения постов группы {group_id}: {e}")
            return []

    async def get_post_comments(
        self,
        owner_id: int,
        post_id: int,
        count: int = 100,
        offset: int = 0,
        sort: str = "asc",
    ) -> list[dict[str, Any]]:
        """
        Получить комментарии к посту

        Args:
            owner_id: ID владельца поста
            post_id: ID поста
            count: Количество комментариев (максимум 100)
            offset: Смещение
            sort: Порядок сортировки (asc/desc)

        Returns:
            Список комментариев
        """
        await self._rate_limit_wait()

        try:
            response = self.api.wall.getComments(
                owner_id=owner_id,
                post_id=post_id,
                count=min(count, 100),
                offset=offset,
                sort=sort,
                extended=1,
                fields="name,screen_name,photo_50",
                thread_items_count=10,
            )

            comments = []
            for item in response["items"]:
                comment_data = {
                    "id": item["id"],
                    "from_id": item["from_id"],
                    "text": item.get("text", ""),
                    "date": datetime.fromtimestamp(item["date"], tz=timezone.utc),
                    "likes": item.get("likes", {}).get("count", 0),
                    "reply_to_user": item.get("reply_to_user"),
                    "reply_to_comment": item.get("reply_to_comment"),
                    "attachments": self._parse_attachments(item.get("attachments", [])),
                    "thread": item.get("thread", {}),
                }

                # Добавляем информацию об авторе из extended данных
                if "profiles" in response:
                    author = self._find_author_info(
                        item["from_id"],
                        response.get("profiles", []),
                        response.get("groups", []),
                    )
                    if author:
                        comment_data["author"] = author

                comments.append(comment_data)

            return comments

        except Exception as e:
            logger.error(
                f"Ошибка получения комментариев поста {owner_id}_{post_id}: {e}"
            )
            return []

    def _parse_attachments(self, attachments: list[dict]) -> dict[str, Any]:
        """Парсинг вложений"""
        types_list: list[str] = []
        result = {
            "has_attachments": len(attachments) > 0,
            "types": types_list,
            "count": len(attachments),
        }

        for attachment in attachments:
            att_type = attachment.get("type")
            if att_type and att_type not in types_list:
                types_list.append(att_type)

        return result

    def _find_author_info(
        self, user_id: int, profiles: list[dict], groups: list[dict]
    ) -> Optional[dict]:
        """Поиск информации об авторе комментария"""
        # Поиск среди пользователей
        if user_id > 0:
            for profile in profiles:
                if profile["id"] == user_id:
                    return {
                        "id": profile["id"],
                        "name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip(),
                        "screen_name": profile.get("screen_name", ""),
                        "photo_url": profile.get("photo_50", ""),
                    }
        # Поиск среди групп (отрицательный ID)
        else:
            group_id = abs(user_id)
            for group in groups:
                if group["id"] == group_id:
                    return {
                        "id": -group["id"],
                        "name": group.get("name", ""),
                        "screen_name": group.get("screen_name", ""),
                        "photo_url": group.get("photo_50", ""),
                    }

        return None

    async def get_comments_count(self, owner_id: int, post_id: int) -> int:
        """Получить количество комментариев к посту"""
        await self._rate_limit_wait()

        try:
            response = self.api.wall.getComments(
                owner_id=owner_id, post_id=post_id, count=1
            )
            return response.get("count", 0)
        except Exception as e:
            logger.error(
                f"Ошибка получения количества комментариев {owner_id}_{post_id}: {e}"
            )
            return 0
