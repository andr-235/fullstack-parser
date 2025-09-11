"""
Сервис для работы с комментариями

Содержит бизнес-логику для операций с комментариями
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from .interfaces import (
    CommentServiceInterface,
    CommentRepositoryInterface,
    CacheServiceInterface,
    LoggerInterface,
)
from .mappers import CommentMapper
from ..exceptions import CommentNotFoundError, ValidationError


class CommentService(CommentServiceInterface):
    """
    Сервис для работы с комментариями

    Реализует бизнес-логику для операций CRUD с комментариями
    """

    def __init__(
        self,
        repository: CommentRepositoryInterface,
        cache_service: Optional[CacheServiceInterface] = None,
        logger: Optional[LoggerInterface] = None,
    ):
        self.repository = repository
        self.cache_service = cache_service
        self.logger = logger

    def _get_cache_key(self, prefix: str, *args) -> str:
        """Генерация ключа кеша"""
        return f"{prefix}:{':'.join(map(str, args))}"

    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Получить данные из кеша"""
        if not self.cache_service:
            return None

        try:
            return await self.cache_service.get("comment", cache_key)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Ошибка получения из кеша: {e}")
            return None

    async def _set_to_cache(
        self, cache_key: str, value: Any, ttl: int = 300
    ) -> None:
        """Сохранить данные в кеш"""
        if not self.cache_service:
            return

        try:
            await self.cache_service.set("comment", cache_key, value, ttl)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Ошибка сохранения в кеш: {e}")

    async def _invalidate_cache(self, cache_key: str) -> None:
        """Инвалидировать кеш"""
        if not self.cache_service:
            return

        try:
            await self.cache_service.delete("comment", cache_key)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Ошибка инвалидации кеша: {e}")

    async def get_comment(self, comment_id: int) -> Dict[str, Any]:
        """Получить комментарий по ID"""
        # Проверяем кеш
        cache_key = self._get_cache_key("comment", comment_id)
        cached_comment = await self._get_from_cache(cache_key)

        if cached_comment:
            if self.logger:
                self.logger.debug(f"Comment {comment_id} found in cache")
            return cached_comment

        # Получаем из БД
        comment = await self.repository.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(comment_id)

        # Формируем ответ
        result = CommentMapper.to_response_dict(comment)

        # Сохраняем в кеш
        await self._set_to_cache(cache_key, result)
        if self.logger:
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
        has_keywords: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить комментарии группы с пагинацией"""
        comments = await self.repository.get_by_group_id(
            group_id=group_id,
            limit=limit,
            offset=offset,
            search_text=search_text,
            is_viewed=is_viewed,
            is_archived=is_archived,
            has_keywords=has_keywords,
        )

        return CommentMapper.to_response_dicts(comments)

    async def get_all_comments(
        self,
        limit: int = 50,
        offset: int = 0,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получить все комментарии с пагинацией"""
        comments = await self.repository.get_all_comments(
            limit=limit,
            offset=offset,
            search_text=search_text,
            is_viewed=is_viewed,
            is_archived=is_archived,
            has_keywords=has_keywords,
        )

        return CommentMapper.to_response_dicts(comments)

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

        return CommentMapper.to_response_dicts(comments)

    async def create_comment(
        self, comment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Создать новый комментарий"""
        # Валидация и нормализация данных
        try:
            normalized_data = CommentMapper.to_create_data(comment_data)
        except ValueError as e:
            raise ValidationError(str(e), field="validation")

        # Проверяем, что комментарий с таким VK ID не существует
        existing = await self.repository.get_by_vk_id(normalized_data["vk_id"])
        if existing:
            raise ValidationError(
                "Комментарий с таким VK ID уже существует",
                field="vk_id",
            )

        # Создаем комментарий
        comment = await self.repository.create(normalized_data)

        # Инвалидируем кеш
        cache_key = self._get_cache_key("comment", comment.id)
        await self._invalidate_cache(cache_key)

        return await self.get_comment(int(comment.id))

    async def update_comment(
        self, comment_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить комментарий"""
        # Валидация и нормализация данных
        try:
            normalized_data = CommentMapper.to_update_data(update_data)
        except ValueError as e:
            raise ValidationError(str(e), field="validation")

        if not normalized_data:
            raise ValidationError("Нет допустимых полей для обновления")

        await self.repository.update(comment_id, normalized_data)

        # Инвалидируем кеш
        cache_key = self._get_cache_key("comment", comment_id)
        await self._invalidate_cache(cache_key)

        return await self.get_comment(comment_id)

    async def delete_comment(self, comment_id: int) -> bool:
        """Удалить комментарий"""
        success = await self.repository.delete(comment_id)

        if success:
            # Инвалидируем кеш
            cache_key = self._get_cache_key("comment", comment_id)
            await self._invalidate_cache(cache_key)

        return success

    async def mark_as_viewed(self, comment_id: int) -> Dict[str, Any]:
        """Отметить комментарий как просмотренный"""
        success = await self.repository.mark_as_viewed(comment_id)
        if not success:
            raise CommentNotFoundError(comment_id)

        # Инвалидируем кеш
        cache_key = self._get_cache_key("comment", comment_id)
        await self._invalidate_cache(cache_key)

        return await self.get_comment(comment_id)

    async def bulk_mark_as_viewed(
        self, comment_ids: List[int]
    ) -> Dict[str, Any]:
        """Массовое отмечание комментариев как просмотренные"""
        update_data = {"processed_at": datetime.utcnow()}
        success_count = await self.repository.bulk_update(
            comment_ids, update_data
        )

        # Инвалидируем кеш для всех обновленных комментариев
        for comment_id in comment_ids:
            cache_key = self._get_cache_key("comment", comment_id)
            await self._invalidate_cache(cache_key)

        return {
            "success_count": success_count,
            "total_requested": len(comment_ids),
            "message": f"Успешно обработано {success_count} из {len(comment_ids)} комментариев",
        }

    async def get_group_stats(self, group_id: str) -> Dict[str, Any]:
        """Получить статистику комментариев группы"""
        total_count = await self.repository.count_by_group(group_id)
        global_stats = await self.repository.get_stats()

        return CommentMapper.to_stats_dict(global_stats, group_id)

    async def search_comments(
        self,
        query: str,
        group_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        has_keywords: Optional[bool] = None,
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
                has_keywords=has_keywords,
            )
        else:
            # Если группа не указана, получаем все комментарии
            return await self.get_all_comments(
                limit=limit,
                offset=offset,
                search_text=search_text,
                is_viewed=is_viewed,
                is_archived=is_archived,
                has_keywords=has_keywords,
            )

    async def count_by_group(
        self,
        group_id: str,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев в группе"""
        return await self.repository.count_by_group(
            group_id=group_id,
            search_text=search_text,
            is_viewed=is_viewed,
            is_archived=is_archived,
        )

    async def count_by_post(
        self,
        post_id: str,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество комментариев к посту"""
        return await self.repository.count_by_post(
            post_id=post_id,
            is_viewed=is_viewed,
            is_archived=is_archived,
        )

    async def count_all(
        self,
        search_text: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Подсчитать общее количество комментариев"""
        return await self.repository.count_all(
            search_text=search_text,
            is_viewed=is_viewed,
            is_archived=is_archived,
        )


# Экспорт
__all__ = [
    "CommentService",
]
