"""
VKDataParser - сервис для непосредственного парсинга данных из VK API

Принципы SOLID:
- Single Responsibility: только парсинг данных из VK API
- Open/Closed: легко добавлять новые методы парсинга
- Liskov Substitution: можно заменить на другую реализацию парсера
- Interface Segregation: чистый интерфейс для парсинга
- Dependency Inversion: зависит от VKAPIService
"""

import logging
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.services.vk_api_service import VKAPIService

logger = logging.getLogger(__name__)


class VKDataParser:
    """
    Сервис для парсинга данных из VK API.

    Предоставляет высокоуровневый интерфейс для:
    - Парсинга постов групп
    - Парсинга комментариев к постам
    - Парсинга информации о пользователях
    - Валидации и обработки данных от VK API
    """

    def __init__(
        self, vk_service: VKAPIService, db: Optional[AsyncSession] = None
    ):
        """
        Инициализация парсера VK данных.

        Args:
            vk_service: Сервис для работы с VK API
            db: Асинхронная сессия базы данных (опционально)
        """
        self.vk_service = vk_service
        self.db = db

    async def parse_group_posts(
        self, group_id: int, limit: int = 10, offset: int = 0
    ) -> List[Dict]:
        """
        Парсинг постов группы из VK API.

        Args:
            group_id: ID группы VK (без знака минус)
            limit: Максимальное количество постов (1-100)
            offset: Смещение для пагинации

        Returns:
            Список постов в формате VK API
        """
        try:
            # Преобразуем group_id в owner_id для VK API
            owner_id = -abs(group_id)

            logger.info(
                f"Parsing posts for group {group_id} (owner_id: {owner_id})",
                group_id=group_id,
                owner_id=owner_id,
                limit=limit,
                offset=offset,
            )

            # Вызываем VK API
            posts = await self.vk_service.get_group_posts(
                group_id=group_id,
                count=min(limit, 100),  # Ограничение VK API
                offset=offset,
            )

            if not posts:
                logger.warning(f"No posts found for group {group_id}")
                return []
            logger.info(
                f"Successfully parsed {len(posts)} posts for group {group_id}"
            )

            return posts

        except Exception as e:
            logger.error(f"Error parsing posts for group {group_id}: {e}")
            raise

    async def parse_post_comments(
        self, post_id: int, owner_id: int, limit: int = 100, offset: int = 0
    ) -> List[Dict]:
        """
        Парсинг комментариев к посту из VK API.

        Args:
            post_id: ID поста
            owner_id: ID владельца поста (группа с минусом)
            limit: Максимальное количество комментариев (1-100)
            offset: Смещение для пагинации

        Returns:
            Список комментариев в формате VK API
        """
        try:
            logger.info(
                f"Parsing comments for post {post_id} in group {owner_id}",
                post_id=post_id,
                owner_id=owner_id,
                limit=limit,
                offset=offset,
            )

            # Вызываем VK API для получения комментариев
            comments_data = await self.vk_service.get_post_comments(
                owner_id=owner_id,
                post_id=post_id,
                count=min(limit, 100),  # Ограничение VK API
                offset=offset,
            )

            if not comments_data or "items" not in comments_data:
                logger.warning(f"No comments found for post {post_id}")
                return []

            comments = comments_data["items"]
            logger.info(
                f"Successfully parsed {len(comments)} comments for post {post_id}"
            )

            return comments

        except Exception as e:
            logger.error(f"Error parsing comments for post {post_id}: {e}")
            raise

    async def parse_user_info(self, user_ids: List[int]) -> Dict[int, Dict]:
        """
        Парсинг информации о пользователях из VK API.

        Args:
            user_ids: Список ID пользователей

        Returns:
            Словарь с информацией о пользователях {user_id: user_info}
        """
        try:
            if not user_ids:
                return {}

            # Ограничение VK API - максимум 1000 пользователей за запрос
            # Для простоты берем первые 100
            user_ids = user_ids[:100]

            logger.info(
                f"Parsing info for {len(user_ids)} users",
                user_count=len(user_ids),
            )

            # Получаем информацию о каждом пользователе отдельно
            users_dict = {}
            for user_id in user_ids:
                try:
                    user_data = await self.vk_service.get_user_info(user_id)
                    if user_data:
                        users_dict[user_id] = {
                            "id": user_data.get("id", user_id),
                            "first_name": user_data.get("first_name", ""),
                            "last_name": user_data.get("last_name", ""),
                            "screen_name": user_data.get("screen_name", ""),
                            "photo_url": user_data.get("photo_100", ""),
                        }
                except Exception as e:
                    logger.warning(
                        f"Failed to get info for user {user_id}: {e}"
                    )
                    continue

            logger.info(
                f"Successfully parsed info for {len(users_dict)} users"
            )
            return users_dict

        except Exception as e:
            logger.error(f"Error parsing user info: {e}")
            raise

    async def parse_group_info(self, group_ids: List[int]) -> Dict[int, Dict]:
        """
        Парсинг информации о группах из VK API.

        Args:
            group_ids: Список ID групп

        Returns:
            Словарь с информацией о группах {group_id: group_info}
        """
        try:
            if not group_ids:
                return {}

            # Ограничение VK API - максимум 500 групп за запрос
            group_ids = group_ids[:500]

            logger.info(
                f"Parsing info for {len(group_ids)} groups",
                group_count=len(group_ids),
            )

            # Получаем информацию о каждой группе отдельно
            groups_dict = {}
            for group_id in group_ids:
                try:
                    group_data = await self.vk_service.get_group_info(group_id)
                    if group_data:
                        groups_dict[group_id] = {
                            "id": group_data.get("id", group_id),
                            "name": group_data.get("name", ""),
                            "screen_name": group_data.get("screen_name", ""),
                            "member_count": group_data.get("members_count", 0),
                            "photo_url": group_data.get("photo_100", ""),
                        }
                except Exception as e:
                    logger.warning(
                        f"Failed to get info for group {group_id}: {e}"
                    )
                    continue

            logger.info(
                f"Successfully parsed info for {len(groups_dict)} groups"
            )
            return groups_dict

        except Exception as e:
            logger.error(f"Error parsing group info: {e}")
            raise

    async def validate_group_access(self, group_id: int) -> bool:
        """
        Проверка доступа к группе.

        Args:
            group_id: ID группы VK

        Returns:
            True если есть доступ, False иначе
        """
        try:
            # Пробуем получить 1 пост из группы
            posts = await self.vk_service.get_group_posts(
                group_id=group_id, count=1
            )

            # Если получили данные, значит есть доступ
            has_access = len(posts) > 0

            logger.info(
                f"Group access validation for {group_id}: {'granted' if has_access else 'denied'}"
            )

            return has_access

        except Exception as e:
            logger.warning(f"Error validating access to group {group_id}: {e}")
            return False

    async def get_group_posts_count(self, group_id: int) -> int:
        """
        Получить количество постов в группе.

        Args:
            group_id: ID группы VK

        Returns:
            Количество постов
        """
        try:
            # Используем специализированный метод для получения количества постов
            return await self.vk_service.get_group_posts_count(group_id)

        except Exception as e:
            logger.error(
                f"Error getting posts count for group {group_id}: {e}"
            )
            return 0

    async def get_post_comments_count(
        self, post_id: int, owner_id: int
    ) -> int:
        """
        Получить количество комментариев к посту.

        Args:
            post_id: ID поста
            owner_id: ID владельца поста

        Returns:
            Количество комментариев
        """
        try:
            # Используем специализированный метод для получения количества комментариев
            return await self.vk_service.get_post_comments_count(
                owner_id, post_id
            )

        except Exception as e:
            logger.error(
                f"Error getting comments count for post {post_id}: {e}"
            )
            return 0
