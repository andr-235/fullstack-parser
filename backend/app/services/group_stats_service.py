"""
GroupStatsService - сервис для получения статистики групп

Принципы SOLID:
- Single Responsibility: только статистика групп
- Open/Closed: легко добавлять новые метрики
- Liskov Substitution: можно заменить на другую реализацию
- Interface Segregation: чистый интерфейс для статистики
- Dependency Inversion: зависит от абстракций
"""

import logging
from typing import List, Dict, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.vk_group import VKGroupStats


logger = logging.getLogger(__name__)


class GroupStatsService:
    """
    Сервис для получения статистики по VK группам.

    Предоставляет высокоуровневый интерфейс для:
    - Получения статистики конкретной группы
    - Анализа ключевых слов в группе
    - Мониторинга активности группы
    """

    def __init__(self):
        """
        Инициализация сервиса статистики групп.
        """
        self.logger = logging.getLogger(__name__)

    async def get_group_stats(
        self, db: AsyncSession, group_id: int
    ) -> VKGroupStats:
        """
        Получить статистику по группе.

        Args:
            db: Сессия базы данных
            group_id: ID группы в базе данных

        Returns:
            Статистика группы

        Raises:
            ValueError: Если группа не найдена
        """
        try:
            from app.models.vk_group import VKGroup
            from app.models.comment_keyword_match import CommentKeywordMatch
            from app.models.keyword import Keyword
            from app.models.vk_comment import VKComment
            from app.models.vk_post import VKPost

            # Получаем группу
            group = await db.get(VKGroup, group_id)
            if not group:
                raise ValueError(f"Группа с ID {group_id} не найдена")

            # Подсчитываем комментарии с ключевыми словами
            comments_with_keywords_query = (
                select(func.count(VKComment.id))
                .select_from(VKComment)
                .join(VKPost, VKComment.post_id == VKPost.id)
                .where(VKPost.group_id == group_id)
                .where(VKComment.matched_keywords_count > 0)
            )
            comments_with_keywords = (
                await db.scalar(comments_with_keywords_query) or 0
            )

            # Получаем топ ключевых слов
            top_keywords = await self._get_top_keywords(db, group_id, limit=10)

            return VKGroupStats(
                group_id=group.vk_id,
                total_posts=group.total_posts_parsed or 0,
                total_comments=group.total_comments_found or 0,
                comments_with_keywords=comments_with_keywords,
                last_activity=group.last_parsed_at,
                top_keywords=top_keywords,
            )

        except Exception as e:
            logger.error(
                f"Error getting group stats for group {group_id}: {e}"
            )
            raise

    async def _get_top_keywords(
        self, db: AsyncSession, group_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получить топ ключевых слов для группы.

        Args:
            db: Сессия базы данных
            group_id: ID группы
            limit: Максимальное количество ключевых слов

        Returns:
            Список топ ключевых слов с количеством совпадений
        """
        try:
            from app.models.comment_keyword_match import CommentKeywordMatch
            from app.models.keyword import Keyword
            from app.models.vk_comment import VKComment
            from app.models.vk_post import VKPost

            # Получаем топ ключевых слов
            top_keywords_query = (
                select(
                    Keyword.text,
                    func.count(CommentKeywordMatch.id).label("match_count"),
                )
                .select_from(CommentKeywordMatch)
                .join(
                    VKComment, CommentKeywordMatch.comment_id == VKComment.id
                )
                .join(VKPost, VKComment.post_id == VKPost.id)
                .join(Keyword, CommentKeywordMatch.keyword_id == Keyword.id)
                .where(VKPost.group_id == group_id)
                .group_by(Keyword.text)
                .order_by(func.count(CommentKeywordMatch.id).desc())
                .limit(limit)
            )

            top_keywords_result = await db.execute(top_keywords_query)
            top_keywords = [
                {"keyword": row.text, "count": row.match_count}
                for row in top_keywords_result.all()
            ]

            logger.info(
                f"Retrieved top {len(top_keywords)} keywords for group {group_id}"
            )
            return top_keywords

        except Exception as e:
            logger.error(
                f"Error getting top keywords for group {group_id}: {e}"
            )
            return []

    async def get_groups_overview(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Получить общую статистику по всем группам.

        Args:
            db: Сессия базы данных

        Returns:
            Общая статистика по группам
        """
        try:
            from app.models.vk_group import VKGroup
            from app.models.vk_post import VKPost
            from app.models.vk_comment import VKComment

            # Общая статистика по группам
            total_groups = (
                await db.scalar(select(func.count()).select_from(VKGroup)) or 0
            )

            active_groups = (
                await db.scalar(
                    select(func.count())
                    .select_from(VKGroup)
                    .where(VKGroup.is_active == True)
                )
                or 0
            )

            # Статистика по постам и комментариям
            total_posts = (
                await db.scalar(
                    select(func.sum(VKGroup.total_posts_parsed)).select_from(
                        VKGroup
                    )
                )
                or 0
            )

            total_comments = (
                await db.scalar(
                    select(func.sum(VKGroup.total_comments_found)).select_from(
                        VKGroup
                    )
                )
                or 0
            )

            overview = {
                "total_groups": total_groups,
                "active_groups": active_groups,
                "inactive_groups": total_groups - active_groups,
                "total_posts": total_posts,
                "total_comments": total_comments,
                "avg_posts_per_group": (
                    total_posts / total_groups if total_groups > 0 else 0
                ),
                "avg_comments_per_group": (
                    total_comments / total_groups if total_groups > 0 else 0
                ),
            }

            logger.info(
                f"Generated groups overview: {total_groups} total groups"
            )
            return overview

        except Exception as e:
            logger.error(f"Error getting groups overview: {e}")
            return {
                "total_groups": 0,
                "active_groups": 0,
                "inactive_groups": 0,
                "total_posts": 0,
                "total_comments": 0,
                "avg_posts_per_group": 0,
                "avg_comments_per_group": 0,
            }

    async def get_group_activity_trends(
        self, db: AsyncSession, group_id: int, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Получить тренды активности группы за последние дни.

        Args:
            db: Сессия базы данных
            group_id: ID группы
            days: Количество дней для анализа

        Returns:
            Список активности по дням
        """
        try:
            from app.models.vk_post import VKPost
            from app.models.vk_comment import VKComment
            from sqlalchemy import func, desc, extract, cast, Date
            from datetime import datetime, timedelta

            # Получаем данные за последние N дней
            start_date = datetime.now() - timedelta(days=days)

            # Группируем посты по дням
            posts_query = (
                select(
                    func.date(VKPost.published_at).label("date"),
                    func.count(VKPost.id).label("posts_count"),
                )
                .select_from(VKPost)
                .where(VKPost.group_id == group_id)
                .where(VKPost.published_at >= start_date)
                .group_by(func.date(VKPost.published_at))
                .order_by(func.date(VKPost.published_at))
            )

            posts_result = await db.execute(posts_query)
            posts_data = {
                row.date: row.posts_count for row in posts_result.all()
            }

            # Группируем комментарии по дням
            comments_query = (
                select(
                    func.date(VKComment.published_at).label("date"),
                    func.count(VKComment.id).label("comments_count"),
                )
                .select_from(VKComment)
                .join(VKPost, VKComment.post_id == VKPost.id)
                .where(VKPost.group_id == group_id)
                .where(VKComment.published_at >= start_date)
                .group_by(func.date(VKComment.published_at))
                .order_by(func.date(VKComment.published_at))
            )

            comments_result = await db.execute(comments_query)
            comments_data = {
                row.date: row.comments_count for row in comments_result.all()
            }

            # Объединяем данные
            activity_trends = []
            for i in range(days):
                date = (start_date + timedelta(days=i)).date()
                activity_trends.append(
                    {
                        "date": date.isoformat(),
                        "posts": posts_data.get(date, 0),
                        "comments": comments_data.get(date, 0),
                    }
                )

            logger.info(
                f"Generated activity trends for group {group_id}: {days} days"
            )
            return activity_trends

        except Exception as e:
            logger.error(
                f"Error getting activity trends for group {group_id}: {e}"
            )
            return []
