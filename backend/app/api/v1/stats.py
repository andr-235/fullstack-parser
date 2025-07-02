"""
API endpoints для статистики VK Comments Parser
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/global")
async def get_global_stats(db: AsyncSession = Depends(get_async_session)) -> dict:
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

    return {
        "total_groups": total_groups,
        "active_groups": active_groups,
        "total_keywords": total_keywords,
        "active_keywords": active_keywords,
        "total_comments": total_comments,
        "comments_with_keywords": comments_with_keywords,
        "last_parse_time": None,
    }


@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_async_session)) -> dict:
    """Получить статистику для дашборда"""

    return {
        "today_comments": 42,
        "today_matches": 8,
        "week_comments": 287,
        "week_matches": 56,
        "top_groups": [
            {"name": "Тестовая группа 1", "count": 15},
            {"name": "Тестовая группа 2", "count": 12},
            {"name": "Тестовая группа 3", "count": 8},
        ],
        "top_keywords": [
            {"word": "важно", "count": 25},
            {"word": "срочно", "count": 18},
            {"word": "проблема", "count": 13},
        ],
        "recent_activity": [
            {
                "id": 1,
                "type": "parse",
                "message": "Запущен парсинг группы",
                "timestamp": "2025-07-02T12:00:00Z",
            },
            {
                "id": 2,
                "type": "comment",
                "message": "Найден новый комментарий",
                "timestamp": "2025-07-02T11:45:00Z",
            },
        ],
    }


@router.get("/health")
async def get_api_health(db: AsyncSession = Depends(get_async_session)) -> dict:
    """Проверка здоровья API и подключений"""

    try:
        await db.execute(select(1))
        return {"success": True, "message": "API работает корректно"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка: {str(e)}"}
