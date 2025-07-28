"""
Parser Service для обработки комментариев и поиска ключевых слов
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

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
from app.services.vk_api_service import VKAPIService

logger = logging.getLogger(__name__)

# Типы для улучшения читаемости
ProgressCallback = Callable[[float], Coroutine[None, None, None]]
CommentStats = Dict[str, int]
KeywordMatch = Tuple[Keyword, str, int]  # (keyword, matched_text, position)
VKPostData = Dict[str, Any]  # Данные поста от VK API


class ParserService:
    """
    Сервис для парсинга постов и комментариев VK

    Основные возможности:
    - Парсинг постов и комментариев групп
    - Поиск ключевых слов в комментариях
    - Управление задачами парсинга
    - Статистика и отчеты
    """

    def __init__(self, db: AsyncSession, vk_service: VKAPIService):
        self.db = db
        self.vk_service = vk_service
        self.logger = structlog.get_logger(__name__)

    async def start_parsing_task(
        self,
        task_data: ParseTaskCreate,
        parser_manager: RedisParserManager,
    ) -> ParseTaskResponse:
        """
        Запускает задачу парсинга группы

        Args:
            task_data: Данные задачи парсинга
            parser_manager: Менеджер для управления задачами

        Returns:
            Информация о запущенной задаче

        Raises:
            HTTPException: Если группа не найдена или неактивна
        """
        group = await self._get_group(task_data.group_id)
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

        task_id = self._generate_task_id(group.id)
        task_response = self._create_task_response(task_data, group, task_id)

        await parser_manager.start_task(task_response)
        await self._enqueue_parsing_task(task_data, task_id)

        self.logger.info(
            "Задача парсинга запущена", task_id=task_id, group_id=group.id
        )
        return task_response

    async def filter_comments(
        self,
        search_params: CommentSearchParams,
        pagination: PaginationParams,
    ) -> PaginatedResponse[VKCommentResponse]:
        """
        Фильтрует комментарии по заданным параметрам

        Args:
            search_params: Параметры поиска
            pagination: Параметры пагинации

        Returns:
            Отфильтрованные комментарии с пагинацией
        """
        self.logger.info(
            "Начало фильтрации комментариев",
            search_params=search_params.model_dump(),
            pagination=pagination.model_dump(),
            order_by=search_params.order_by,
            order_dir=search_params.order_dir,
        )

        query = self._build_comments_query(search_params)

        # Получаем общее количество
        total_result = await self.db.execute(query)
        total = len(total_result.scalars().all())

        self.logger.info(
            "Общее количество комментариев",
            total=total,
            skip=pagination.skip,
            limit=pagination.size,
        )

        # Применяем пагинацию
        paginated_query = query.offset(pagination.skip).limit(pagination.size)
        result = await self.db.execute(paginated_query)
        comments = result.scalars().all()

        self.logger.info(
            "Результаты фильтрации",
            total_comments=len(comments),
            first_comment_id=comments[0].id if comments else None,
            last_comment_id=comments[-1].id if comments else None,
            first_comment_has_post=(
                comments[0].post is not None if comments else None
            ),
            first_comment_has_group=(
                comments[0].post.group is not None
                if comments and comments[0].post
                else None
            ),
            order_by=search_params.order_by,
            order_dir=search_params.order_dir,
            first_comment_published_at=(
                comments[0].published_at if comments else None
            ),
            first_comment_author_name=(
                comments[0].author_name if comments else None
            ),
        )

        # Преобразуем в ответы API
        items = [
            self._convert_comment_to_response(comment) for comment in comments
        ]

        return PaginatedResponse(
            total=total,
            page=pagination.page,
            size=pagination.size,
            items=items,
        )

    async def get_comment_with_keywords(
        self, comment_id: int
    ) -> CommentWithKeywords:
        """
        Получает комментарий с детальной информацией о найденных ключевых словах

        Args:
            comment_id: ID комментария

        Returns:
            Комментарий с информацией о ключевых словах

        Raises:
            HTTPException: Если комментарий не найден
        """
        comment = await self._get_comment_with_matches(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден",
            )

        return self._build_comment_with_keywords_response(comment)

    async def get_global_stats(self) -> GlobalStats:
        """Получает глобальную статистику системы"""
        stats = await self._calculate_global_stats()
        return GlobalStats(**stats)

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
            group_id: ID группы в нашей БД
            max_posts_count: Максимальное количество постов для обработки
            force_reparse: Принудительно перепарсить уже обработанные посты
            progress_callback: Функция обратного вызова для обновления прогресса
            task_id: Идентификатор задачи для dashboard (опционально)

        Returns:
            Статистика парсинга
        """
        start_time = datetime.now(timezone.utc)

        self.logger.info(
            "Начало парсинга группы",
            group_id=group_id,
            max_posts=max_posts_count,
            force_reparse=force_reparse,
            task_id=task_id,
        )

        group = await self._get_group(group_id)
        if not group or not group.is_active:
            self.logger.warning(
                "Группа не найдена или неактивна", group_id=group_id
            )
            return ParseStats(duration_seconds=0)

        self.logger.info(
            "Группа найдена",
            group_id=group.id,
            vk_id=group.vk_id,
            name=group.name,
            screen_name=group.screen_name,
        )

        stats = ParseStats(duration_seconds=0)
        keywords = await self._get_active_keywords()
        if not keywords:
            self.logger.warning("Нет активных ключевых слов для поиска")
            return stats

        self.logger.info(
            "Используем ключевых слов для поиска", count=len(keywords)
        )

        posts_limit = max_posts_count or group.max_posts_to_check
        posts = await self.vk_service.get_group_posts(
            group.vk_id, count=posts_limit
        )

        self.logger.info(
            "Получены посты от VK API",
            group_id=group.id,
            group_vk_id=group.vk_id,
            posts_count=len(posts),
        )

        if not posts:
            self.logger.info("Нет постов для обработки", group_id=group.id)
            return stats

        total_posts = len(posts)
        for i, post_data in enumerate(posts):
            try:
                post = await self._get_or_create_post(group, post_data)

                # Обрабатываем комментарии если они есть
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

                # Обновляем статус поста
                post.is_parsed = True
                post.parsed_at = datetime.now(timezone.utc).replace(
                    tzinfo=None
                )
                stats.posts_processed += 1

                # Обновляем прогресс
                if progress_callback:
                    progress = (i + 1) / total_posts
                    await progress_callback(progress)

                await asyncio.sleep(
                    0.1
                )  # Небольшая задержка для избежания rate limiting

            except Exception as e:
                post_id = getattr(post_data, "id", None)
                self.logger.error(
                    "Ошибка обработки поста",
                    post_id=post_id,
                    group_id=group_id,
                    error=str(e),
                    exc_info=True,
                )
                continue

        await self._update_group_stats(group, stats)

        # Обновляем статистику ключевых слов
        await self._update_keywords_stats()

        stats.duration_seconds = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()

        self.logger.info(
            "Парсинг группы завершен",
            group_name=group.name,
            stats=stats.model_dump(),
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

    async def _get_or_create_post(
        self, group: VKGroup, post_data: VKPostData
    ) -> VKPost:
        """
        Получает существующий пост или создает новый

        Args:
            group: Группа VK
            post_data: Данные поста от VK API

        Returns:
            Объект поста VKPost

        Raises:
            ValueError: Если не удалось получить vk_id или owner_id
        """
        # Извлекаем ID поста из различных возможных полей
        vk_id = (
            post_data.get("id")
            or post_data.get("post_id")
            or post_data.get("vk_id")
        )
        owner_id = post_data.get("owner_id") or group.vk_id

        # Валидируем данные
        if vk_id is None:
            self.logger.error(
                "vk_id не найден в данных поста", post_data=post_data
            )
            raise ValueError(
                f"Не удалось получить vk_id из данных поста: {post_data}"
            )

        if owner_id is None:
            self.logger.error(
                "owner_id не найден в данных поста", post_data=post_data
            )
            raise ValueError(
                f"Не удалось получить owner_id из данных поста: {post_data}"
            )

        # Преобразуем в числа
        try:
            vk_id = int(vk_id)
            owner_id = int(owner_id)
        except (ValueError, TypeError) as e:
            self.logger.error(
                "Некорректные типы данных для vk_id или owner_id",
                vk_id=vk_id,
                owner_id=owner_id,
                error=str(e),
            )
            raise ValueError(
                f"Некорректные типы данных для vk_id или owner_id: {e}"
            )

        # Ищем существующий пост
        result = await self.db.execute(
            select(VKPost).where(
                VKPost.vk_id == vk_id, VKPost.group_id == group.id
            )
        )
        post = result.scalar_one_or_none()

        if post:
            return await self._update_existing_post(post, post_data)
        else:
            return await self._create_new_post(
                group, post_data, vk_id, owner_id
            )

    async def _update_existing_post(
        self, post: VKPost, post_data: VKPostData
    ) -> VKPost:
        """Обновляет существующий пост новыми данными"""
        # Обновляем счетчики
        for field in [
            "likes_count",
            "reposts_count",
            "comments_count",
            "views_count",
        ]:
            api_field = field[:-6] if field.endswith("_count") else field
            setattr(post, field, self._get_nested_count(post_data, api_field))

        # Обновляем дату
        date_value = post_data.get("date")
        if isinstance(date_value, datetime):
            post.updated_at = date_value.replace(tzinfo=timezone.utc)
        elif isinstance(date_value, (int, float)):
            post.updated_at = datetime.fromtimestamp(
                date_value, tz=timezone.utc
            )
        else:
            self.logger.warning(
                "Неожиданный тип даты",
                date_type=type(date_value),
                date_value=date_value,
            )

        return post

    async def _create_new_post(
        self, group: VKGroup, post_data: VKPostData, vk_id: int, owner_id: int
    ) -> VKPost:
        """Создает новый пост"""
        # Обрабатываем дату публикации
        date_value = post_data.get("date")
        if isinstance(date_value, datetime):
            published_at = date_value.replace(tzinfo=timezone.utc)
            updated_at = date_value.replace(tzinfo=timezone.utc)
        elif isinstance(date_value, (int, float)):
            published_at = datetime.fromtimestamp(date_value, tz=timezone.utc)
            updated_at = published_at
        else:
            self.logger.warning(
                "Неожиданный тип даты, используем текущее время",
                date_type=type(date_value),
                date_value=date_value,
            )
            published_at = datetime.now(timezone.utc)
            updated_at = published_at

        # Создаем новый пост
        new_post = VKPost(
            vk_id=vk_id,
            vk_owner_id=owner_id,
            group_id=group.id,
            text=post_data.get("text", ""),
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
    ) -> CommentStats:
        stats = {"total": 0, "with_keywords": 0, "new": 0, "matches": 0}
        owner_id = getattr(post.group, "vk_id", None)
        post_id = getattr(post, "vk_id", None)
        if owner_id is None or post_id is None:
            logger.warning(
                f"owner_id или post_id не определены для поста! post={post}"
            )
            return stats
        comments = await self.vk_service.get_all_post_comments(
            owner_id=int(owner_id), post_id=int(post_id)
        )
        stats["total"] = len(comments)

        for comment_data in comments:
            try:
                if not force_reparse:
                    comment_vk_id = comment_data.get("id")
                    existing = await self.db.execute(
                        select(VKComment).where(
                            VKComment.vk_id == comment_vk_id
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                text = comment_data.get("text", "")
                matches = self._find_keywords_in_text(text, keywords)
                if matches:
                    await self._save_comment(post, comment_data, matches)
                    stats["with_keywords"] += 1
                    stats["matches"] += len(matches)
                stats["new"] += 1
            except Exception as e:
                comment_id = comment_data.get("id")
                logger.error(
                    f"Ошибка обработки комментария {comment_id}: {e}",
                    exc_info=True,
                )
                continue
        return stats

    def _find_keywords_in_text(
        self, text: str, keywords: list[Keyword]
    ) -> list[KeywordMatch]:
        """
        Найти ключевые слова в тексте с использованием морфологического анализа.

        Args:
            text: Текст для поиска
            keywords: Список ключевых слов

        Returns:
            Список кортежей (ключевое_слово, найденный_текст, позиция)
        """
        matches: List[KeywordMatch] = []

        self.logger.debug(
            "Поиск ключевых слов в тексте",
            text_length=len(text),
            keywords_count=len(keywords),
            text_preview=text[:100] + "..." if len(text) > 100 else text,
        )

        for keyword in keywords:
            self.logger.debug(
                "Обработка ключевого слова",
                keyword_id=keyword.id,
                keyword_word=keyword.word,
                is_case_sensitive=keyword.is_case_sensitive,
                is_whole_word=keyword.is_whole_word,
            )

            # Используем морфологический анализ для поиска всех форм слова
            morphological_matches = (
                morphological_service.find_morphological_matches(
                    text=text,
                    keyword=keyword.word,
                    case_sensitive=keyword.is_case_sensitive,
                    whole_word=keyword.is_whole_word,
                )
            )

            self.logger.debug(
                "Результаты морфологического поиска",
                keyword_word=keyword.word,
                matches_count=len(morphological_matches),
                matches=morphological_matches,
            )

            # Добавляем найденные совпадения
            for matched_text, position in morphological_matches:
                matches.append((keyword, matched_text, position))

        self.logger.info(
            "Завершен поиск ключевых слов",
            total_matches=len(matches),
            unique_keywords=len(set(match[0].id for match in matches)),
        )

        return matches

    async def _get_author_info(self, author_id: int) -> tuple[str, str, str]:
        """
        Получает информацию об авторе комментария

        Args:
            author_id: ID автора в VK

        Returns:
            Кортеж (имя, screen_name, photo_url)
        """
        if author_id is None:
            self.logger.warning("author_id is None")
            return "", "", ""

        self.logger.info("Получаю данные об авторе VK", author_id=author_id)

        if author_id > 0:
            # Пользователь
            try:
                self.logger.info(
                    "Запрос данных пользователя", author_id=author_id
                )
                user_info = await self.vk_service.get_user_info(author_id)
                self.logger.info(
                    "Ответ VK API для пользователя", user_info=user_info
                )

                if user_info:
                    # Формируем полное имя из first_name и last_name
                    first_name = user_info.get("first_name", "")
                    last_name = user_info.get("last_name", "")
                    name = f"{first_name} {last_name}".strip()

                    # Получаем screen_name (может быть пустым)
                    screen_name = user_info.get("screen_name", "")

                    # Получаем URL фото
                    photo_url = user_info.get("photo_100", "")

                    self.logger.info(
                        "Информация о пользователе получена",
                        author_id=author_id,
                        name=name,
                        screen_name=screen_name,
                        photo_url=photo_url,
                    )

                    # Возвращаем реальные данные, даже если screen_name пустой
                    return name, screen_name, photo_url
                else:
                    self.logger.warning(
                        "VK API вернул пустые данные пользователя",
                        author_id=author_id,
                    )
            except Exception as e:
                self.logger.error(
                    "Ошибка получения данных пользователя",
                    author_id=author_id,
                    error=str(e),
                    error_type=type(e).__name__,
                )

            # Fallback только если VK API недоступен или вернул ошибку
            self.logger.warning(
                "Используем fallback для пользователя - VK API недоступен",
                author_id=author_id,
            )
            return f"Пользователь {author_id}", f"id{author_id}", ""
        else:
            # Группа
            group_id = abs(author_id)
            try:
                self.logger.info("Запрос данных группы", group_id=group_id)
                group_info = await self.vk_service.get_group_info(group_id)
                self.logger.info(
                    "Ответ VK API для группы", group_info=group_info
                )

                if group_info:
                    name = group_info.get("name", "")
                    screen_name = group_info.get("screen_name", "")
                    photo_url = group_info.get("photo_100", "")

                    self.logger.info(
                        "Информация о группе получена",
                        group_id=group_id,
                        name=name,
                        screen_name=screen_name,
                        photo_url=photo_url,
                    )

                    # Возвращаем реальные данные группы
                    return name, screen_name, photo_url
                else:
                    self.logger.warning(
                        "VK API вернул пустые данные группы", group_id=group_id
                    )
            except Exception as e:
                self.logger.error(
                    "Ошибка получения данных группы",
                    group_id=group_id,
                    error=str(e),
                    error_type=type(e).__name__,
                )

            # Fallback только если VK API недоступен или вернул ошибку
            self.logger.warning(
                "Используем fallback для группы - VK API недоступен",
                group_id=group_id,
            )
            return f"Группа {group_id}", f"id{group_id}", ""

        self.logger.warning(
            "Не удалось получить данные об авторе VK", author_id=author_id
        )
        # Финальный fallback только в крайнем случае
        if author_id > 0:
            return f"Пользователь {author_id}", f"id{author_id}", ""
        else:
            return f"Группа {abs(author_id)}", f"id{abs(author_id)}", ""

    async def _save_comment(
        self,
        post: VKPost,
        comment_data: Dict[str, Any],
        matches: List[KeywordMatch],
    ) -> VKComment:
        """
        Сохраняет комментарий с найденными ключевыми словами

        Args:
            post: Пост VK
            comment_data: Данные комментария от VK API
            matches: Список найденных ключевых слов

        Returns:
            Сохраненный комментарий
        """
        author_id = comment_data.get("from_id")
        if author_id is None:
            author_name, author_screen_name, author_photo_url = "", "", ""
        else:
            author_name, author_screen_name, author_photo_url = (
                await self._get_author_info(author_id)
            )

        # Создаем комментарий
        new_comment = VKComment(
            vk_id=comment_data.get("id"),
            post_id=post.id,
            post_vk_id=post.vk_id,  # Добавляем VK ID поста для формирования ссылок
            text=comment_data.get("text", ""),
            published_at=datetime.fromtimestamp(
                comment_data.get("date", 0), tz=timezone.utc
            ),
            author_id=author_id,
            author_name=author_name,
            author_screen_name=author_screen_name,
            author_photo_url=author_photo_url,
            is_processed=True,
            matched_keywords_count=len(matches),
            processed_at=datetime.now(timezone.utc),
        )

        self.db.add(new_comment)
        await self.db.flush()

        # Сохраняем совпадения ключевых слов
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
        """Обновляет статистику группы после парсинга"""
        group.last_parsed_at = datetime.now(timezone.utc)
        group.total_posts_parsed += stats.posts_processed
        group.total_comments_found += stats.comments_found
        await self.db.commit()

    async def _update_keywords_stats(self) -> None:
        """Обновляет статистику ключевых слов на основе совпадений"""
        from sqlalchemy import func

        # Подсчитываем количество совпадений для каждого ключевого слова
        result = await self.db.execute(
            select(
                CommentKeywordMatch.keyword_id,
                func.count(CommentKeywordMatch.id).label("match_count"),
            ).group_by(CommentKeywordMatch.keyword_id)
        )

        keyword_stats = result.all()

        # Обновляем total_matches для каждого ключевого слова
        for keyword_id, match_count in keyword_stats:
            await self.db.execute(
                select(Keyword).where(Keyword.id == keyword_id)
            )
            keyword_result = await self.db.execute(
                select(Keyword).where(Keyword.id == keyword_id)
            )
            keyword = keyword_result.scalar_one_or_none()
            if keyword:
                keyword.total_matches = match_count

        await self.db.commit()

    # Устаревшие методы - помечены как deprecated
    async def parse_group_comments(
        self, group_id: int, max_posts: Optional[int] = None
    ) -> Dict[str, int]:
        """
        [DEPRECATED] Парсинг комментариев группы

        Используйте parse_group_posts вместо этого метода
        """
        self.logger.warning(
            "Метод parse_group_comments устарел. Используйте parse_group_posts."
        )
        stats = await self.parse_group_posts(
            group_id, max_posts_count=max_posts
        )
        return stats.model_dump()

    async def get_parsing_status(self, task_id: str) -> Dict[str, Any]:
        """
        [DEPRECATED] Получить статус задачи парсинга

        Этот метод больше не используется, так как статус управляется через Redis
        """
        self.logger.warning(
            "Метод get_parsing_status устарел. Статус управляется через Redis."
        )
        return {}

    async def run_parser_for_all_groups(self) -> Dict[str, Any]:
        """
        [DEPRECATED] Запустить парсер для всех групп

        Используйте мониторинг вместо этого метода
        """
        self.logger.warning(
            "Метод run_parser_for_all_groups устарел. Используйте мониторинг."
        )
        return {}

    # Вспомогательные методы для улучшения структуры

    def _generate_task_id(self, group_id: int) -> str:
        """Генерирует уникальный ID задачи"""
        timestamp = int(datetime.now().timestamp())
        return f"parse_{group_id}_{timestamp}"

    def _create_task_response(
        self, task_data: ParseTaskCreate, group: VKGroup, task_id: str
    ) -> ParseTaskResponse:
        """Создает объект ответа задачи"""
        return ParseTaskResponse(
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

    async def _enqueue_parsing_task(
        self, task_data: ParseTaskCreate, task_id: str
    ) -> None:
        """Добавляет задачу парсинга в очередь"""
        await enqueue_run_parsing_task(
            group_id=task_data.group_id,
            max_posts=task_data.max_posts,
            force_reparse=task_data.force_reparse,
            job_id=task_id,
        )

    def _build_comments_query(self, search_params: CommentSearchParams):
        """Строит SQL запрос для фильтрации комментариев"""
        query = select(VKComment).options(
            selectinload(VKComment.post).selectinload(VKPost.group),
            selectinload(VKComment.keyword_matches).selectinload(
                CommentKeywordMatch.keyword
            ),
        )

        # Применяем фильтры
        if search_params.text:
            query = query.where(VKComment.text.like(f"%{search_params.text}%"))
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
        if search_params.author_screen_name:
            query = query.where(
                VKComment.author_screen_name.in_(
                    search_params.author_screen_name
                )
            )
        if search_params.date_from:
            query = query.where(
                VKComment.published_at >= search_params.date_from
            )
        if search_params.date_to:
            query = query.where(
                VKComment.published_at <= search_params.date_to
            )

        # Новые фильтры для статуса просмотра и архивирования
        if search_params.is_viewed is not None:
            query = query.where(VKComment.is_viewed == search_params.is_viewed)
        if search_params.is_archived is not None:
            query = query.where(
                VKComment.is_archived == search_params.is_archived
            )

        # Базовые условия
        query = query.where(
            and_(VKComment.is_processed, VKComment.matched_keywords_count > 0)
        )

        # Применяем сортировку
        if search_params.order_by and search_params.order_dir:
            if search_params.order_dir.lower() == "desc":
                if search_params.order_by == "published_at":
                    query = query.order_by(desc(VKComment.published_at))
                elif search_params.order_by == "author_name":
                    query = query.order_by(desc(VKComment.author_name))
                elif search_params.order_by == "likes_count":
                    query = query.order_by(desc(VKComment.likes_count))
                elif search_params.order_by == "matched_keywords_count":
                    query = query.order_by(
                        desc(VKComment.matched_keywords_count)
                    )
                elif search_params.order_by == "created_at":
                    query = query.order_by(desc(VKComment.created_at))
                else:
                    query = query.order_by(desc(VKComment.published_at))
            else:
                if search_params.order_by == "published_at":
                    query = query.order_by(VKComment.published_at)
                elif search_params.order_by == "author_name":
                    query = query.order_by(VKComment.author_name)
                elif search_params.order_by == "likes_count":
                    query = query.order_by(VKComment.likes_count)
                elif search_params.order_by == "matched_keywords_count":
                    query = query.order_by(VKComment.matched_keywords_count)
                elif search_params.order_by == "created_at":
                    query = query.order_by(VKComment.created_at)
                else:
                    query = query.order_by(VKComment.published_at)
        else:
            # Сортировка по умолчанию
            query = query.order_by(desc(VKComment.published_at))

        return query

    def _convert_comment_to_response(
        self, comment: VKComment
    ) -> VKCommentResponse:
        """Преобразует модель комментария в ответ API"""
        group = None
        post_vk_id = None

        # Используем post_vk_id из базы данных, если он есть
        if hasattr(comment, "post_vk_id") and comment.post_vk_id:
            post_vk_id = comment.post_vk_id
        elif comment.post and comment.post.group:
            group = VKGroupResponse.model_validate(comment.post.group)
            post_vk_id = comment.post.vk_id

        # Если у нас есть post_vk_id, но нет группы, попробуем получить группу из поста
        if post_vk_id and not group and comment.post and comment.post.group:
            group = VKGroupResponse.model_validate(comment.post.group)

        # Извлекаем ключевые слова из совпадений
        matched_keywords = []
        if comment.keyword_matches:
            for match in comment.keyword_matches:
                if match.keyword:
                    matched_keywords.append(match.keyword.word)

        # Отладочная информация
        self.logger.info(
            "Converting comment to response",
            comment_id=comment.id,
            post_vk_id=post_vk_id,
            has_post=comment.post is not None,
            has_group=comment.post.group if comment.post else None,
            group_name=(
                comment.post.group.name
                if comment.post and comment.post.group
                else None
            ),
            matched_keywords_count=len(matched_keywords),
        )

        comment_data = VKCommentResponse.model_validate(comment)
        comment_data.group = group
        comment_data.post_vk_id = (
            post_vk_id if post_vk_id is not None else None
        )
        comment_data.matched_keywords = matched_keywords

        return comment_data

    async def _get_comment_with_matches(
        self, comment_id: int
    ) -> Optional[VKComment]:
        """Получает комментарий с загруженными совпадениями ключевых слов"""
        result = await self.db.execute(
            select(VKComment)
            .where(VKComment.id == comment_id)
            .options(selectinload(VKComment.keyword_matches))
        )
        return result.scalar_one_or_none()

    def _build_comment_with_keywords_response(
        self, comment: VKComment
    ) -> CommentWithKeywords:
        """Строит ответ с информацией о ключевых словах"""
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

    async def _calculate_global_stats(self) -> Dict[str, Any]:
        """Вычисляет глобальную статистику"""
        # Группы
        groups_result = await self.db.execute(select(func.count(VKGroup.id)))
        total_groups = groups_result.scalar()

        active_groups_result = await self.db.execute(
            select(func.count(VKGroup.id)).where(VKGroup.is_active)
        )
        active_groups = active_groups_result.scalar()

        # Ключевые слова
        keywords_result = await self.db.execute(select(func.count(Keyword.id)))
        total_keywords = keywords_result.scalar()

        active_keywords_result = await self.db.execute(
            select(func.count(Keyword.id)).where(Keyword.is_active)
        )
        active_keywords = active_keywords_result.scalar()

        # Комментарии
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

        # Последний парсинг
        last_parse_result = await self.db.execute(
            select(func.max(VKGroup.last_parsed_at)).where(
                VKGroup.last_parsed_at.isnot(None)
            )
        )
        last_parse_time = last_parse_result.scalar()

        return {
            "total_groups": total_groups or 0,
            "active_groups": active_groups or 0,
            "total_keywords": total_keywords or 0,
            "active_keywords": active_keywords or 0,
            "total_comments": total_comments or 0,
            "comments_with_keywords": comments_with_keywords or 0,
            "last_parse_time": last_parse_time,
        }
