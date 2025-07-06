"""
Parser Service для обработки комментариев и поиска ключевых слов
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.services.vk_api_service import VKAPIService

logger = logging.getLogger(__name__)


class ParserService:
    """Сервис для парсинга комментариев VK"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.vk_api = VKAPIService()

    async def parse_group_comments(
        self, group_id: int, max_posts: Optional[int] = None
    ) -> dict[str, int]:
        """
        Парсинг комментариев группы

        Args:
            group_id: ID группы в нашей БД
            max_posts: Максимальное количество постов для обработки

        Returns:
            Статистика парсинга
        """
        # Получаем группу из БД
        result = await self.db.execute(select(VKGroup).where(VKGroup.id == group_id))
        group = result.scalar_one_or_none()

        if not group or not group.is_active:
            logger.warning(f"Группа {group_id} не найдена или неактивна")
            return {
                "posts_processed": 0,
                "comments_found": 0,
                "comments_with_keywords": 0,
                "new_comments": 0,
                "keyword_matches": 0,
            }

        logger.info(f"Начинаем парсинг группы {group.name} (VK ID: {group.vk_id})")

        stats = {
            "posts_processed": 0,
            "comments_found": 0,
            "comments_with_keywords": 0,
            "new_comments": 0,
            "keyword_matches": 0,
        }

        # Получаем активные ключевые слова
        keywords = await self._get_active_keywords()
        if not keywords:
            logger.warning("Нет активных ключевых слов для поиска")
            return {
                "posts_processed": 0,
                "comments_found": 0,
                "comments_with_keywords": 0,
                "new_comments": 0,
                "keyword_matches": 0,
            }

        logger.info(f"Используем {len(keywords)} ключевых слов для поиска")

        # Получаем посты группы
        posts_limit = max_posts or int(group.max_posts_to_check)
        posts = await self.vk_api.get_group_posts(
            int(group.vk_id), count=min(posts_limit, 100)
        )

        for post_data in posts:
            try:
                # Сохраняем пост в БД
                post = await self._save_post(group, post_data)

                if post_data["comments"] > 0:
                    # Парсим комментарии к посту
                    comment_stats = await self._parse_post_comments(post, keywords)

                    stats["comments_found"] += comment_stats["total"]
                    stats["comments_with_keywords"] += comment_stats["with_keywords"]
                    stats["new_comments"] += comment_stats["new"]
                    stats["keyword_matches"] += comment_stats["matches"]

                stats["posts_processed"] += 1

                # Небольшая пауза между постами
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Ошибка обработки поста {post_data['id']}: {e}")
                continue

        # Обновляем статистику группы
        group.last_parsed_at = datetime.now(timezone.utc)
        group.total_posts_parsed = (
            int(group.total_posts_parsed) + stats["posts_processed"]
        )
        group.total_comments_found = (
            int(group.total_comments_found) + stats["comments_with_keywords"]
        )

        await self.db.commit()

        logger.info(f"Парсинг группы {group.name} завершён. Статистика: {stats}")
        return stats

    async def _parse_post_comments(
        self, post: VKPost, keywords: list[Keyword]
    ) -> dict[str, int]:
        """Парсинг комментариев конкретного поста"""
        stats = {"total": 0, "with_keywords": 0, "new": 0, "matches": 0}

        # Получаем комментарии через VK API
        comments = await self.vk_api.get_post_comments(
            owner_id=int(post.vk_owner_id), post_id=int(post.vk_id), count=100
        )

        stats["total"] = len(comments)

        for comment_data in comments:
            try:
                # Проверяем, есть ли уже этот комментарий в БД
                existing = await self.db.execute(
                    select(VKComment).where(
                        and_(
                            VKComment.vk_id == comment_data["id"],
                            VKComment.post_id == post.id,
                        )
                    )
                )

                if existing.scalar_one_or_none():
                    continue  # Комментарий уже обработан

                # Ищем ключевые слова в тексте комментария
                matches = await self._find_keywords_in_text(
                    comment_data["text"], keywords
                )

                if matches:
                    # Сохраняем комментарий с найденными ключевыми словами
                    await self._save_comment(post, comment_data, matches)
                    stats["with_keywords"] += 1
                    stats["matches"] += len(matches)

                stats["new"] += 1

            except Exception as e:
                logger.error(f"Ошибка обработки комментария {comment_data['id']}: {e}")
                continue

        return stats

    async def _find_keywords_in_text(
        self, text: str, keywords: list[Keyword]
    ) -> list[tuple[Keyword, str, int]]:
        """
        Поиск ключевых слов в тексте

        Returns:
            Список кортежей (keyword, matched_text, position)
        """
        matches = []
        text_lower = text.lower()

        for keyword in keywords:
            word = keyword.word
            search_text = text if keyword.is_case_sensitive else text_lower
            search_word = word if keyword.is_case_sensitive else word.lower()

            if keyword.is_whole_word:
                # Поиск целых слов с помощью regex
                pattern = r"\b" + re.escape(search_word) + r"\b"
                flags = 0 if keyword.is_case_sensitive else re.IGNORECASE

                for match in re.finditer(pattern, search_text, flags):
                    matches.append((keyword, match.group(), match.start()))
            else:
                # Простой поиск подстроки
                pos = search_text.find(search_word)
                while pos != -1:
                    matches.append((keyword, search_word, pos))
                    pos = search_text.find(search_word, pos + 1)

        return matches

    async def _save_post(self, group: VKGroup, post_data: dict) -> VKPost:
        """Сохранение поста в БД"""
        # Проверяем, есть ли уже этот пост
        result = await self.db.execute(
            select(VKPost).where(
                and_(VKPost.vk_id == post_data["id"], VKPost.group_id == group.id)
            )
        )

        existing_post = result.scalar_one_or_none()
        if existing_post:
            # Обновляем статистику существующего поста
            existing_post.likes_count = post_data["likes"]
            existing_post.reposts_count = post_data["reposts"]
            existing_post.comments_count = post_data["comments"]
            existing_post.views_count = post_data["views"]
            return existing_post

        # Создаём новый пост
        post = VKPost(
            vk_id=post_data["id"],
            vk_owner_id=post_data["owner_id"],
            text=post_data["text"],
            group_id=group.id,
            published_at=post_data["date"],
            likes_count=post_data["likes"],
            reposts_count=post_data["reposts"],
            comments_count=post_data["comments"],
            views_count=post_data["views"],
            has_attachments=post_data["attachments"]["has_attachments"],
            attachments_info=str(post_data["attachments"]),
        )

        self.db.add(post)
        await self.db.flush()  # Получаем ID
        return post

    async def _save_comment(
        self, post: VKPost, comment_data: dict, matches: list[tuple[Keyword, str, int]]
    ) -> VKComment:
        """Сохранение комментария с найденными ключевыми словами"""
        # Получаем информацию об авторе
        author_info = comment_data.get("author", {})

        comment = VKComment(
            vk_id=comment_data["id"],
            text=comment_data["text"],
            post_id=post.id,
            author_id=comment_data["from_id"],
            author_name=author_info.get("name", ""),
            author_screen_name=author_info.get("screen_name", ""),
            author_photo_url=author_info.get("photo_url", ""),
            published_at=comment_data["date"],
            likes_count=comment_data["likes"],
            parent_comment_id=comment_data.get("reply_to_comment"),
            has_attachments=comment_data["attachments"]["has_attachments"],
            attachments_info=str(comment_data["attachments"]),
            matched_keywords_count=len(matches),
            is_processed=True,
            processed_at=datetime.now(timezone.utc),
        )

        self.db.add(comment)
        await self.db.flush()  # Получаем ID

        # Сохраняем совпадения ключевых слов
        for keyword, matched_text, position in matches:
            # Создаём контекст вокруг найденного слова
            context_start = max(0, position - 50)
            context_end = min(
                len(comment_data["text"]), position + len(matched_text) + 50
            )
            context = comment_data["text"][context_start:context_end]

            match = CommentKeywordMatch(
                comment_id=comment.id,
                keyword_id=keyword.id,
                matched_text=matched_text,
                match_position=position,
                match_context=context,
            )

            self.db.add(match)

            # Обновляем статистику ключевого слова
            keyword.total_matches = int(keyword.total_matches) + 1

        return comment

    async def _get_active_keywords(self) -> list[Keyword]:
        """Получение списка активных ключевых слов"""
        result = await self.db.execute(select(Keyword).where(Keyword.is_active))
        return list(result.scalars().all())
