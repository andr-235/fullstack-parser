"""
API endpoints для управления комментариями
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional

from app.core.database import get_db
from app.models import VKComment, VKGroup, Keyword
from app.schemas.base import PaginatedResponse

router = APIRouter(tags=["Comments"])
logger = structlog.get_logger(__name__)


@router.get("/")
async def get_comments(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    is_viewed: Optional[bool] = Query(
        None, description="Фильтр по просмотренности"
    ),
    keyword_id: Optional[int] = Query(
        None, description="Фильтр по ключевому слову"
    ),
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение списка комментариев с пагинацией и фильтрами.
    """
    try:
        offset = (page - 1) * size

        # Базовый запрос
        query = select(VKComment)
        count_query = select(func.count(VKComment.id))

        # Применяем фильтры
        filters = []
        if is_viewed is not None:
            filters.append(VKComment.is_viewed == is_viewed)
        if keyword_id is not None:
            # Нужно присоединить таблицу совпадений ключевых слов
            filters.append(VKComment.matched_keywords_count > 0)
        if group_id is not None:
            filters.append(
                VKComment.post_id == group_id
            )  # VKComment связан с постом, а пост с группой

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Выполняем запросы
        result = await db.execute(
            query.offset(offset)
            .limit(size)
            .order_by(VKComment.created_at.desc())
        )
        comments = result.scalars().all()

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        pages = (total + size - 1) // size if total > 0 else 1

        # Преобразуем комментарии в словари
        items = []
        for comment in comments:
            items.append(
                {
                    "id": comment.id,
                    "vk_id": comment.vk_id,
                    "text": comment.text,
                    "author_name": comment.author_name,
                    "author_screen_name": comment.author_screen_name,
                    "published_at": (
                        comment.published_at.isoformat()
                        if comment.published_at
                        else None
                    ),
                    "likes_count": comment.likes_count,
                    "is_viewed": comment.is_viewed,
                    "is_archived": comment.is_archived,
                    "matched_keywords_count": comment.matched_keywords_count,
                    "created_at": (
                        comment.created_at.isoformat()
                        if comment.created_at
                        else None
                    ),
                    "updated_at": (
                        comment.updated_at.isoformat()
                        if comment.updated_at
                        else None
                    ),
                }
            )

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }

    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении комментариев",
        )


@router.get("/{comment_id}")
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получение комментария по ID.
    """
    try:
        result = await db.execute(
            select(VKComment).where(VKComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден",
            )

        return {
            "id": comment.id,
            "vk_id": comment.vk_id,
            "text": comment.text,
            "author_name": comment.author_name,
            "author_screen_name": comment.author_screen_name,
            "published_at": (
                comment.published_at.isoformat()
                if comment.published_at
                else None
            ),
            "likes_count": comment.likes_count,
            "is_viewed": comment.is_viewed,
            "is_archived": comment.is_archived,
            "matched_keywords_count": comment.matched_keywords_count,
            "created_at": (
                comment.created_at.isoformat() if comment.created_at else None
            ),
            "updated_at": (
                comment.updated_at.isoformat() if comment.updated_at else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении комментария",
        )


@router.post("/{comment_id}/mark-viewed")
async def mark_comment_as_viewed(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Отметить комментарий как просмотренный.
    """
    try:
        result = await db.execute(
            select(VKComment).where(VKComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден",
            )

        comment.is_viewed = True
        await db.commit()

        return {
            "status": "success",
            "message": "Комментарий отмечен как просмотренный",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking comment {comment_id} as viewed: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении комментария",
        )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление комментария.
    """
    try:
        result = await db.execute(
            select(VKComment).where(VKComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден",
            )

        await db.delete(comment)
        await db.commit()

        return {"status": "success", "message": "Комментарий удален"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении комментария",
        )
