"""
Парсер групп для модуля Parser

Отвечает за парсинг конкретных групп VK
"""

import time
from typing import Any, Dict, List, Optional, Protocol

from infrastructure.logging import get_loguru_logger

from parser.config import parser_settings
from parser.utils import retry_with_backoff, validate_vk_group_id


class VKAPIServiceProtocol(Protocol):
    """Протокол для VK API сервиса"""

    async def get_group_info(self, group_id: int) -> Dict[str, Any]:
        """Получить информацию о группе"""
        ...

    async def get_group_posts(self, group_id: int, count: int) -> Dict[str, Any]:
        """Получить посты группы"""
        ...

    async def get_post_comments(self, group_id: int, post_id: int, count: int) -> Dict[str, Any]:
        """Получить комментарии к посту"""
        ...


class GroupParser:
    """Парсер групп VK"""

    def __init__(self, vk_api_service: VKAPIServiceProtocol):
        self.vk_api = vk_api_service
        self._logger = get_loguru_logger("group-parser")

    async def parse_group(
        self,
        group_id: int,
        max_posts: int = 10,
        max_comments_per_post: int = 100,
    ) -> Dict[str, Any]:
        """
        Парсинг конкретной группы VK

        Args:
            group_id: ID группы VK
            max_posts: Максимум постов
            max_comments_per_post: Максимум комментариев на пост

        Returns:
            Dict[str, Any]: Результат парсинга
        """
        try:
            # Валидация входных параметров
            if not validate_vk_group_id(group_id):
                raise ValueError(f"Неверный ID группы: {group_id}")

            if max_posts < 1 or max_posts > parser_settings.max_posts_per_group:
                raise ValueError(f"max_posts должен быть от 1 до {parser_settings.max_posts_per_group}")

            if max_comments_per_post < 0 or max_comments_per_post > parser_settings.max_comments_per_post:
                raise ValueError(f"max_comments_per_post должен быть от 0 до {parser_settings.max_comments_per_post}")

            start_time = time.time()
            self._logger.info(f"Starting parsing group {group_id}")

            # Получаем информацию о группе
            group_info = await self._get_group_info(group_id)
            if not group_info:
                return self._create_error_result(group_id, ["Группа не найдена или недоступна"])

            # Получаем посты
            posts = await self._get_group_posts(group_id, max_posts)
            posts_found = len(posts)

            # Обрабатываем посты и получаем комментарии
            comments_found = 0
            errors = []

            for post in posts:
                try:
                    post_comments = await self._get_post_comments(
                        group_id, post["id"], max_comments_per_post
                    )
                    comments_found += len(post_comments)
                except Exception as e:
                    error_msg = f"Ошибка получения комментариев к посту {post['id']}: {str(e)}"
                    errors.append(error_msg)
                    self._logger.warning(error_msg)

            duration = time.time() - start_time

            result = {
                "group_id": group_id,
                "group_info": group_info,
                "posts_found": posts_found,
                "comments_found": comments_found,
                "posts_saved": posts_found,
                "comments_saved": comments_found,
                "errors": errors,
                "duration_seconds": duration,
                "success": len(errors) == 0,
            }

            self._logger.info(
                f"Completed parsing group {group_id}: {posts_found} posts, {comments_found} comments"
            )

            return result

        except Exception as e:
            self._logger.error(f"Failed to parse group {group_id}: {str(e)}")
            return self._create_error_result(group_id, [str(e)])

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def _get_group_info(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о группе"""
        try:
            result = await self.vk_api.get_group_info(group_id)
            return result.get("group")
        except Exception as e:
            self._logger.warning(f"Failed to get group info for {group_id}: {str(e)}")
            return None

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def _get_group_posts(self, group_id: int, count: int) -> List[Dict[str, Any]]:
        """Получить посты группы"""
        try:
            result = await self.vk_api.get_group_posts(group_id, count)
            return result.get("posts", [])
        except Exception as e:
            self._logger.warning(f"Failed to get posts for group {group_id}: {str(e)}")
            return []

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def _get_post_comments(self, group_id: int, post_id: int, count: int) -> List[Dict[str, Any]]:
        """Получить комментарии к посту"""
        try:
            result = await self.vk_api.get_post_comments(group_id, post_id, count)
            return result.get("comments", [])
        except Exception as e:
            self._logger.warning(f"Failed to get comments for post {post_id}: {str(e)}")
            return []

    def _create_error_result(self, group_id: int, errors: List[str]) -> Dict[str, Any]:
        """Создать результат с ошибкой"""
        return {
            "group_id": group_id,
            "posts_found": 0,
            "comments_found": 0,
            "posts_saved": 0,
            "comments_saved": 0,
            "errors": errors,
            "duration_seconds": 0.0,
            "success": False,
        }
