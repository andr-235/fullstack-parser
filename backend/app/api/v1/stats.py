"""
API endpoints для статистики VK Comments Parser
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.stats import (
    GlobalStats,
    DashboardStats,
    DashboardTopItem,
    RecentActivityItem,
)
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, func

router = APIRouter(tags=["Stats"])


@router.get("/global", response_model=GlobalStats)
async def get_global_stats(
    db: AsyncSession = Depends(get_db),
) -> GlobalStats:
    """Получить глобальную статистику системы"""

    # Общее количество групп
    total_groups_result = await db.execute(select(func.count(VKGroup.id)))
    total_groups = total_groups_result.scalar() or 0

    # Активные группы
    active_groups_result = await db.execute(
        select(func.count(VKGroup.id)).where(VKGroup.is_active)
    )
    active_groups = active_groups_result.scalar() or 0

    # Общее количество ключевых слов
    total_keywords_result = await db.execute(select(func.count(Keyword.id)))
    total_keywords = total_keywords_result.scalar() or 0

    # Активные ключевые слова
    active_keywords_result = await db.execute(
        select(func.count(Keyword.id)).where(Keyword.is_active)
    )
    active_keywords = active_keywords_result.scalar() or 0

    # Общее количество комментариев
    total_comments_result = await db.execute(select(func.count(VKComment.id)))
    total_comments = total_comments_result.scalar() or 0

    # Комментарии с ключевыми словами
    comments_with_keywords_result = await db.execute(
        select(func.count(func.distinct(CommentKeywordMatch.comment_id)))
    )
    comments_with_keywords = comments_with_keywords_result.scalar() or 0

    return GlobalStats(
        total_groups=total_groups,
        active_groups=active_groups,
        total_keywords=total_keywords,
        active_keywords=active_keywords,
        total_comments=total_comments,
        comments_with_keywords=comments_with_keywords,
        last_parse_time=None,
    )


# @router.get("/", response_model=Stats)
# async def get_stats(db: AsyncSession = Depends(get_db)):
#     """
#     Эндпоинт для получения статистики.
#     """
#     # Здесь может быть логика для сбора данных для статистики
#     return Stats(
#         groups=group_stats,
#         keywords=keyword_stats,
#         comments=comment_stats,
#         parser=parser_stats,
#     )


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    """Получить статистику для дашборда"""

    try:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)

        # Комментарии за сегодня
        today_comments_result = await db.execute(
            select(func.count(VKComment.id)).where(
                VKComment.created_at >= today_start
            )
        )
        today_comments = today_comments_result.scalar() or 0

        # Совпадения за сегодня
        today_matches_result = await db.execute(
            select(
                func.count(func.distinct(CommentKeywordMatch.comment_id))
            ).where(CommentKeywordMatch.created_at >= today_start)
        )
        today_matches = today_matches_result.scalar() or 0

        # Комментарии за неделю
        week_comments_result = await db.execute(
            select(func.count(VKComment.id)).where(
                VKComment.created_at >= week_start
            )
        )
        week_comments = week_comments_result.scalar() or 0

        # Совпадения за неделю
        week_matches_result = await db.execute(
            select(
                func.count(func.distinct(CommentKeywordMatch.comment_id))
            ).where(CommentKeywordMatch.created_at >= week_start)
        )
        week_matches = week_matches_result.scalar() or 0

        # Топ групп по количеству комментариев
        try:
            top_groups_query = (
                select(
                    VKGroup.name,
                    func.count(VKComment.id).label("comment_count"),
                )
                .join(VKPost, VKGroup.id == VKPost.group_id)
                .join(VKComment, VKPost.id == VKComment.post_id)
                .group_by(VKGroup.id, VKGroup.name)
                .order_by(desc("comment_count"))
                .limit(10)
            )
            top_groups_result = await db.execute(top_groups_query)
            top_groups = [
                DashboardTopItem(name=row.name, count=row.comment_count)
                for row in top_groups_result
            ]
        except Exception as e:
            print(f"Error fetching top groups: {e}")
            top_groups = []

        # Топ ключевых слов по количеству совпадений
        try:
            top_keywords_query = (
                select(
                    Keyword.word,
                    func.count(CommentKeywordMatch.id).label("match_count"),
                )
                .join(
                    CommentKeywordMatch,
                    Keyword.id == CommentKeywordMatch.keyword_id,
                )
                .group_by(Keyword.id, Keyword.word)
                .order_by(desc("match_count"))
                .limit(10)
            )
            top_keywords_result = await db.execute(top_keywords_query)
            top_keywords = [
                DashboardTopItem(name=row.word, count=row.match_count)
                for row in top_keywords_result
            ]
        except Exception as e:
            print(f"Error fetching top keywords: {e}")
            top_keywords = []

        # Недавняя активность (последние 10 записей)
        try:
            recent_activity_query = (
                select(VKComment)
                .order_by(desc(VKComment.created_at))
                .limit(10)
            )
            recent_comments = (
                (await db.execute(recent_activity_query)).scalars().all()
            )

            recent_activity = []
            for i, comment in enumerate(recent_comments):
                # Определяем тип активности на основе наличия совпадений
                try:
                    match_count = await db.execute(
                        select(func.count(CommentKeywordMatch.id)).where(
                            CommentKeywordMatch.comment_id == comment.id
                        )
                    )
                    has_matches = (match_count.scalar() or 0) > 0
                except Exception:
                    has_matches = False

                activity_type = "match" if has_matches else "comment"
                message = (
                    f"Найден комментарий в группе {comment.group_id}"
                    if has_matches
                    else f"Новый комментарий в группе {comment.group_id}"
                )

                recent_activity.append(
                    RecentActivityItem(
                        id=i + 1,
                        type=activity_type,
                        message=message,
                        timestamp=comment.created_at,
                    )
                )
        except Exception as e:
            print(f"Error fetching recent activity: {e}")
            recent_activity = []

        return DashboardStats(
            today_comments=today_comments,
            today_matches=today_matches,
            week_comments=week_comments,
            week_matches=week_matches,
            top_groups=top_groups,
            top_keywords=top_keywords,
            recent_activity=recent_activity,
        )

    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
        # Возвращаем пустые данные в случае ошибки
        return DashboardStats(
            today_comments=0,
            today_matches=0,
            week_comments=0,
            week_matches=0,
            top_groups=[],
            top_keywords=[],
            recent_activity=[],
        )


@router.get("/health")
async def get_api_health(db: AsyncSession = Depends(get_db)) -> dict:
    """Проверка здоровья API и подключений"""

    try:
        await db.execute(select(1))
        return {"success": True, "message": "API работает корректно"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка: {str(e)}"}
