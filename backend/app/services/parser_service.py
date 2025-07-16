"""
Parser Service для обработки комментариев и поиска ключевых слов
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, Coroutine, List, Optional, Tuple

import structlog
from fastapi import HTTPException, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.base import PaginatedResponse, PaginationParams
from app.schemas.parser import (
    GlobalStats,
    ParseStats,
    ParseTaskCreate,
    ParseTaskResponse,
)
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentWithKeywords,
    VKCommentResponse,
)
from app.schemas.vk_group import VKGroupResponse
from app.services.arq_enqueue import enqueue_run_parsing_task
from app.services.morphological_service import morphological_service
from app.services.redis_parser_manager import RedisParserManager
from app.services.vkbottle_service import VKBottleService

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float], Coroutine[None, None, None]]


class ParserService:
    """Сервис для парсинга постов и комментариев VK"""

    def __init__(self, db: AsyncSession, vk_service: VKBottleService):
        self.db = db
        self.vk_service = vk_service
        self.logger = structlog.get_logger(__name__)

    async def start_parsing_task(
        self,
        task_data: ParseTaskCreate,
        parser_manager: RedisParserManager,
    ) -> ParseTaskResponse:
        result = await self.db.execute(
            select(VKGroup).where(VKGroup.id == task_data.group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Группа не найдена",
            )
        if not group.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Группа неактивна",
            )
        task_id = f"parse_{group.id}_{int(datetime.now().timestamp())}"
        task_response = ParseTaskResponse(
            task_id=task_id,
            group_id=task_data.group_id,
            group_name=group.name,
            status="running",
            progress=0.0,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            stats=None,
            error_message=None,
        )
        await parser_manager.start_task(task_response)
        await enqueue_run_parsing_task(
            group_id=task_data.group_id,
            max_posts=task_data.max_posts,
            force_reparse=task_data.force_reparse,
            job_id=task_id,
        )
        self.logger.info(f"Старт задачи парсинга: {task_id}")
        return task_response

    async def filter_comments(
        self,
        search_params: CommentSearchParams,
        pagination: PaginationParams,
    ) -> PaginatedResponse:
        query = select(VKComment).options(
            selectinload(VKComment.post).selectinload(VKPost.group)
        )
        if search_params.group_id:
            query = query.join(VKComment.post).where(
                VKComment.post.has(group_id=search_params.group_id)
            )
        if search_params.keyword_id:
            query = query.join(VKComment.keyword_matches).where(
                VKComment.keyword_matches.any(
                    keyword_id=search_params.keyword_id
                )
            )
        if search_params.author_id:
            query = query.where(VKComment.author_id == search_params.author_id)
        if search_params.date_from:
            query = query.where(
                VKComment.published_at >= search_params.date_from
            )
        if search_params.date_to:
            query = query.where(
                VKComment.published_at <= search_params.date_to
            )
        query = query.where(
            and_(VKComment.is_processed, VKComment.matched_keywords_count > 0)
        )
        query = query.order_by(desc(VKComment.published_at))
        total_result = await self.db.execute(query)
        total = len(total_result.scalars().all())
        paginated_query = query.offset(pagination.skip).limit(pagination.size)
        result = await self.db.execute(paginated_query)
        comments = result.scalars().all()
        items = []
        for comment in comments:
            group = None
            post_vk_id = None
            if comment.post and comment.post.group:
                group = VKGroupResponse.model_validate(comment.post.group)
                post_vk_id = comment.post.vk_id
            comment_data = VKCommentResponse.model_validate(comment)
            comment_data.group = group
            comment_data.post_vk_id = post_vk_id
            items.append(comment_data)
        return PaginatedResponse(
            total=total,
            page=pagination.page,
            size=pagination.size,
            items=items,
        )

    async def get_comment_with_keywords(
        self, comment_id: int
    ) -> CommentWithKeywords:
        result = await self.db.execute(
            select(VKComment)
            .where(VKComment.id == comment_id)
            .options(selectinload(VKComment.keyword_matches))
        )
        comment = result.scalar_one_or_none()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден",
            )
        matched_keywords = []
        keyword_matches = []
        for match in comment.keyword_matches:
            matched_keywords.append(match.keyword.word)
            keyword_matches.append(
                {
                    "keyword": match.keyword.word,
                    "matched_text": match.matched_text,
                    "position": match.match_position,
                    "context": match.match_context,
                }
            )
        comment_data = VKCommentResponse.model_validate(comment)
        return CommentWithKeywords(
            **comment_data.model_dump(),
            matched_keywords=matched_keywords,
            keyword_matches=keyword_matches,
        )

    async def get_global_stats(self) -> GlobalStats:
        groups_result = await self.db.execute(select(func.count(VKGroup.id)))
        total_groups = groups_result.scalar()
        active_groups_result = await self.db.execute(
            select(func.count(VKGroup.id)).where(VKGroup.is_active)
        )
        active_groups = active_groups_result.scalar()
        keywords_result = await self.db.execute(select(func.count(Keyword.id)))
        total_keywords = keywords_result.scalar()
        active_keywords_result = await self.db.execute(
            select(func.count(Keyword.id)).where(Keyword.is_active)
        )
        active_keywords = active_keywords_result.scalar()
        comments_result = await self.db.execute(
            select(func.count(VKComment.id))
        )
        total_comments = comments_result.scalar()
        comments_with_keywords_result = await self.db.execute(
            select(func.count(VKComment.id)).where(
                VKComment.matched_keywords_count > 0
            )
        )
        comments_with_keywords = comments_with_keywords_result.scalar()
        last_parse_result = await self.db.execute(
            select(func.max(VKGroup.last_parsed_at)).where(
                VKGroup.last_parsed_at.isnot(None)
            )
        )
        last_parse_time = last_parse_result.scalar()
        return GlobalStats(
            total_groups=total_groups or 0,
            active_groups=active_groups or 0,
            total_keywords=total_keywords or 0,
            active_keywords=active_keywords or 0,
            total_comments=total_comments or 0,
            comments_with_keywords=comments_with_keywords or 0,
            last_parse_time=last_parse_time,
        )

    async def parse_group_posts(
        self,
        group_id: int,
        max_posts_count: Optional[int] = None,
        force_reparse: bool = False,
        progress_callback: Optional[ProgressCallback] = None,
        task_id: Optional[str] = None,
    ) -> ParseStats:
        """
        Парсит посты группы, их комментарии и ищет ключевые слова.

        Args:
            group_id: ID группы в нашей БД.
            max_posts_count: Максимальное количество постов для обработки.
            force_reparse: Принудительно перепарсить уже обработанные посты.
            progress_callback: Функция обратного вызова для обновления прогресса.
            task_id: Идентификатор задачи для dashboard (опционально)

        Returns:
            Статистика парсинга.
        """
        if task_id:
            logger.info(f"[PARSER] Старт парсинга с task_id={task_id}")
        start_time = datetime.now(timezone.utc)
        group = await self._get_group(group_id)
        if not group or not group.is_active:
            logger.warning(f"Группа {group_id} не найдена или неактивна.")
            return ParseStats(duration_seconds=0)

        logger.info(
            f"Начинаем парсинг группы {group.name} (VK ID: {group.vk_id})"
        )
        stats = ParseStats(duration_seconds=0)
        keywords = await self._get_active_keywords()
        if not keywords:
            logger.warning("Нет активных ключевых слов для поиска.")
            return stats

        logger.info(f"Используем {len(keywords)} ключевых слов для поиска.")
        posts_limit = max_posts_count or group.max_posts_to_check
        posts = await self.vk_service.get_group_posts(
            group.vk_id, count=posts_limit
        )

        total_posts = len(posts)
        for i, post_data in enumerate(posts):
            try:
                post = await self._get_or_create_post(group, post_data)
                # ОТЛАДКА: временно отключаю фильтрацию по parsed_at/updated_at
                # if (
                #     not force_reparse
                #     and post.parsed_at
                #     and post.updated_at
                #     and post.parsed_at > post.updated_at
                # ):
                #     continue

                comments_count = self._get_nested_count(post_data, "comments")
                if comments_count > 0:
                    comment_stats = await self._parse_post_comments(
                        post, keywords, force_reparse
                    )
                    stats.comments_found += comment_stats["total"]
                    stats.comments_with_keywords += comment_stats[
                        "with_keywords"
                    ]
                    stats.new_comments += comment_stats["new"]
                    stats.keyword_matches += comment_stats["matches"]

                post.is_parsed = True
                post.parsed_at = datetime.now(timezone.utc).replace(
                    tzinfo=None
                )
                stats.posts_processed += 1
                if progress_callback:
                    progress = (i + 1) / total_posts
                    await progress_callback(progress)

                await asyncio.sleep(0.1)
            except Exception as e:
                post_id = getattr(post_data, "id", None)
                logger.error(
                    f"Ошибка обработки поста {post_id}: {e}",
                    exc_info=True,
                )
                continue

        await self._update_group_stats(group, stats)
        stats.duration_seconds = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()
        logger.info(
            f"Парсинг группы {group.name} завершён. Статистика: {stats}"
        )
        return stats

    def _get_nested_count(self, data, key: str) -> int:
        """
        Безопасно извлекает значение 'count' из вложенного объекта или словаря.
        API VK может возвращать как объект {'count': X}, так и просто X, либо объект VKBottle.
        """
        value = getattr(data, key, None)
        if value is None and isinstance(data, dict):
            value = data.get(key, {})
        if isinstance(value, dict):
            return value.get("count", 0)
        if hasattr(value, "count"):
            return getattr(value, "count", 0)
        if isinstance(value, int):
            return value
        return 0

    async def _get_group(self, group_id: int) -> Optional[VKGroup]:
        result = await self.db.execute(
            select(VKGroup).where(VKGroup.id == group_id)
        )
        return result.scalar_one_or_none()

    async def _get_active_keywords(self) -> List[Keyword]:
        result = await self.db.execute(
            select(Keyword).where(Keyword.is_active)
        )
        return list(result.scalars().all())

    async def _get_or_create_post(self, group: VKGroup, post_data) -> VKPost:
        # Теперь post_data может быть объектом VKBottle, а не dict
        vk_id = getattr(post_data, "id", None)
        result = await self.db.execute(
            select(VKPost).where(
                VKPost.vk_id == vk_id, VKPost.group_id == group.id
            )
        )
        post = result.scalar_one_or_none()
        if post:
            for field in [
                "likes_count",
                "reposts_count",
                "comments_count",
                "views_count",
            ]:
                # Для likes, reposts, comments, views — пробуем получить через атрибут, если нет — 0
                setattr(
                    post,
                    field,
                    self._get_nested_count(
                        post_data,
                        field[:-6] if field.endswith("_count") else field,
                    ),
                )
            date_value = getattr(post_data, "date", None)
            if isinstance(date_value, datetime):
                post.updated_at = date_value.replace(tzinfo=None)
            elif isinstance(date_value, (int, float)):
                post.updated_at = datetime.fromtimestamp(
                    date_value, tz=timezone.utc
                ).replace(tzinfo=None)
            else:
                logger.warning(
                    f"Неожиданный тип даты: {type(date_value)} — {date_value}"
                )
                post.updated_at = None
            return post

        date_value = getattr(post_data, "date", None)
        if isinstance(date_value, datetime):
            published_at = date_value.replace(tzinfo=None)
            updated_at = date_value.replace(tzinfo=None)
        elif isinstance(date_value, (int, float)):
            published_at = datetime.fromtimestamp(
                date_value, tz=timezone.utc
            ).replace(tzinfo=None)
            updated_at = datetime.fromtimestamp(date_value, tz=timezone.utc)
            updated_at = updated_at.replace(tzinfo=None)
        else:
            logger.warning(
                f"Неожиданный тип даты: {type(date_value)} — {date_value}"
            )
            published_at = None
            updated_at = None

        new_post = VKPost(
            vk_id=getattr(post_data, "id", None),
            vk_owner_id=getattr(post_data, "owner_id", None),
            group_id=group.id,
            text=getattr(post_data, "text", ""),
            likes_count=self._get_nested_count(post_data, "likes"),
            reposts_count=self._get_nested_count(post_data, "reposts"),
            comments_count=self._get_nested_count(post_data, "comments"),
            views_count=self._get_nested_count(post_data, "views"),
            published_at=published_at,
            updated_at=updated_at,
        )
        self.db.add(new_post)
        await self.db.flush()
        return new_post

    async def _parse_post_comments(
        self,
        post: VKPost,
        keywords: list[Keyword],
        force_reparse: bool = False,
    ) -> dict[str, int]:
        stats = {"total": 0, "with_keywords": 0, "new": 0, "matches": 0}
        owner_id = getattr(post.group, "vk_id", None)
        post_id = getattr(post, "vk_id", None)
        if owner_id is None or post_id is None:
            logger.warning(
                f"owner_id или post_id не определены для поста! post={post}"
            )
            return stats
        comments = await self.vk_service.get_post_comments(
            owner_id=int(owner_id), post_id=int(post_id)
        )
        stats["total"] = len(comments)

        for comment_data in comments:
            try:
                if not force_reparse:
                    comment_vk_id = getattr(comment_data, "id", None)
                    existing = await self.db.execute(
                        select(VKComment).where(
                            VKComment.vk_id == comment_vk_id
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                text = getattr(comment_data, "text", "")
                matches = self._find_keywords_in_text(text, keywords)
                if matches:
                    await self._save_comment(post, comment_data, matches)
                    stats["with_keywords"] += 1
                    stats["matches"] += len(matches)
                stats["new"] += 1
            except Exception as e:
                comment_id = getattr(comment_data, "id", None)
                logger.error(
                    f"Ошибка обработки комментария {comment_id}: {e}",
                    exc_info=True,
                )
                continue
        return stats

    def _find_keywords_in_text(
        self, text: str, keywords: list[Keyword]
    ) -> list[tuple[Keyword, str, int]]:
        """
        Найти ключевые слова в тексте с использованием морфологического анализа.

        Args:
            text: Текст для поиска
            keywords: Список ключевых слов

        Returns:
            Список кортежей (ключевое_слово, найденный_текст, позиция)
        """
        matches: List[Tuple[Keyword, str, int]] = []

        for keyword in keywords:
            # Используем морфологический анализ для поиска всех форм слова
            morphological_matches = (
                morphological_service.find_morphological_matches(
                    text=text,
                    keyword=keyword.word,
                    case_sensitive=keyword.is_case_sensitive,
                    whole_word=keyword.is_whole_word,
                )
            )

            # Добавляем найденные совпадения
            for matched_text, position in morphological_matches:
                matches.append((keyword, matched_text, position))

        return matches

    async def _get_author_info(self, author_id: int) -> tuple[str, str, str]:
        self.vk_service.logger.info(
            f"Получаю данные об авторе VK: {author_id}"
        )
        if author_id is None:
            return "", "", ""
        if author_id > 0:
            users = await self.vk_service.api.users.get(
                user_ids=[author_id], fields=["screen_name", "photo_100"]
            )
            if users:
                user = users[0]
                name = f"{user.first_name} {user.last_name}"
                screen_name = getattr(user, "screen_name", "")
                photo_url = getattr(user, "photo_100", "")
                self.vk_service.logger.info(
                    f"User info: {name}, {screen_name}, {photo_url}"
                )
                return name, screen_name, photo_url
        else:
            group_id = abs(author_id)
            groups = await self.vk_service.api.groups.get_by_id(
                group_ids=[group_id], fields=["screen_name", "photo_100"]
            )
            if groups:
                group = groups[0]
                name = group.name
                screen_name = getattr(group, "screen_name", "")
                photo_url = getattr(group, "photo_100", "")
                self.vk_service.logger.info(
                    f"Group info: {name}, {screen_name}, {photo_url}"
                )
                return name, screen_name, photo_url
        self.vk_service.logger.warning(
            f"Не удалось получить данные об авторе VK: {author_id}"
        )
        return "", "", ""

    async def _save_comment(
        self, post: VKPost, comment_data, matches: list
    ) -> VKComment:
        author_id = getattr(comment_data, "from_id", None)
        (
            author_name,
            author_screen_name,
            author_photo_url,
        ) = await self._get_author_info(author_id)
        new_comment = VKComment(
            vk_id=getattr(comment_data, "id", None),
            post_id=post.id,
            text=getattr(comment_data, "text", ""),
            published_at=datetime.fromtimestamp(
                getattr(comment_data, "date", 0), tz=timezone.utc
            ).replace(tzinfo=None),
            author_id=author_id,
            author_name=author_name,
            author_screen_name=author_screen_name,
            author_photo_url=author_photo_url,
            is_processed=True,
            matched_keywords_count=len(matches),
            processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self.db.add(new_comment)
        await self.db.flush()

        for keyword, matched_text, position in matches:
            match = CommentKeywordMatch(
                comment_id=new_comment.id,
                keyword_id=keyword.id,
                matched_text=matched_text,
                match_position=position,
                found_at=datetime.now(timezone.utc),
            )
            self.db.add(match)

        await self.db.flush()
        return new_comment

    async def _update_group_stats(
        self, group: VKGroup, stats: ParseStats
    ) -> None:
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
            "Метод parse_group_comments устарел. "
            "Используйте parse_group_posts."
        )
        stats = await self.parse_group_posts(
            group_id, max_posts_count=max_posts
        )
        return stats.model_dump()

    async def get_parsing_status(self, task_id: str) -> dict:
        """Получить статус задачи парсинга."""
        # Убрать обращение к self.redis_manager, если его нет
        logger.warning(
            "redis_manager не определён в ParserService. Возвращаю пустой статус."
        )
        return {}

    async def run_parser_for_all_groups(self) -> dict:
        return {}
