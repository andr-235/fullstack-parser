"""
Application Service для комментариев (DDD)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..domain.comment import Comment, CommentContent, CommentStatus
from ..domain.keyword import Keyword
from .base import ApplicationService


class CommentApplicationService(ApplicationService):
    """Application Service для работы с комментариями"""

    def __init__(self, comment_repository, keyword_repository):
        self.comment_repository = comment_repository
        self.keyword_repository = keyword_repository

    async def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Получить комментарий по ID"""
        return await self.comment_repository.find_by_id(comment_id)

    async def get_comments_by_group(
        self,
        group_id: int,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False,
    ) -> List[Comment]:
        """Получить комментарии группы"""
        # Здесь будет логика фильтрации и пагинации
        comments = await self.comment_repository.find_by_group_id(group_id)

        if not include_archived:
            comments = [c for c in comments if not c.is_archived]

        return comments[offset : offset + limit]

    async def search_comments(
        self,
        query: str,
        group_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Comment]:
        """Поиск комментариев по тексту"""
        # Здесь будет логика поиска
        all_comments = await self.comment_repository.find_all()

        # Фильтрация по группе
        if group_id:
            all_comments = [c for c in all_comments if c.group_id == group_id]

        # Фильтрация по тексту
        filtered_comments = []
        for comment in all_comments:
            if query.lower() in comment.content.text.lower():
                filtered_comments.append(comment)

        return filtered_comments[offset : offset + limit]

    async def mark_comment_as_viewed(self, comment_id: int) -> bool:
        """Отметить комментарий как просмотренный"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.mark_as_viewed()
        await self.comment_repository.save(comment)
        return True

    async def mark_comment_as_processed(self, comment_id: int) -> bool:
        """Отметить комментарий как обработанный"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.mark_as_processed()
        await self.comment_repository.save(comment)
        return True

    async def archive_comment(self, comment_id: int) -> bool:
        """Архивировать комментарий"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.archive()
        await self.comment_repository.save(comment)
        return True

    async def unarchive_comment(self, comment_id: int) -> bool:
        """Разархивировать комментарий"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False

        comment.unarchive()
        await self.comment_repository.save(comment)
        return True

    async def analyze_comment_with_keywords(
        self, comment_id: int
    ) -> Dict[str, Any]:
        """Анализировать комментарий на совпадения с ключевыми словами"""
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return {"error": "Comment not found"}

        keywords = await self.keyword_repository.find_active_keywords()
        matches = []

        for keyword in keywords:
            if keyword.word.lower() in comment.content.text.lower():
                comment.add_keyword_match(keyword.id, keyword.word)
                matches.append(
                    {
                        "keyword_id": keyword.id,
                        "keyword_word": keyword.word,
                        "keyword_category": keyword.category_name,
                    }
                )

        if matches:
            await self.comment_repository.save(comment)

        return {
            "comment_id": comment.id,
            "matches_found": len(matches),
            "matches": matches,
        }

    # Дополнительные методы из CommentService для полной миграции

    async def search_comments(
        self,
        search_params: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Поиск комментариев по различным критериям (мигрировано из CommentService)

        Args:
            search_params: Параметры поиска
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            Результаты поиска с пагинацией
        """
        # Используем существующую функциональность поиска
        query = search_params.get("text", "")
        group_id = search_params.get("group_id")

        if group_id:
            comments = await self.get_comments_by_group(
                group_id=group_id, limit=limit, offset=offset
            )
            # Фильтруем по тексту если указан
            if query:
                comments = [
                    c
                    for c in comments
                    if query.lower() in c.content.text.lower()
                ]
        else:
            # Поиск по всем комментариям
            all_comments = await self.comment_repository.find_all()
            comments = [
                c
                for c in all_comments
                if query.lower() in c.content.text.lower()
            ][offset : offset + limit]

        return {
            "comments": comments,
            "total": len(comments),
            "limit": limit,
            "offset": offset,
        }

    async def update_comment_status(
        self, comment_id: int, status_updates: Dict[str, Any]
    ) -> Optional[Comment]:
        """
        Обновить статус комментария (мигрировано из CommentService)

        Args:
            comment_id: ID комментария
            status_updates: Обновления статуса

        Returns:
            Обновленный комментарий или None
        """
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return None

        # Обновляем статус
        if "is_viewed" in status_updates and status_updates["is_viewed"]:
            comment.mark_as_viewed()

        if "is_processed" in status_updates and status_updates["is_processed"]:
            comment.mark_as_processed()

        if "is_archived" in status_updates and status_updates["is_archived"]:
            comment.archive()

        await self.comment_repository.save(comment)
        return comment

    async def get_comments_statistics(
        self, group_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Получить статистику по комментариям (мигрировано из CommentService)

        Args:
            group_id: ID группы (опционально)

        Returns:
            Статистика по комментариям
        """
        # Получаем все комментарии
        all_comments = await self.comment_repository.find_all()

        # Фильтруем по группе если указана
        if group_id:
            all_comments = [c for c in all_comments if c.group_id == group_id]

        # Вычисляем статистику
        total_comments = len(all_comments)
        viewed_comments = len([c for c in all_comments if c.is_viewed])
        processed_comments = len([c for c in all_comments if c.is_processed])
        archived_comments = len([c for c in all_comments if c.is_archived])

        return {
            "total_comments": total_comments,
            "viewed_comments": viewed_comments,
            "processed_comments": processed_comments,
            "archived_comments": archived_comments,
            "unprocessed_comments": total_comments - processed_comments,
            "view_rate": (
                (viewed_comments / total_comments * 100)
                if total_comments > 0
                else 0
            ),
            "archive_rate": (
                (archived_comments / total_comments * 100)
                if total_comments > 0
                else 0
            ),
        }

    async def get_comment_statistics(
        self, group_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Получить статистику по комментариям"""
        comments = await self.comment_repository.find_all()

        if group_id:
            comments = [c for c in comments if c.group_id == group_id]

        total_comments = len(comments)
        viewed_comments = len([c for c in comments if c.is_viewed])
        processed_comments = len([c for c in comments if c.is_processed])
        archived_comments = len([c for c in comments if c.is_archived])

        return {
            "total_comments": total_comments,
            "viewed_comments": viewed_comments,
            "processed_comments": processed_comments,
            "archived_comments": archived_comments,
            "unprocessed_comments": total_comments - processed_comments,
        }

    # =============== РЕАЛЬНАЯ МИГРАЦИЯ ИЗ comment_service.py ===============

    async def get_comment_by_id_with_details(
        self, comment_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получить комментарий по ID с полной информацией (мигрировано из CommentService)

        Args:
            comment_id: ID комментария

        Returns:
            Полная информация о комментарии или None
        """
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return None

        return {
            "id": comment.id,
            "vk_id": getattr(comment, "vk_comment_id", None),
            "text": comment.content.text if comment.content else "",
            "author_id": (
                comment.content.author_id if comment.content else None
            ),
            "author_name": (
                comment.content.author_name if comment.content else None
            ),
            "published_at": comment.published_at.isoformat(),
            "is_viewed": comment.is_viewed,
            "is_processed": comment.is_processed,
            "is_archived": comment.is_archived,
            "matched_keywords_count": len(comment.keyword_matches),
            "processing_status": comment.get_processing_status(),
            "can_be_edited": comment.can_be_edited(),
            "relevance_score": comment.calculate_relevance_score(),
        }

    async def update_comment_fields(
        self, comment_id: int, fields_to_update: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить поля комментария (мигрировано из CommentService)

        Args:
            comment_id: ID комментария
            fields_to_update: Поля для обновления

        Returns:
            Обновленная информация о комментарии или None
        """
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return None

        updated_fields = []
        for field, value in fields_to_update.items():
            if hasattr(comment, field):
                setattr(comment, field, value)
                updated_fields.append(field)

        await self.comment_repository.save(comment)

        return {
            "comment_id": comment_id,
            "updated_fields": updated_fields,
            "updated_at": comment.updated_at.isoformat(),
        }

    async def bulk_update_comments_status(
        self, comment_ids: List[int], status_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Массовое обновление статуса комментариев (мигрировано из CommentService)

        Args:
            comment_ids: Список ID комментариев
            status_updates: Обновления статуса

        Returns:
            Результат массовой операции
        """
        updated_count = 0
        errors = []

        for comment_id in comment_ids:
            try:
                result = await self.update_comment_status(
                    comment_id, status_updates
                )
                if result:
                    updated_count += 1
                else:
                    errors.append(f"Comment {comment_id} not found")
            except Exception as e:
                errors.append(f"Error updating comment {comment_id}: {str(e)}")

        return {
            "total_requested": len(comment_ids),
            "updated_count": updated_count,
            "errors": errors,
            "success_rate": (
                (updated_count / len(comment_ids) * 100) if comment_ids else 0
            ),
        }

    # =============== ПРОДОЛЖЕНИЕ МИГРАЦИИ ИЗ comment_service.py ===============

    async def search_comments_with_filters(
        self,
        text: Optional[str] = None,
        group_id: Optional[int] = None,
        author_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        is_viewed: Optional[bool] = None,
        is_processed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Поиск комментариев с расширенными фильтрами (мигрировано из CommentService)

        Args:
            text: Текст для поиска
            group_id: ID группы
            author_id: ID автора
            date_from: Дата начала (ISO формат)
            date_to: Дата окончания (ISO формат)
            is_viewed: Фильтр по просмотру
            is_processed: Фильтр по обработке
            is_archived: Фильтр по архиву
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Результаты поиска с пагинацией
        """
        from datetime import datetime
        from ..infrastructure.repositories.base import QueryOptions

        # Создаем фильтры
        filters = {}

        if group_id is not None:
            filters["group_id"] = group_id
        if is_viewed is not None:
            filters["is_viewed"] = is_viewed
        if is_processed is not None:
            filters["is_processed"] = is_processed
        if is_archived is not None:
            filters["is_archived"] = is_archived

        # Создаем QueryOptions
        options = QueryOptions(
            limit=limit,
            offset=offset,
            filters=filters,
            order_by="published_at",
            order_direction="desc",
        )

        # Получаем комментарии
        comments = await self.comment_repository.find_all(options)

        # Применяем дополнительные фильтры
        if text:
            comments = [
                c
                for c in comments
                if text.lower() in (c.content.text or "").lower()
            ]

        if author_id is not None:
            comments = [
                c for c in comments if c.content.author_id == author_id
            ]

        if date_from:
            from_date = datetime.fromisoformat(
                date_from.replace("Z", "+00:00")
            )
            comments = [c for c in comments if c.published_at >= from_date]

        if date_to:
            to_date = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
            comments = [c for c in comments if c.published_at <= to_date]

        # Преобразуем в response формат
        comment_responses = []
        for comment in comments:
            response = {
                "id": comment.id,
                "vk_id": getattr(comment, "vk_comment_id", None),
                "text": comment.content.text if comment.content else "",
                "author_id": (
                    comment.content.author_id if comment.content else None
                ),
                "author_name": (
                    comment.content.author_name if comment.content else None
                ),
                "published_at": comment.published_at.isoformat(),
                "is_viewed": comment.is_viewed,
                "is_processed": comment.is_processed,
                "is_archived": comment.is_archived,
                "matched_keywords_count": len(comment.keyword_matches),
                "matched_keywords": (
                    [match.keyword.word for match in comment.keyword_matches]
                    if comment.keyword_matches
                    else []
                ),
            }
            comment_responses.append(response)

        return {
            "comments": comment_responses,
            "total": len(comment_responses),
            "limit": limit,
            "offset": offset,
            "has_next": len(comment_responses) == limit,
        }

    async def get_comment_by_id_detailed(
        self, comment_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получить комментарий по ID с детальной информацией (мигрировано из CommentService)

        Args:
            comment_id: ID комментария

        Returns:
            Детальная информация о комментарии или None
        """
        from ..domain.comment import Comment

        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return None

        # Получаем связанные данные
        return {
            "id": comment.id,
            "vk_id": getattr(comment, "vk_comment_id", None),
            "text": comment.content.text if comment.content else "",
            "author_id": (
                comment.content.author_id if comment.content else None
            ),
            "author_name": (
                comment.content.author_name if comment.content else None
            ),
            "published_at": comment.published_at.isoformat(),
            "post_id": comment.post_id,
            "is_viewed": comment.is_viewed,
            "viewed_at": (
                comment.viewed_at.isoformat() if comment.viewed_at else None
            ),
            "is_processed": comment.is_processed,
            "processed_at": (
                comment.processed_at.isoformat()
                if comment.processed_at
                else None
            ),
            "is_archived": comment.is_archived,
            "archived_at": (
                comment.archived_at.isoformat()
                if comment.archived_at
                else None
            ),
            "matched_keywords_count": len(comment.keyword_matches),
            "matched_keywords": (
                [match.keyword.word for match in comment.keyword_matches]
                if comment.keyword_matches
                else []
            ),
            "keyword_matches": (
                [
                    {
                        "keyword": match.keyword.word,
                        "position": match.position,
                        "context": match.matched_text,
                    }
                    for match in comment.keyword_matches
                ]
                if comment.keyword_matches
                else []
            ),
            "processing_status": comment.get_processing_status(),
            "can_be_edited": comment.can_be_edited(),
            "relevance_score": comment.calculate_relevance_score(),
        }

    async def update_comment_full(
        self, comment_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Полное обновление комментария (мигрировано из CommentService)

        Args:
            comment_id: ID комментария
            update_data: Данные для обновления

        Returns:
            Обновленный комментарий или None
        """
        comment = await self.comment_repository.find_by_id(comment_id)
        if not comment:
            return None

        from datetime import datetime

        # Обновляем поля
        updated_fields = []
        for field, value in update_data.items():
            if hasattr(comment, field):
                setattr(comment, field, value)
                updated_fields.append(field)

                # Устанавливаем timestamp для специальных полей
                if field == "is_viewed" and value and not comment.viewed_at:
                    comment.viewed_at = datetime.utcnow()
                elif (
                    field == "is_archived"
                    and value
                    and not comment.archived_at
                ):
                    comment.archived_at = datetime.utcnow()

        # Сохраняем изменения
        await self.comment_repository.save(comment)

        return await self.get_comment_by_id_detailed(comment_id)

    async def get_comments_count_with_filters(
        self,
        group_id: Optional[int] = None,
        is_viewed: Optional[bool] = None,
        is_processed: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """
        Подсчет комментариев с фильтрами (мигрировано из CommentService)

        Args:
            group_id: ID группы
            is_viewed: Фильтр по просмотру
            is_processed: Фильтр по обработке
            is_archived: Фильтр по архиву

        Returns:
            Количество комментариев
        """
        # Создаем спецификацию для фильтрации
        from ..domain.specifications.comment import CommentSpecification

        spec = CommentSpecification()

        if group_id is not None:
            spec = spec.by_group_id(group_id)

        if is_viewed is not None:
            spec = spec.by_viewed_status(is_viewed)

        if is_processed is not None:
            spec = spec.by_processed_status(is_processed)

        if is_archived is not None:
            spec = spec.by_archived_status(is_archived)

        return await self.comment_repository.count(spec)

    async def get_comments_paginated_detailed(
        self,
        group_id: int,
        limit: int = 50,
        offset: int = 0,
        include_group_info: bool = False,
    ) -> Dict[str, Any]:
        """
        Пагинированная выборка комментариев группы с деталями (мигрировано из CommentService)

        Args:
            group_id: ID группы
            limit: Максимальное количество
            offset: Смещение
            include_group_info: Включить информацию о группе

        Returns:
            Пагинированный результат
        """
        from ..infrastructure.repositories.base import QueryOptions

        options = QueryOptions(
            limit=limit,
            offset=offset,
            filters={"group_id": group_id},
            order_by="published_at",
            order_direction="desc",
        )

        comments = await self.comment_repository.find_all(options)

        # Преобразуем в response формат
        comment_responses = []
        for comment in comments:
            response = {
                "id": comment.id,
                "vk_id": getattr(comment, "vk_comment_id", None),
                "text": comment.content.text if comment.content else "",
                "author_id": (
                    comment.content.author_id if comment.content else None
                ),
                "author_name": (
                    comment.content.author_name if comment.content else None
                ),
                "published_at": comment.published_at.isoformat(),
                "is_viewed": comment.is_viewed,
                "is_processed": comment.is_processed,
                "is_archived": comment.is_archived,
                "matched_keywords_count": len(comment.keyword_matches),
            }

            if include_group_info and comment.post and comment.post.group:
                response["group"] = {
                    "id": comment.post.group.id,
                    "vk_id": comment.post.group.vk_id,
                    "name": comment.post.group.name,
                    "screen_name": comment.post.group.screen_name,
                    "is_active": comment.post.group.is_active,
                }

            comment_responses.append(response)

        return {
            "comments": comment_responses,
            "total": await self.get_comments_count_with_filters(
                group_id=group_id
            ),
            "limit": limit,
            "offset": offset,
            "has_next": len(comment_responses) == limit,
            "has_prev": offset > 0,
        }

    async def get_comment_stats_detailed(
        self, group_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Детальная статистика по комментариям (мигрировано из CommentService)

        Args:
            group_id: ID группы (опционально)

        Returns:
            Детальная статистика
        """
        # Получаем все комментарии
        all_comments = await self.comment_repository.find_all()

        # Фильтруем по группе если указана
        if group_id:
            all_comments = [c for c in all_comments if c.group_id == group_id]

        # Вычисляем статистику
        total_comments = len(all_comments)
        viewed_comments = len([c for c in all_comments if c.is_viewed])
        archived_comments = len([c for c in all_comments if c.is_archived])
        processed_comments = len([c for c in all_comments if c.is_processed])

        # Статистика по ключевым словам
        total_keywords = sum(len(c.keyword_matches) for c in all_comments)
        avg_keywords_per_comment = (
            total_keywords / total_comments if total_comments > 0 else 0
        )

        return {
            "total_comments": total_comments,
            "viewed_comments": viewed_comments,
            "archived_comments": archived_comments,
            "processed_comments": processed_comments,
            "unprocessed_comments": total_comments - processed_comments,
            "total_matched_keywords": total_keywords,
            "avg_keywords_per_comment": round(avg_keywords_per_comment, 2),
            "view_rate": (
                round(viewed_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            ),
            "archive_rate": (
                round(archived_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            ),
            "processing_rate": (
                round(processed_comments / total_comments * 100, 2)
                if total_comments > 0
                else 0
            ),
        }

    async def archive_old_comments_enhanced(
        self,
        days_old: int = 30,
        group_id: Optional[int] = None,
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Улучшенная архивация старых комментариев (мигрировано из CommentService)

        Args:
            days_old: Возраст комментариев в днях
            group_id: ID группы (опционально)
            batch_size: Размер батча для обработки

        Returns:
            Результат операции архивирования
        """
        from datetime import datetime, timedelta

        # Определяем дату отсечения
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Получаем комментарии для архивирования
        from ..infrastructure.repositories.base import QueryOptions

        filters = {}
        if group_id is not None:
            filters["group_id"] = group_id

        options = QueryOptions(filters=filters)
        all_comments = await self.comment_repository.find_all(options)

        # Фильтруем по дате
        comments_to_archive = [
            c
            for c in all_comments
            if c.published_at < cutoff_date and not c.is_archived
        ]

        archived_count = 0
        for i in range(0, len(comments_to_archive), batch_size):
            batch = comments_to_archive[i : i + batch_size]

            for comment in batch:
                comment.archive()
                await self.comment_repository.save(comment)
                archived_count += 1

        return {
            "archived_count": archived_count,
            "total_candidates": len(comments_to_archive),
            "days_old": days_old,
            "group_id": group_id,
            "cutoff_date": cutoff_date.isoformat(),
            "batch_size": batch_size,
            "batches_processed": (archived_count + batch_size - 1)
            // batch_size,
        }
