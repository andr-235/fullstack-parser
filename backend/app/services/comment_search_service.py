"""
CommentSearchService - сервис для поиска и фильтрации комментариев

Принципы SOLID:
- Single Responsibility: только поиск и фильтрация комментариев
- Open/Closed: легко добавлять новые фильтры
- Liskov Substitution: можно заменить на другую реализацию поиска
- Interface Segregation: чистый интерфейс для поиска
- Dependency Inversion: зависит от абстракций (AsyncSession)
"""

import logging
from typing import List, Optional

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.base import PaginatedResponse
from app.schemas.vk_comment import CommentSearchParams, CommentWithKeywords

logger = logging.getLogger(__name__)


class CommentSearchService:
    """
    Сервис для поиска и фильтрации комментариев VK.

    Предоставляет высокоуровневый интерфейс для:
    - Поиска комментариев по различным критериям
    - Фильтрации комментариев по ключевым словам
    - Получения комментариев с пагинацией
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса поиска.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db

    async def search_comments(
        self,
        search_params: CommentSearchParams,
        limit: int = 50,
        offset: int = 0,
        include_group: bool = False,
    ) -> List[CommentWithKeywords]:
        """
        Поиск комментариев по различным критериям.

        Args:
            search_params: Параметры поиска
            limit: Максимальное количество результатов
            offset: Смещение для пагинации
            include_group: Включить информацию о группе

        Returns:
            Список найденных комментариев с ключевыми словами
        """
        try:
            # Строим базовый запрос
            query = self._build_search_query(search_params, include_group)

            # Применяем сортировку
            query = self._apply_sorting(query, search_params)

            # Применяем пагинацию
            query = query.limit(limit).offset(offset)

            # Выполняем запрос
            result = await self.db.execute(query)
            comments = result.scalars().all()

            logger.info(
                f"Search completed: found {len(comments)} comments",
                search_params=search_params.model_dump(exclude_unset=True),
                limit=limit,
                offset=offset,
            )

            return [
                self._comment_to_response_with_keywords(comment)
                for comment in comments
            ]

        except Exception as e:
            logger.error(f"Error searching comments: {e}")
            raise

    async def get_comments_by_group(
        self,
        group_id: int,
        limit: int = 50,
        offset: int = 0,
        include_group: bool = False,
    ) -> PaginatedResponse:
        """
        Получить комментарии группы с пагинацией.

        Args:
            group_id: ID группы VK
            limit: Максимальное количество комментариев
            offset: Смещение для пагинации
            include_group: Включить информацию о группе

        Returns:
            Пагинированный ответ с комментариями группы
        """
        try:
            # Строим запрос для подсчета общего количества
            count_query = (
                select(VKComment)
                .join(VKPost, VKComment.post_id == VKPost.id)
                .where(VKPost.group_id == group_id)
            )

            count_result = await self.db.execute(count_query)
            total = len(count_result.scalars().all())

            # Строим запрос для получения комментариев
            query = (
                select(VKComment)
                .join(VKPost, VKComment.post_id == VKPost.id)
                .where(VKPost.group_id == group_id)
                .order_by(desc(VKComment.published_at))
                .limit(limit)
                .offset(offset)
            )

            if include_group:
                query = query.options(
                    selectinload(VKComment.post).selectinload(VKPost.group)
                )

            result = await self.db.execute(query)
            comments = result.scalars().all()

            logger.info(
                f"Retrieved {len(comments)} comments for group {group_id}",
                group_id=group_id,
                total=total,
                limit=limit,
                offset=offset,
            )

            return PaginatedResponse(
                total=total,
                page=(offset // limit) + 1,
                size=limit,
                items=[
                    self._comment_to_response(comment) for comment in comments
                ],
            )

        except Exception as e:
            logger.error(f"Error getting comments for group {group_id}: {e}")
            raise

    async def filter_by_keywords(
        self,
        comments: List[VKComment],
        keywords: List[str],
        case_sensitive: bool = False,
    ) -> List[VKComment]:
        """
        Фильтрация комментариев по ключевым словам.

        Args:
            comments: Список комментариев для фильтрации
            keywords: Список ключевых слов
            case_sensitive: Учитывать регистр

        Returns:
            Отфильтрованный список комментариев
        """
        try:
            if not keywords:
                return comments

            filtered_comments = []

            for comment in comments:
                comment_text = comment.text
                if not case_sensitive:
                    comment_text = comment_text.lower()
                    keywords_lower = [kw.lower() for kw in keywords]

                # Проверяем, содержит ли текст хотя бы одно ключевое слово
                if any(
                    keyword in comment_text
                    for keyword in (
                        keywords_lower if not case_sensitive else keywords
                    )
                ):
                    filtered_comments.append(comment)

            logger.info(
                f"Filtered {len(comments)} comments by {len(keywords)} keywords, "
                f"result: {len(filtered_comments)} comments",
                keywords=keywords,
                case_sensitive=case_sensitive,
            )

            return filtered_comments

        except Exception as e:
            logger.error(f"Error filtering comments by keywords: {e}")
            raise

    async def get_comments_count(
        self,
        search_params: Optional[CommentSearchParams] = None,
        group_id: Optional[int] = None,
    ) -> int:
        """
        Получить количество комментариев по заданным критериям.

        Args:
            search_params: Параметры поиска
            group_id: ID группы (если указан, игнорирует search_params)

        Returns:
            Количество комментариев
        """
        try:
            if group_id is not None:
                # Простой подсчет по группе
                query = (
                    select(VKComment)
                    .join(VKPost, VKComment.post_id == VKPost.id)
                    .where(VKPost.group_id == group_id)
                )
            elif search_params:
                # Подсчет по параметрам поиска
                query = self._build_search_query(
                    search_params, include_group=False
                )
            else:
                # Общий подсчет
                query = select(VKComment)

            result = await self.db.execute(query)
            count = len(result.scalars().all())

            logger.info(f"Counted {count} comments", group_id=group_id)
            return count

        except Exception as e:
            logger.error(f"Error counting comments: {e}")
            raise

    def _build_search_query(
        self, search_params: CommentSearchParams, include_group: bool = False
    ):
        """
        Построить запрос для поиска комментариев.

        Args:
            search_params: Параметры поиска
            include_group: Включить информацию о группе

        Returns:
            SQLAlchemy запрос
        """
        # Базовый запрос с загрузкой связанных данных
        query = select(VKComment).options(
            selectinload(VKComment.keyword_matches)
        )

        if include_group:
            query = query.options(
                selectinload(VKComment.post).selectinload(VKPost.group)
            )

        # Применяем фильтры
        conditions = []

        if search_params.text:
            conditions.append(VKComment.text.ilike(f"%{search_params.text}%"))

        if search_params.group_id:
            query = query.join(VKPost, VKComment.post_id == VKPost.id)
            conditions.append(VKPost.group_id == search_params.group_id)

        if search_params.author_id:
            conditions.append(VKComment.author_id == search_params.author_id)

        if search_params.date_from:
            conditions.append(
                VKComment.published_at >= search_params.date_from
            )

        if search_params.date_to:
            conditions.append(VKComment.published_at <= search_params.date_to)

        if search_params.is_viewed is not None:
            conditions.append(VKComment.is_viewed == search_params.is_viewed)

        if conditions:
            query = query.where(and_(*conditions))

        return query

    def _apply_sorting(self, query, search_params: CommentSearchParams):
        """
        Применить сортировку к запросу.

        Args:
            query: SQLAlchemy запрос
            search_params: Параметры поиска с сортировкой

        Returns:
            Запрос с примененной сортировкой
        """
        # Определяем колонку для сортировки
        if search_params.order_by:
            order_column = getattr(
                VKComment, search_params.order_by, VKComment.published_at
            )
        else:
            order_column = VKComment.published_at  # Сортировка по умолчанию

        # Определяем направление сортировки
        if (
            search_params.order_dir
            and search_params.order_dir.lower() == "asc"
        ):
            query = query.order_by(order_column)
        else:
            query = query.order_by(desc(order_column))

        return query

    def _comment_to_response(self, comment: VKComment):
        """
        Преобразовать объект комментария в схему ответа.

        Args:
            comment: Объект комментария из базы данных

        Returns:
            Схема ответа для API
        """
        from app.schemas.vk_comment import VKCommentResponse

        return VKCommentResponse(
            id=comment.id,
            vk_id=comment.vk_id,
            text=comment.text,
            author_id=comment.author_id,
            author_name=comment.author_name,
            published_at=comment.published_at,
            post_id=comment.post_id,
            post_vk_id=comment.post_vk_id,
            author_screen_name=comment.author_screen_name,
            author_photo_url=comment.author_photo_url,
            likes_count=comment.likes_count,
            parent_comment_id=comment.parent_comment_id,
            has_attachments=comment.has_attachments,
            matched_keywords_count=comment.matched_keywords_count,
            is_processed=comment.is_processed,
            processed_at=comment.processed_at,
            is_viewed=comment.is_viewed,
            viewed_at=comment.viewed_at,
            is_archived=comment.is_archived,
            archived_at=comment.archived_at,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            group=(
                {
                    "id": comment.post.group.id,
                    "vk_id": comment.post.group.vk_id,
                    "name": comment.post.group.name,
                    "screen_name": comment.post.group.screen_name,
                    "is_active": comment.post.group.is_active,
                    "member_count": comment.post.group.member_count,
                }
                if comment.post and comment.post.group
                else None
            ),
        )

    def _comment_to_response_with_keywords(
        self, comment: VKComment
    ) -> CommentWithKeywords:
        """
        Преобразовать объект комментария в схему ответа с ключевыми словами.

        Args:
            comment: Объект комментария из базы данных

        Returns:
            Схема ответа с ключевыми словами
        """
        # Получаем найденные ключевые слова
        matched_keywords = (
            [match.keyword.word for match in comment.keyword_matches]
            if comment.keyword_matches
            else []
        )

        # Получаем детали совпадений
        keyword_matches = (
            [
                {
                    "keyword": match.keyword.word,
                    "position": match.position,
                    "context": match.matched_text,
                }
                for match in comment.keyword_matches
            ]
            if comment.keyword_matches
            else []
        )

        # Создаем базовый response
        base_response = self._comment_to_response(comment)

        # Устанавливаем matched_keywords в базовом response
        base_dict = base_response.model_dump()
        base_dict["matched_keywords"] = matched_keywords

        return CommentWithKeywords(
            **base_dict,
            keyword_matches=keyword_matches,
        )
