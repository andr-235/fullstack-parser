"""
API endpoints для управления комментариями

Этот модуль предоставляет эндпоинты для работы с комментариями VK,
включая получение, обновление и фильтрацию комментариев.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.logging import get_logger
from app.models import CommentKeywordMatch, Keyword, VKComment, VKGroup, VKPost
from app.schemas.vk_comment import CommentUpdateRequest

router = APIRouter(tags=["Comments"])
logger = get_logger(__name__)


@router.get(
    "/",
    summary="Get Comments",
    description="Получить список комментариев с пагинацией и фильтрацией",
    response_description="Список комментариев с метаданными",
)
async def get_comments(
    page: int = Query(
        default=1, ge=1, description="Номер страницы", examples=[1, 2, 3]
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Размер страницы",
        examples=[10, 20, 50],
    ),
    is_viewed: Optional[bool] = Query(
        default=None, description="Фильтр по просмотренности"
    ),
    keyword_id: Optional[int] = Query(
        default=None, description="Фильтр по ключевому слову"
    ),
    group_id: Optional[int] = Query(
        default=None, description="Фильтр по группе"
    ),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Получение списка комментариев с пагинацией и фильтрацией.

    Args:
        page: Номер страницы (начиная с 1)
        size: Размер страницы (от 1 до 100)
        is_viewed: Фильтр по статусу просмотра
        keyword_id: Фильтр по ID ключевого слова
        group_id: Фильтр по ID группы
        db: Сессия базы данных

    Returns:
        Dict[str, Any]: Словарь с комментариями и метаданными пагинации

    Raises:
        HTTPException: При ошибках получения данных
    """
    try:
        offset = (page - 1) * size

        # Базовый запрос с присоединением группы и поста
        query = (
            select(VKComment)
            .options(selectinload(VKComment.post).selectinload(VKPost.group))
            .outerjoin(VKPost, VKComment.post_id == VKPost.id)
            .outerjoin(VKGroup, VKPost.group_id == VKGroup.id)
        )
        count_query = (
            select(func.count(VKComment.id))
            .outerjoin(VKPost, VKComment.post_id == VKPost.id)
            .outerjoin(VKGroup, VKPost.group_id == VKGroup.id)
        )

        # Применяем фильтры
        filters: List[Any] = []
        if is_viewed is not None:
            filters.append(VKComment.is_viewed == is_viewed)
        if keyword_id is not None:
            # Нужно присоединить таблицу совпадений ключевых слов
            filters.append(VKComment.matched_keywords_count > 0)
        if group_id is not None:
            filters.append(VKGroup.id == group_id)

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

        # Преобразуем комментарии в словари с данными о группе
        items: List[Dict[str, Any]] = []

        # Получаем все ключевые слова для комментариев одним запросом
        comment_ids = [comment.id for comment in comments]
        keyword_matches_query = (
            select(CommentKeywordMatch.comment_id, Keyword.word)
            .join(Keyword, Keyword.id == CommentKeywordMatch.keyword_id)
            .where(CommentKeywordMatch.comment_id.in_(comment_ids))
        )

        keyword_result = await db.execute(keyword_matches_query)
        keyword_matches = keyword_result.fetchall()

        # Группируем ключевые слова по комментариям
        keywords_by_comment: Dict[int, List[str]] = {}
        for comment_id, keyword in keyword_matches:
            if comment_id not in keywords_by_comment:
                keywords_by_comment[comment_id] = []
            keywords_by_comment[comment_id].append(keyword)

        for comment in comments:
            matched_keywords = keywords_by_comment.get(comment.id, [])

            # Получаем данные группы через связь
            group_data = None
            if comment.post and comment.post.group:
                group_data = {
                    "id": comment.post.group.id,
                    "name": comment.post.group.name,
                    "vk_id": comment.post.group.vk_id,
                    "screen_name": comment.post.group.screen_name,
                }

            items.append(
                {
                    "id": comment.id,
                    "vk_id": comment.vk_id,
                    "text": comment.text,
                    "author_name": comment.author_name,
                    "author_screen_name": comment.author_screen_name,
                    "author_photo_url": comment.author_photo_url,
                    "published_at": (
                        comment.published_at.isoformat()
                        if comment.published_at
                        else None
                    ),
                    "likes_count": comment.likes_count,
                    "is_viewed": comment.is_viewed,
                    "is_archived": comment.is_archived,
                    "matched_keywords_count": comment.matched_keywords_count,
                    "matched_keywords": matched_keywords,
                    "post_vk_id": comment.post.vk_id if comment.post else None,
                    "group": group_data,
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


@router.get(
    "/{comment_id}",
    summary="Get Comment by ID",
    description="Получить комментарий по его уникальному идентификатору",
    response_description="Детальная информация о комментарии",
)
async def get_comment(
    comment_id: int = Path(
        ..., description="ID комментария", examples=[12345, 67890]
    ),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Получение комментария по ID.

    Args:
        comment_id: Уникальный идентификатор комментария
        db: Сессия базы данных

    Returns:
        Dict[str, Any]: Детальная информация о комментарии

    Raises:
        HTTPException: Если комментарий не найден
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


@router.patch("/{comment_id}")
async def update_comment(
    comment_id: int,
    update_data: CommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Обновить статус комментария (просмотрен/архивирован).
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

        # Обновляем статус просмотренности
        if update_data.is_viewed is not None:
            comment.is_viewed = update_data.is_viewed
            if update_data.is_viewed:
                comment.viewed_at = datetime.now(timezone.utc)
            else:
                comment.viewed_at = None

        # Обновляем статус архивирования
        if update_data.is_archived is not None:
            comment.is_archived = update_data.is_archived
            if update_data.is_archived:
                comment.archived_at = datetime.now(timezone.utc).replace(
                    tzinfo=None
                )
            else:
                comment.archived_at = None

        await db.commit()
        await db.refresh(comment)

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
        logger.error(f"Error updating comment {comment_id}: {e}")
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
