"""
Parser Service для обработки комментариев и поиска ключевых слов
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Callable, Coroutine, List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.parser import ParseStats
from app.services.vk_api_service import VKAPIService

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float], Coroutine[None, None, None]]


class ParserService:
    """Сервис для парсинга постов и комментариев VK"""

    def __init__(self, db: AsyncSession, vk_api: VKAPIService):
        self.db = db
        self.vk_api = vk_api

    async def parse_group_posts(
        self,
        group_id: int,
        max_posts_count: Optional[int] = None,
        force_reparse: bool = False,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> ParseStats:
        """
        Парсит посты группы, их комментарии и ищет ключевые слова.

        Args:
            group_id: ID группы в нашей БД.
            max_posts_count: Максимальное количество постов для обработки.
            force_reparse: Принудительно перепарсить уже обработанные посты.
            progress_callback: Функция обратного вызова для обновления прогресса.

        Returns:
            Статистика парсинга.
        """
        start_time = datetime.now(timezone.utc)
        group = await self._get_group(group_id)
        if not group or not group.is_active:
            logger.warning(f"Группа {group_id} не найдена или неактивна.")
            return ParseStats()

        logger.info(f"Начинаем парсинг группы {group.name} (VK ID: {group.vk_id})")
        stats = ParseStats()
        keywords = await self._get_active_keywords()
        if not keywords:
            logger.warning("Нет активных ключевых слов для поиска.")
            return stats

        logger.info(f"Используем {len(keywords)} ключевых слов для поиска.")
        posts_limit = max_posts_count or group.max_posts_to_check
        posts = await self.vk_api.get_group_posts(group.vk_id, count=posts_limit)

        total_posts = len(posts)
        for i, post_data in enumerate(posts):
            try:
                post = await self._get_or_create_post(group, post_data)
                if (
                    not force_reparse
                    and post.parsed_at
                    and post.updated_at
                    and post.parsed_at > post.updated_at
                ):
                    continue

                comments_count = self._get_nested_count(post_data, "comments")
                if comments_count > 0:
                    comment_stats = await self._parse_post_comments(
                        post, keywords, force_reparse
                    )
                    stats.comments_found += comment_stats["total"]
                    stats.comments_with_keywords += comment_stats["with_keywords"]
                    stats.new_comments += comment_stats["new"]
                    stats.keyword_matches += comment_stats["matches"]

                post.is_parsed = True
                post.parsed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                stats.posts_processed += 1
                if progress_callback:
                    progress = (i + 1) / total_posts
                    await progress_callback(progress)

                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(
                    f"Ошибка обработки поста {post_data.get('id', 'N/A')}: {e}",
                    exc_info=True,
                )
                continue

        await self._update_group_stats(group, stats)
        stats.duration_seconds = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()
        logger.info(f"Парсинг группы {group.name} завершён. Статистика: {stats}")
        return stats

    def _get_nested_count(self, data: dict, key: str) -> int:
        """
        Безопасно извлекает значение 'count' из вложенного словаря.
        API VK может возвращать как объект {'count': X}, так и просто X.
        """
        value = data.get(key, {})
        if isinstance(value, dict):
            return value.get("count", 0)
        if isinstance(value, int):
            return value
        return 0

    async def _get_group(self, group_id: int) -> Optional[VKGroup]:
        result = await self.db.execute(select(VKGroup).where(VKGroup.id == group_id))
        return result.scalar_one_or_none()

    async def _get_active_keywords(self) -> List[Keyword]:
        result = await self.db.execute(select(Keyword).where(Keyword.is_active))
        return list(result.scalars().all())

    async def _get_or_create_post(self, group: VKGroup, post_data: dict) -> VKPost:
        result = await self.db.execute(
            select(VKPost).where(VKPost.vk_id == post_data["id"])
        )
        post = result.scalar_one_or_none()
        if post:
            post.likes_count = self._get_nested_count(post_data, "likes")
            post.reposts_count = self._get_nested_count(post_data, "reposts")
            post.comments_count = self._get_nested_count(post_data, "comments")
            post.views_count = self._get_nested_count(post_data, "views")
            post.updated_at = datetime.fromtimestamp(
                post_data["date"], tz=timezone.utc
            ).replace(tzinfo=None)
            return post

        new_post = VKPost(
            vk_id=post_data["id"],
            vk_owner_id=post_data["owner_id"],
            group_id=group.id,
            text=post_data.get("text", ""),
            likes_count=self._get_nested_count(post_data, "likes"),
            reposts_count=self._get_nested_count(post_data, "reposts"),
            comments_count=self._get_nested_count(post_data, "comments"),
            views_count=self._get_nested_count(post_data, "views"),
            published_at=datetime.fromtimestamp(
                post_data["date"], tz=timezone.utc
            ).replace(tzinfo=None),
            updated_at=datetime.fromtimestamp(
                post_data["date"], tz=timezone.utc
            ).replace(tzinfo=None),
        )
        self.db.add(new_post)
        await self.db.flush()
        return new_post

    async def _parse_post_comments(
        self, post: VKPost, keywords: list[Keyword], force_reparse: bool = False
    ) -> dict[str, int]:
        stats = {"total": 0, "with_keywords": 0, "new": 0, "matches": 0}
        comments = await self.vk_api.get_post_comments(
            owner_id=post.group.vk_id, post_id=post.vk_id
        )
        stats["total"] = len(comments)

        for comment_data in comments:
            try:
                if not force_reparse:
                    existing = await self.db.execute(
                        select(VKComment).where(VKComment.vk_id == comment_data["id"])
                    )
                    if existing.scalar_one_or_none():
                        continue

                matches = self._find_keywords_in_text(comment_data["text"], keywords)
                if matches:
                    await self._save_comment(post, comment_data, matches)
                    stats["with_keywords"] += 1
                    stats["matches"] += len(matches)
                stats["new"] += 1
            except Exception as e:
                logger.error(
                    f"Ошибка обработки комментария {comment_data['id']}: {e}",
                    exc_info=True,
                )
                continue
        return stats

    def _find_keywords_in_text(
        self, text: str, keywords: list[Keyword]
    ) -> list[tuple[Keyword, str, int]]:
        matches: List[Tuple[Keyword, str, int]] = []
        text_lower = text.lower()
        for keyword in keywords:
            search_text = text if keyword.is_case_sensitive else text_lower
            search_word = (
                keyword.word if keyword.is_case_sensitive else keyword.word.lower()
            )
            if keyword.is_whole_word:
                pattern = r"\b" + re.escape(search_word) + r"\b"
                flags = re.IGNORECASE if not keyword.is_case_sensitive else 0
                for match in re.finditer(pattern, search_text, flags):
                    matches.append((keyword, match.group(0), match.start()))
            else:
                pos = search_text.find(search_word, 0)
                while pos != -1:
                    matches.append((keyword, search_word, pos))
                    pos = search_text.find(search_word, pos + 1)
        return matches

    async def _save_comment(
        self, post: VKPost, comment_data: dict, matches: list
    ) -> VKComment:
        new_comment = VKComment(
            vk_id=comment_data["id"],
            post_id=post.id,
            text=comment_data["text"],
            published_at=datetime.fromtimestamp(
                comment_data["date"], tz=timezone.utc
            ).replace(tzinfo=None),
            author_id=comment_data.get("from_id"),
        )
        self.db.add(new_comment)
        await self.db.flush()

        for keyword, matched_text, position in matches:
            match = CommentKeywordMatch(
                comment_id=new_comment.id,
                keyword_id=keyword.id,
                matched_text=matched_text,
                position=position,
            )
            self.db.add(match)

        return new_comment

    async def _update_group_stats(self, group: VKGroup, stats: ParseStats) -> None:
        group.last_parsed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        group.total_posts_parsed += stats.posts_processed
        group.total_comments_found += stats.comments_found
        await self.db.commit()

    async def parse_group_comments(
        self, group_id: int, max_posts: Optional[int] = None
    ) -> dict[str, int]:
        """
        [DEPRECATED] Парсинг комментариев группы
        """
        logger.warning(
            "Метод parse_group_comments устарел. " "Используйте parse_group_posts."
        )
        stats = await self.parse_group_posts(group_id, max_posts_count=max_posts)
        return stats.model_dump()

    async def get_parsing_status(self, task_id: str) -> dict:
        """Получить статус задачи парсинга."""
        return await self.redis_manager.get_task_status(task_id)

    async def run_parser_for_all_groups(self) -> dict:
        # ... existing code ...
