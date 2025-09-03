"""
Сервис для работы с комментариями

Содержит бизнес-логику для операций с комментариями
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import CommentRepository
from ..exceptions import CommentNotFoundError, ValidationError
from ..infrastructure import cache_service, logging_service


class CommentService:
    """
    Сервис для работы с комментариями

    Реализует бизнес-логику для операций CRUD с комментариями
    """

    def __init__(self, repository: CommentRepository):
        self.repository = repository
        self.logger = logging_service.get_logger("comments")

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
        result = {
            "id": comment.id,
            "vk_comment_id": comment.vk_id,
            "vk_post_id": comment.post_id,
            "vk_group_id": comment.group_id,
            "author_id": comment.author_id,
            "author_name": comment.author_name,
            "text": comment.text,
            "likes_count": comment.likes_count,
            "date": comment.published_at,
            "processed_at": comment.processed_at,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        }

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
    ) -> List[Dict[str, Any]]:
        """Получить комментарии группы с пагинацией"""
        comments = await self.repository.get_by_group_id(
            group_id=group_id,
            limit=limit,
            offset=offset,
            search_text=search_text,
        )

        return [
            {
                "id": comment.id,
                "vk_comment_id": comment.vk_id,
                "vk_post_id": comment.post_id,
                "vk_group_id": comment.group_id,
                "author_id": comment.author_id,
                "author_name": comment.author_name,
                "text": comment.text,
                "likes_count": comment.likes_count,
                "date": comment.date,
                "processed_at": comment.processed_at,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            }
            for comment in comments
        ]

    async def get_comments_by_post(
        self, post_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить комментарии к посту"""
        comments = await self.repository.get_by_post_id(
            post_id=post_id, limit=limit, offset=offset
        )

        return [
            {
                "id": comment.id,
                "vk_comment_id": comment.vk_id,
                "vk_post_id": comment.post_id,
                "vk_group_id": comment.group_id,
                "author_id": comment.author_id,
                "author_name": comment.author_name,
                "text": comment.text,
                "likes_count": comment.likes_count,
                "date": comment.date,
                "processed_at": comment.processed_at,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            }
            for comment in comments
        ]

    async def create_comment(
        self, comment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Создать новый комментарий"""
        # Валидация данных
        required_fields = [
            "vk_id",
            "post_id",
            "group_id",
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
        return await self.get_comment(comment.id)

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
    ) -> List[Dict[str, Any]]:
        """Поиск комментариев по тексту"""
        if not query or len(query.strip()) < 2:
            raise ValidationError(
                "Запрос поиска должен содержать минимум 2 символа",
                field="query",
            )

        return await self.get_comments_by_group(
            group_id=group_id or "",
            limit=limit,
            offset=offset,
            search_text=query.strip(),
        )


# Экспорт
__all__ = [
    "CommentService",
]
