"""
CommentService - сервис для работы с комментариями VK

Принципы SOLID:
- Single Responsibility: только работа с комментариями
- Open/Closed: легко расширять новыми методами
- Liskov Substitution: можно заменить на другую реализацию
- Interface Segregation: минимальный интерфейс для работы с комментариями
- Dependency Inversion: зависит от абстракций (AsyncSession)
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentUpdateRequest,
    CommentWithKeywords,
    VKCommentResponse
)

logger = logging.getLogger(__name__)


class CommentService:
    """
    Сервис для работы с комментариями VK.

    Предоставляет высокоуровневый интерфейс для:
    - Получения комментариев с фильтрацией и пагинацией
    - Поиска комментариев по различным критериям
    - Обновления статуса комментариев
    - Получения статистики по комментариям
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db

    async def get_comments_by_group(
        self,
        group_id: int,
        limit: int = 50,
        offset: int = 0,
        include_group: bool = False
    ) -> List[VKCommentResponse]:
        """
        Получить комментарии группы с пагинацией.

        Args:
            group_id: ID группы VK
            limit: Максимальное количество комментариев
            offset: Смещение для пагинации
            include_group: Включить информацию о группе

        Returns:
            Список комментариев группы
        """
        try:
            # Базовый запрос с загрузкой связанных данных
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

            return [self._comment_to_response(comment) for comment in comments]

        except Exception as e:
            logger.error(f"Error getting comments for group {group_id}: {e}")
            raise

    async def search_comments(
        self,
        search_params: CommentSearchParams,
        limit: int = 50,
        offset: int = 0
    ) -> List[CommentWithKeywords]:
        """
        Поиск комментариев по различным критериям.

        Args:
            search_params: Параметры поиска
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            Список найденных комментариев с ключевыми словами
        """
        try:
            query = select(VKComment).options(
                selectinload(VKComment.post).selectinload(VKPost.group),
                selectinload(VKComment.keyword_matches)
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
                conditions.append(VKComment.published_at >= search_params.date_from)

            if search_params.date_to:
                conditions.append(VKComment.published_at <= search_params.date_to)

            if search_params.is_viewed is not None:
                conditions.append(VKComment.is_viewed == search_params.is_viewed)

            if conditions:
                query = query.where(and_(*conditions))

            # Порядок и пагинация
            query = (
                query
                .order_by(desc(VKComment.published_at))
                .limit(limit)
                .offset(offset)
            )

            result = await self.db.execute(query)
            comments = result.scalars().all()

            return [self._comment_to_response_with_keywords(comment) for comment in comments]

        except Exception as e:
            logger.error(f"Error searching comments: {e}")
            raise

    async def get_comment_by_id(self, comment_id: int) -> Optional[VKCommentResponse]:
        """
        Получить комментарий по ID.

        Args:
            comment_id: ID комментария в базе данных

        Returns:
            Комментарий или None если не найден
        """
        try:
            query = (
                select(VKComment)
                .options(
                    selectinload(VKComment.post).selectinload(VKPost.group),
                    selectinload(VKComment.keyword_matches)
                )
                .where(VKComment.id == comment_id)
            )

            result = await self.db.execute(query)
            comment = result.scalar_one_or_none()

            return self._comment_to_response(comment) if comment else None

        except Exception as e:
            logger.error(f"Error getting comment {comment_id}: {e}")
            raise

    async def update_comment(
        self,
        comment_id: int,
        update_data: CommentUpdateRequest
    ) -> Optional[VKCommentResponse]:
        """
        Обновить статус комментария.

        Args:
            comment_id: ID комментария
            update_data: Данные для обновления

        Returns:
            Обновленный комментарий или None если не найден
        """
        try:
            # Получаем комментарий
            comment = await self.get_comment_by_id(comment_id)
            if not comment:
                return None

            # Получаем объект из базы для обновления
            query = select(VKComment).where(VKComment.id == comment_id)
            result = await self.db.execute(query)
            db_comment = result.scalar_one()

            # Обновляем поля
            update_dict = update_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                if hasattr(db_comment, field):
                    setattr(db_comment, field, value)

                    # Устанавливаем timestamp для viewed_at или archived_at
                    if field == 'is_viewed' and value and not db_comment.viewed_at:
                        db_comment.viewed_at = datetime.now()
                    elif field == 'is_archived' and value and not db_comment.archived_at:
                        db_comment.archived_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(db_comment)

            return self._comment_to_response(db_comment)

        except Exception as e:
            logger.error(f"Error updating comment {comment_id}: {e}")
            await self.db.rollback()
            raise

    async def get_comment_stats(self, group_id: Optional[int] = None) -> dict:
        """
        Получить статистику по комментариям.

        Args:
            group_id: ID группы (если None - статистика по всем группам)

        Returns:
            Статистика по комментариям
        """
        try:
            # Базовый запрос
            query = select(VKComment)

            if group_id:
                query = (
                    query
                    .join(VKPost, VKComment.post_id == VKPost.id)
                    .where(VKPost.group_id == group_id)
                )

            result = await self.db.execute(query)
            comments = result.scalars().all()

            # Вычисляем статистику
            total_comments = len(comments)
            viewed_comments = len([c for c in comments if c.is_viewed])
            archived_comments = len([c for c in comments if c.is_archived])
            processed_comments = len([c for c in comments if c.is_processed])

            # Статистика по ключевым словам
            total_keywords = sum(c.matched_keywords_count for c in comments)
            avg_keywords_per_comment = total_keywords / total_comments if total_comments > 0 else 0

            return {
                "total_comments": total_comments,
                "viewed_comments": viewed_comments,
                "archived_comments": archived_comments,
                "processed_comments": processed_comments,
                "total_matched_keywords": total_keywords,
                "avg_keywords_per_comment": round(avg_keywords_per_comment, 2),
                "view_rate": round(viewed_comments / total_comments * 100, 2) if total_comments > 0 else 0,
                "archive_rate": round(archived_comments / total_comments * 100, 2) if total_comments > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error getting comment stats: {e}")
            raise

    def _comment_to_response(self, comment: VKComment) -> VKCommentResponse:
        """
        Преобразовать объект комментария в схему ответа.

        Args:
            comment: Объект комментария из базы данных

        Returns:
            Схема ответа для API
        """
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
                    "member_count": comment.post.group.member_count
                }
                if comment.post and comment.post.group else None
            )
        )

    def _comment_to_response_with_keywords(self, comment: VKComment) -> CommentWithKeywords:
        """
        Преобразовать объект комментария в схему ответа с ключевыми словами.

        Args:
            comment: Объект комментария из базы данных

        Returns:
            Схема ответа с ключевыми словами
        """
        # Получаем найденные ключевые слова
        matched_keywords = [
            match.keyword.word for match in comment.keyword_matches
        ] if comment.keyword_matches else []

        # Получаем детали совпадений
        keyword_matches = [
            {
                "keyword": match.keyword.word,
                "position": match.position,
                "context": match.matched_text
            }
            for match in comment.keyword_matches
        ] if comment.keyword_matches else []

        return CommentWithKeywords(
            **self._comment_to_response(comment).model_dump(),
            matched_keywords=matched_keywords,
            keyword_matches=keyword_matches
        )
