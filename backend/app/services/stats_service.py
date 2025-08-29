"""
StatsService - сервис для сбора статистики и аналитики

Принципы SOLID:
- Single Responsibility: только статистика и аналитика
- Open/Closed: легко добавлять новые метрики
- Liskov Substitution: можно заменить на другую реализацию статистики
- Interface Segregation: чистый интерфейс для статистики
- Dependency Inversion: зависит от абстракций (AsyncSession)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost

logger = logging.getLogger(__name__)


class StatsService:
    """
    Сервис для сбора статистики и аналитики системы.

    Предоставляет высокоуровневый интерфейс для:
    - Глобальной статистики системы
    - Статистики по группам
    - Статистики по ключевым словам
    - Аналитических отчетов
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса статистики.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db

    async def get_global_stats(self) -> Dict:
        """
        Получить глобальную статистику системы.

        Returns:
            Словарь с глобальной статистикой
        """
        try:
            # Статистика по группам
            groups_query = select(VKGroup)
            groups_result = await self.db.execute(groups_query)
            all_groups = groups_result.scalars().all()

            active_groups = [g for g in all_groups if g.is_active]
            total_groups = len(all_groups)
            active_groups_count = len(active_groups)

            # Статистика по комментариям
            comments_query = select(VKComment)
            comments_result = await self.db.execute(comments_query)
            all_comments = comments_result.scalars().all()

            total_comments = len(all_comments)
            viewed_comments = len([c for c in all_comments if c.is_viewed])
            archived_comments = len([c for c in all_comments if c.is_archived])
            processed_comments = len(
                [c for c in all_comments if c.is_processed]
            )

            # Статистика по ключевым словам
            keywords_query = select(Keyword)
            keywords_result = await self.db.execute(keywords_query)
            all_keywords = keywords_result.scalars().all()

            active_keywords = [k for k in all_keywords if k.is_active]
            total_keywords = len(all_keywords)
            active_keywords_count = len(active_keywords)

            # Статистика по постам
            posts_query = select(VKPost)
            posts_result = await self.db.execute(posts_query)
            total_posts = len(posts_result.scalars().all())

            # Расчет производных метрик
            view_rate = (
                round(viewed_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            )
            archive_rate = (
                round(archived_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            )
            processing_rate = (
                round(processed_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            )

            # Среднее количество комментариев на группу
            avg_comments_per_group = (
                round(total_comments / total_groups, 2)
                if total_groups > 0
                else 0
            )

            # Среднее количество комментариев на пост
            avg_comments_per_post = (
                round(total_comments / total_posts, 2)
                if total_posts > 0
                else 0
            )

            stats = {
                "overview": {
                    "total_groups": total_groups,
                    "active_groups": active_groups_count,
                    "total_comments": total_comments,
                    "total_posts": total_posts,
                    "total_keywords": total_keywords,
                    "active_keywords": active_keywords_count,
                },
                "comments": {
                    "total": total_comments,
                    "viewed": viewed_comments,
                    "archived": archived_comments,
                    "processed": processed_comments,
                    "view_rate": view_rate,
                    "archive_rate": archive_rate,
                    "processing_rate": processing_rate,
                },
                "engagement": {
                    "avg_comments_per_group": avg_comments_per_group,
                    "avg_comments_per_post": avg_comments_per_post,
                    "groups_with_comments": len(
                        set(c.post.group_id for c in all_comments if c.post)
                    ),
                },
                "keywords": {
                    "total": total_keywords,
                    "active": active_keywords_count,
                    "inactive": total_keywords - active_keywords_count,
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                "Global stats generated",
                total_comments=total_comments,
                total_groups=total_groups,
                active_groups=active_groups_count,
            )

            return stats

        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            raise

    async def get_group_stats(self, group_id: int) -> Dict:
        """
        Получить статистику по конкретной группе.

        Args:
            group_id: ID группы VK

        Returns:
            Статистика группы
        """
        try:
            # Информация о группе
            group_query = select(VKGroup).where(VKGroup.vk_id == group_id)
            group_result = await self.db.execute(group_query)
            group = group_result.scalar_one_or_none()

            if not group:
                raise ValueError(f"Group with ID {group_id} not found")

            # Статистика постов группы
            posts_query = select(VKPost).where(VKPost.group_id == group.id)
            posts_result = await self.db.execute(posts_query)
            posts = posts_result.scalars().all()
            total_posts = len(posts)

            # Статистика комментариев группы
            comments_query = (
                select(VKComment)
                .join(VKPost, VKComment.post_id == VKPost.id)
                .where(VKPost.group_id == group.id)
            )
            comments_result = await self.db.execute(comments_query)
            comments = comments_result.scalars().all()

            total_comments = len(comments)
            viewed_comments = len([c for c in comments if c.is_viewed])
            archived_comments = len([c for c in comments if c.is_archived])
            processed_comments = len([c for c in comments if c.is_processed])

            # Статистика по ключевым словам в комментариях группы
            total_keyword_matches = sum(
                c.matched_keywords_count for c in comments
            )
            avg_keywords_per_comment = (
                round(total_keyword_matches / total_comments, 2)
                if total_comments > 0
                else 0
            )

            # Расчет метрик
            view_rate = (
                round(viewed_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            )
            archive_rate = (
                round(archived_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            )
            avg_comments_per_post = (
                round(total_comments / total_posts, 2)
                if total_posts > 0
                else 0
            )

            stats = {
                "group_info": {
                    "id": group.id,
                    "vk_id": group.vk_id,
                    "name": group.name,
                    "screen_name": group.screen_name,
                    "is_active": group.is_active,
                    "member_count": getattr(group, "member_count", 0),
                },
                "posts": {"total": total_posts},
                "comments": {
                    "total": total_comments,
                    "viewed": viewed_comments,
                    "archived": archived_comments,
                    "processed": processed_comments,
                    "view_rate": view_rate,
                    "archive_rate": archive_rate,
                    "avg_keywords_per_comment": avg_keywords_per_comment,
                },
                "engagement": {
                    "avg_comments_per_post": avg_comments_per_post,
                    "total_keyword_matches": total_keyword_matches,
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"Group stats generated for group {group_id}",
                group_id=group_id,
                total_comments=total_comments,
                total_posts=total_posts,
            )

            return stats

        except Exception as e:
            logger.error(f"Error getting group stats for {group_id}: {e}")
            raise

    async def get_keyword_stats(self) -> List[Dict]:
        """
        Получить статистику по ключевым словам.

        Returns:
            Список статистик по ключевым словам
        """
        try:
            keywords_query = select(Keyword)
            keywords_result = await self.db.execute(keywords_query)
            keywords = keywords_result.scalars().all()

            keyword_stats = []

            for keyword in keywords:
                # Считаем количество комментариев, содержащих это ключевое слово
                # В реальном приложении здесь была бы более сложная логика
                # с использованием полнотекстового поиска или индексов

                # Для простоты используем простое совпадение
                comments_with_keyword = []
                for comment in await self._get_all_comments():
                    if keyword.word.lower() in comment.text.lower():
                        comments_with_keyword.append(comment)

                stats = {
                    "keyword_id": keyword.id,
                    "word": keyword.word,
                    "category": keyword.category,
                    "is_active": keyword.is_active,
                    "comments_count": len(comments_with_keyword),
                    "description": keyword.description,
                }

                keyword_stats.append(stats)

            # Сортируем по количеству комментариев (убывание)
            keyword_stats.sort(key=lambda x: x["comments_count"], reverse=True)

            logger.info(
                f"Keyword stats generated for {len(keywords)} keywords",
                keywords_count=len(keywords),
            )

            return keyword_stats

        except Exception as e:
            logger.error(f"Error getting keyword stats: {e}")
            raise

    async def get_recent_activity(self, hours: int = 24) -> Dict:
        """
        Получить статистику недавней активности.

        Args:
            hours: Количество часов для анализа

        Returns:
            Статистика недавней активности
        """
        try:
            since_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            # Новые комментарии за период
            recent_comments_query = select(VKComment).where(
                VKComment.created_at >= since_time
            )
            recent_comments_result = await self.db.execute(
                recent_comments_query
            )
            recent_comments = recent_comments_result.scalars().all()

            # Новые посты за период
            recent_posts_query = select(VKPost).where(
                VKPost.created_at >= since_time
            )
            recent_posts_result = await self.db.execute(recent_posts_query)
            recent_posts = recent_posts_result.scalars().all()

            # Комментарии, просмотренные за период
            viewed_comments_query = select(VKComment).where(
                and_(
                    VKComment.viewed_at >= since_time,
                    VKComment.viewed_at.isnot(None),
                )
            )
            viewed_comments_result = await self.db.execute(
                viewed_comments_query
            )
            viewed_comments = viewed_comments_result.scalars().all()

            stats = {
                "period_hours": hours,
                "recent_comments": len(recent_comments),
                "recent_posts": len(recent_posts),
                "viewed_comments": len(viewed_comments),
                "comments_per_hour": round(len(recent_comments) / hours, 2),
                "posts_per_hour": round(len(recent_posts) / hours, 2),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"Recent activity stats generated for {hours} hours",
                hours=hours,
                recent_comments=len(recent_comments),
                recent_posts=len(recent_posts),
            )

            return stats

        except Exception as e:
            logger.error(f"Error getting recent activity stats: {e}")
            raise

    async def _get_all_comments(self) -> List[VKComment]:
        """
        Получить все комментарии (вспомогательный метод).

        Returns:
            Список всех комментариев
        """
        query = select(VKComment)
        result = await self.db.execute(query)
        return result.scalars().all()
