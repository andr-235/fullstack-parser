"""
Обработчики для модуля Comments

Содержит бизнес-логику для обработки HTTP запросов
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from .interfaces import CommentServiceInterface
from .schemas import (
    CommentResponse,
    CommentListResponse,
    CommentCreate,
    CommentUpdate,
    CommentStats,
    CommentBulkAction,
    CommentBulkResponse,
)
from .exceptions import (
    CommentError,
    CommentNotFoundError,
    CommentValidationError,
    handle_comment_error,
    handle_validation_error,
    handle_not_found_error,
    handle_internal_error,
)
from ..pagination import PaginationParams, PageParam, SizeParam, SearchParam
from ..responses import APIResponse


class CommentHandlers:
    """Обработчики для комментариев"""

    def __init__(self, service: CommentServiceInterface):
        self.service = service

    async def get_comments(
        self,
        page: PageParam = 1,
        size: SizeParam = 20,
        group_id: Optional[str] = None,
        post_id: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        search: SearchParam = None,
    ) -> CommentListResponse:
        """Получить список комментариев с фильтрацией и пагинацией"""
        pagination = PaginationParams(
            page=page,
            size=size,
            search=search,
        )

        # Определяем тип запроса
        if post_id:
            # Комментарии к конкретному посту
            comments = await self.service.get_comments_by_post(
                post_id=post_id,
                limit=pagination.limit,
                offset=pagination.offset,
                is_viewed=is_viewed,
                is_archived=is_archived,
            )
            # Получаем общее количество комментариев к посту
            total = await self.service.count_by_post(
                post_id=post_id, is_viewed=is_viewed, is_archived=is_archived
            )

        elif group_id:
            # Комментарии группы
            comments = await self.service.get_comments_by_group(
                group_id=group_id,
                limit=pagination.limit,
                offset=pagination.offset,
                search_text=pagination.search,
                is_viewed=is_viewed,
                is_archived=is_archived,
            )
            # Получаем общее количество для пагинации
            total = await self.service.count_by_group(
                group_id=group_id,
                search_text=pagination.search,
                is_viewed=is_viewed,
                is_archived=is_archived,
            )

        else:
            # Общий поиск по всем комментариям
            if not pagination.search:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Необходимо указать group_id, post_id или поисковый запрос",
                )

            # Специальный запрос "**" означает получить все комментарии
            if pagination.search == "**":
                pagination.search = None

            comments = await self.service.search_comments(
                query=pagination.search or "**",  # Fallback для None
                limit=pagination.limit,
                offset=pagination.offset,
                is_viewed=is_viewed,
                is_archived=is_archived,
            )
            # Получаем общее количество для пагинации
            total = await self.service.count_all(
                search_text=pagination.search,  # None означает все комментарии
                is_viewed=is_viewed,
                is_archived=is_archived,
            )

        return CommentListResponse(
            items=[CommentResponse(**c) for c in comments],
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(
                (total + pagination.size - 1) // pagination.size
                if pagination.size > 0
                else 0
            ),
        )

    async def search_comments(
        self,
        q: str,
        group_id: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
        page: PageParam = 1,
        size: SizeParam = 20,
    ) -> CommentListResponse:
        """Поиск комментариев по тексту"""
        try:
            pagination = PaginationParams(page=page, size=size)
            comments = await self.service.search_comments(
                query=q,
                group_id=group_id,
                limit=pagination.limit,
                offset=pagination.offset,
                is_viewed=is_viewed,
                is_archived=is_archived,
                has_keywords=has_keywords,
            )

            # Получаем общее количество для пагинации
            # Специальный запрос "**" означает получить все комментарии без фильтрации по тексту
            search_text = None if q.strip() == "**" else q.strip()

            if group_id:
                total = await self.service.count_by_group(
                    group_id=group_id,
                    search_text=search_text,
                    is_viewed=is_viewed,
                    is_archived=is_archived,
                )
            else:
                total = await self.service.count_all(
                    search_text=search_text,
                    is_viewed=is_viewed,
                    is_archived=is_archived,
                )

            return CommentListResponse(
                items=[CommentResponse(**c) for c in comments],
                total=total,
                page=pagination.page,
                size=pagination.size,
                pages=(
                    (total + pagination.size - 1) // pagination.size
                    if pagination.size > 0
                    else 0
                ),
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )

    async def get_comment(self, comment_id: int) -> CommentResponse:
        """Получить комментарий по ID"""
        try:
            comment = await self.service.get_comment(comment_id)
            return CommentResponse(**comment)
        except CommentNotFoundError as e:
            raise handle_comment_error(e)
        except CommentError as e:
            raise handle_comment_error(e)
        except Exception as e:
            raise handle_internal_error(e, "get_comment")

    async def create_comment(
        self, comment_data: CommentCreate
    ) -> CommentResponse:
        """Создать новый комментарий"""
        try:
            created = await self.service.create_comment(
                comment_data.model_dump()
            )
            return CommentResponse(**created)
        except CommentValidationError as e:
            raise handle_comment_error(e)
        except CommentError as e:
            raise handle_comment_error(e)
        except Exception as e:
            raise handle_internal_error(e, "create_comment")

    async def update_comment(
        self, comment_id: int, comment_data: CommentUpdate
    ) -> CommentResponse:
        """Обновить комментарий"""
        try:
            updated = await self.service.update_comment(
                comment_id, comment_data.model_dump(exclude_unset=True)
            )
            return CommentResponse(**updated)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )

    async def delete_comment(self, comment_id: int) -> None:
        """Удалить комментарий"""
        try:
            success = await self.service.delete_comment(comment_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Комментарий не найден",
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )

    async def mark_comment_as_viewed(self, comment_id: int) -> CommentResponse:
        """Отметить комментарий как просмотренный"""
        try:
            updated = await self.service.mark_as_viewed(comment_id)
            return CommentResponse(**updated)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )

    async def bulk_mark_as_viewed(
        self, action_data: CommentBulkAction
    ) -> CommentBulkResponse:
        """Массовое отмечание комментариев как просмотренные"""
        try:
            if action_data.action != "view":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Поддерживается только действие 'view'",
                )

            result = await self.service.bulk_mark_as_viewed(
                action_data.comment_ids
            )
            return CommentBulkResponse(
                success_count=result["success_count"],
                error_count=result["total_requested"]
                - result["success_count"],
                errors=[],
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )

    async def get_group_stats(self, group_id: str) -> CommentStats:
        """Получить статистику комментариев группы"""
        try:
            stats = await self.service.get_group_stats(group_id)
            return CommentStats(**stats)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )


# Экспорт
__all__ = [
    "CommentHandlers",
]
