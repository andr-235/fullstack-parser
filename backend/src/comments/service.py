"""
Сервис для работы с комментариями

Содержит бизнес-логику для операций с комментариями
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import CommentRepository
from ..exceptions import CommentNotFoundError, ValidationError
from ..infrastructure import cache_service
from ..infrastructure.logging import get_loguru_logger


class CommentService:
    """
    Сервис для работы с комментариями

    Реализует бизнес-логику для операций CRUD с комментариями
    """

    def __init__(self, repository: CommentRepository):
        self.repository = repository
        self.logger = get_loguru_logger("comments")

    def _map_comment_to_response(self, comment) -> Dict[str, Any]:
        """Маппинг комментария из БД в формат ответа API"""
        return {
            "id": comment.id,
            "vk_id": str(comment.vk_id),
            "text": comment.text,
            "author": comment.author_name or str(comment.author_id),
            "author_name": comment.author_name,
            "author_screen_name": comment.author_screen_name,
            "author_photo_url": comment.author_photo_url,
            "post_id": comment.post_id,
            "post_vk_id": (
                str(comment.post_vk_id) if comment.post_vk_id else None
            ),
            "group_id": comment.group_vk_id or 0,
            "date": (
                comment.published_at.isoformat()
                if comment.published_at
                else ""
            ),
            "published_at": (
                comment.published_at.isoformat()
                if comment.published_at
                else None
            ),
            "is_viewed": comment.is_viewed,
            "is_archived": comment.is_archived,
            "likes_count": comment.likes_count,
            "parent_comment_id": comment.parent_comment_id,
            "matched_keywords_count": comment.matched_keywords_count,
            "processed_at": (
                comment.processed_at.isoformat()
                if comment.processed_at
                else None
            ),
            "created_at": (
                comment.created_at.isoformat() if comment.created_at else None
            ),
            "updated_at": (
                comment.updated_at.isoformat() if comment.updated_at else None
            ),
        }

    async def get_comment(self, comment_id: int) -> Dict[str, Any]:
        """Получить комментарий по ID"""
        # Проверяем кеш
        cache_key = str(comment_id)
        cached_comment = await cache_service.get("comment", cache_key)

        if cached_comment:
            self.logger.debug(f"Comment {comment_id} found in cache")
            return cached_comment

        # Получаем из БД
        comment = await self.repository.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(comment_id)

        # Формируем ответ
        result = self._map_comment_to_response(comment)

        # Сохраняем в кеш
        await cache_service.set("comment", cache_key, result)
        self.logger.debug(f"Comment {comment_id} cached")

        return result

    async def get_comments_by_group(
        self,
        group_id: str,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить комментарии группы с пагинацией"""
        comments = await self.repository.get_by_group_id(
            group_id=group_id,
            limit=limit,
            offset=offset,
            search_text=search_text,
            is_viewed=is_viewed,
            is_archived=is_archived,
        )

        return [self._map_comment_to_response(comment) for comment in comments]

    async def get_all_comments(
        self,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить все комментарии с пагинацией"""
        comments = await self.repository.get_all_comments(
            limit=limit,
            offset=offset,
            search_text=search_text,
            is_viewed=is_viewed,
            is_archived=is_archived,
        )

        return [self._map_comment_to_response(comment) for comment in comments]

    async def get_comments_by_post(
        self,
        post_id: str,
        limit: int = 100,
        offset: int = 0,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить комментарии к посту"""
        comments = await self.repository.get_by_post_id(
            post_id=post_id,
            limit=limit,
            offset=offset,
            is_viewed=is_viewed,
            is_archived=is_archived,
        )

        return [self._map_comment_to_response(comment) for comment in comments]

    async def create_comment(
        self, comment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Создать новый комментарий"""
        # Валидация данных
        required_fields = [
            "vk_id",
            "post_id",
            "group_vk_id",
            "author_id",
            "author_name",
            "text",
            "published_at",
        ]
        for field in required_fields:
            if field not in comment_data or not comment_data[field]:
                raise ValidationError(
                    f"Обязательное поле '{field}' не заполнено", field=field
                )

        # Проверяем, что комментарий с таким VK ID не существует
        existing = await self.repository.get_by_vk_id(comment_data["vk_id"])
        if existing:
            raise ValidationError(
                "Комментарий с таким VK ID уже существует",
                field="vk_id",
            )

        # Создаем комментарий
        comment = await self.repository.create(comment_data)
        return await self.get_comment(int(comment.id))

    async def update_comment(
        self, comment_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить комментарий"""
        # Валидация входных данных
        allowed_fields = ["processed_at", "likes_count"]
        filtered_data = {
            k: v for k, v in update_data.items() if k in allowed_fields
        }

        if not filtered_data:
            raise ValidationError("Нет допустимых полей для обновления")

        await self.repository.update(comment_id, filtered_data)
        return await self.get_comment(comment_id)

    async def delete_comment(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        return await self.repository.delete(comment_id)

    async def mark_as_viewed(self, comment_id: int) -> Dict[str, Any]:
        """Отметить комментарий как просмотренный"""
        success = await self.repository.mark_as_viewed(comment_id)
        if not success:
            raise CommentNotFoundError(comment_id)

        return await self.get_comment(comment_id)

    async def bulk_mark_as_viewed(
        self, comment_ids: List[int]
    ) -> Dict[str, Any]:
        """Массовое отмечание комментариев как просмотренные"""
        update_data = {"processed_at": datetime.utcnow()}
        success_count = await self.repository.bulk_update(
            comment_ids, update_data
        )

        return {
            "success_count": success_count,
            "total_requested": len(comment_ids),
            "message": f"Успешно обработано {success_count} из {len(comment_ids)} комментариев",
        }

    async def get_group_stats(self, group_id: str) -> Dict[str, Any]:
        """Получить статистику комментариев группы"""
        total_count = await self.repository.count_by_group(group_id)
        global_stats = await self.repository.get_stats()

        return {
            "group_id": group_id,
            "total_comments": total_count,
            "avg_likes_per_comment": global_stats["avg_likes_per_comment"],
        }

    async def search_comments(
        self,
        query: str,
        group_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Поиск комментариев по тексту"""
        if not query or len(query.strip()) < 2:
            raise ValidationError(
                "Запрос поиска должен содержать минимум 2 символа",
                field="query",
            )

        # Специальный запрос "**" означает получить все комментарии без фильтрации по тексту
        search_text = None if query.strip() == "**" else query.strip()

        if group_id:
            return await self.get_comments_by_group(
                group_id=group_id,
                limit=limit,
                offset=offset,
                search_text=search_text,
                is_viewed=is_viewed,
                is_archived=is_archived,
            )
        else:
            # Если группа не указана, получаем все комментарии
            return await self.get_all_comments(
                limit=limit,
                offset=offset,
                search_text=search_text,
                is_viewed=is_viewed,
                is_archived=is_archived,
            )


# Экспорт
__all__ = [
    "CommentService",
]
