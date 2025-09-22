"""
Сервис для работы с комментариями
"""

import logging
from typing import List, Optional

from comments.models import Comment
from comments.repository import CommentRepository
from comments.schemas import (
    BatchKeywordAnalysisRequest,
    BatchKeywordAnalysisResponse,
    CommentCreate,
    CommentFilter,
    CommentListResponse,
    CommentResponse,
    CommentStats,
    CommentUpdate,
    DEFAULT_KEYWORD_CONFIDENCE,
    KeywordAnalysisRequest,
    KeywordAnalysisResponse,
    KeywordMatch,
    KeywordSearchRequest,
    KeywordSearchResponse,
    KeywordStatisticsResponse,
    MIN_COMMENT_TEXT_LENGTH,
    MIN_WORD_LENGTH,
)

logger = logging.getLogger(__name__)


class CommentService:
    """
    Сервис для работы с комментариями.

    Обеспечивает бизнес-логику для операций с комментариями,
    включая валидацию, анализ ключевых слов и статистику.
    """

    def __init__(self, repository: CommentRepository):
        self.repository = repository

    async def get_comment(self, comment_id: int, include_author: bool = False) -> Optional[CommentResponse]:
        """
        Получить комментарий по ID.

        Args:
            comment_id: ID комментария
            include_author: Включать ли информацию об авторе

        Returns:
            CommentResponse или None, если комментарий не найден

        Raises:
            ValueError: Если comment_id не положительное число
        """
        if comment_id <= 0:
            raise ValueError("ID комментария должен быть положительным числом")

        comment = await self.repository.get_by_id(comment_id, include_author)
        if not comment:
            return None

        return self._to_response(comment, include_author)

    async def get_comment_by_vk_id(self, vk_id: int) -> Optional[CommentResponse]:
        """
        Получить комментарий по VK ID.

        Args:
            vk_id: VK ID комментария

        Returns:
            CommentResponse или None, если комментарий не найден

        Raises:
            ValueError: Если vk_id не положительное число
        """
        if vk_id <= 0:
            raise ValueError("VK ID должен быть положительным числом")

        comment = await self.repository.get_by_vk_id(vk_id)
        if not comment:
            return None

        return self._to_response(comment)

    async def get_comments(
        self,
        filters: Optional[CommentFilter] = None,
        limit: int = 20,
        offset: int = 0,
        include_author: bool = False,
    ) -> CommentListResponse:
        """
        Получить список комментариев с фильтрацией.

        Args:
            filters: Фильтры для применения
            limit: Максимальное количество комментариев
            offset: Смещение для пагинации
            include_author: Включать ли информацию об авторе

        Returns:
            CommentListResponse с комментариями и метаданными пагинации

        Raises:
            ValueError: Если параметры limit или offset некорректны
        """
        if limit <= 0 or limit > 100:
            raise ValueError("Limit должен быть между 1 и 100")
        if offset < 0:
            raise ValueError("Offset не может быть отрицательным")

        comments = await self.repository.get_list(filters, limit, offset, include_author)
        total = await self.repository.count(filters)

        return CommentListResponse(
            items=[self._to_response(comment, include_author) for comment in comments],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def create_comment(self, comment_data: CommentCreate) -> CommentResponse:
        """Создать комментарий"""
        # Проверяем, что комментарий с таким VK ID не существует
        existing = await self.repository.get_by_vk_id(comment_data.vk_id)
        if existing:
            raise ValueError(f"Комментарий с VK ID {comment_data.vk_id} уже существует")

        comment = await self.repository.create(comment_data)
        return self._to_response(comment)

    async def update_comment(
        self, comment_id: int, update_data: CommentUpdate
    ) -> Optional[CommentResponse]:
        """Обновить комментарий"""
        comment = await self.repository.update(comment_id, update_data)
        if not comment:
            return None

        return self._to_response(comment)

    async def delete_comment(self, comment_id: int) -> bool:
        """
        Удалить комментарий (мягкое удаление).

        Args:
            comment_id: ID комментария для удаления

        Returns:
            True, если комментарий найден и удален, False в противном случае

        Raises:
            ValueError: Если comment_id некорректен
        """
        if comment_id <= 0:
            raise ValueError("ID комментария должен быть положительным числом")

        return await self.repository.delete(comment_id)

    async def get_stats(self) -> CommentStats:
        """
        Получить статистику комментариев.

        Returns:
            CommentStats со статистикой комментариев
        """
        stats = await self.repository.get_stats()
        return CommentStats(**stats)

    # Методы для анализа ключевых слов
    async def analyze_keywords(self, request: KeywordAnalysisRequest) -> KeywordAnalysisResponse:
        """Анализ ключевых слов в комментарии"""
        try:
            # Получаем комментарий
            comment = await self.repository.get_by_id(request.comment_id)
            if not comment:
                raise ValueError(f"Комментарий с ID {request.comment_id} не найден")

            if not comment.text or len(comment.text.strip()) < MIN_COMMENT_TEXT_LENGTH:
                return KeywordAnalysisResponse(
                    comment_id=request.comment_id,
                    keywords_found=0,
                    keywords_created=0,
                    keywords_updated=0,
                    status="skipped"
                )

            # Простой анализ ключевых слов (можно заменить на более сложный)
            keywords_found = 0
            keywords_created = 0
            keywords_updated = 0

            # Извлекаем слова из текста
            words = comment.text.lower().split()
            for word in words:
                if len(word) < MIN_WORD_LENGTH:
                    continue

                # Проверяем существующую связь
                existing_match = await self.repository.get_keyword_match(request.comment_id, word)
                if existing_match:
                    keywords_updated += 1
                else:
                    keywords_created += 1
                    await self.repository.create_keyword_match(
                        request.comment_id, word, DEFAULT_KEYWORD_CONFIDENCE  # Простая уверенность
                    )

                keywords_found += 1

            return KeywordAnalysisResponse(
                comment_id=request.comment_id,
                keywords_found=keywords_found,
                keywords_created=keywords_created,
                keywords_updated=keywords_updated,
                status="success"
            )

        except Exception as e:
            logger.error(f"Ошибка анализа ключевых слов: {str(e)}")
            raise ValueError(f"Ошибка анализа ключевых слов: {str(e)}")

    async def analyze_batch_keywords(self, request: BatchKeywordAnalysisRequest) -> BatchKeywordAnalysisResponse:
        """Массовый анализ ключевых слов"""
        results = []
        total_found = 0
        total_created = 0
        total_updated = 0
        errors = 0

        for comment_id in request.comment_ids:
            try:
                analysis_request = KeywordAnalysisRequest(
                    comment_id=comment_id,
                    min_confidence=request.min_confidence,
                    max_keywords=request.max_keywords
                )
                result = await self.analyze_keywords(analysis_request)
                results.append(result)
                total_found += result.keywords_found
                total_created += result.keywords_created
                total_updated += result.keywords_updated
            except Exception as e:
                logger.error(f"Ошибка анализа комментария {comment_id}: {str(e)}")
                errors += 1
                results.append(KeywordAnalysisResponse(
                    comment_id=comment_id,
                    keywords_found=0,
                    keywords_created=0,
                    keywords_updated=0,
                    status="error"
                ))

        return BatchKeywordAnalysisResponse(
            total_processed=len(request.comment_ids),
            successful=len(request.comment_ids) - errors,
            errors=errors,
            total_keywords_found=total_found,
            total_keywords_created=total_created,
            total_keywords_updated=total_updated,
            results=results
        )

    async def search_by_keywords(self, request: KeywordSearchRequest) -> KeywordSearchResponse:
        """Поиск комментариев по ключевым словам"""
        comments = await self.repository.search_by_keywords(
            request.keywords, request.limit, request.offset
        )
        total = await self.repository.count_by_keywords(request.keywords)

        return KeywordSearchResponse(
            comments=[self._to_response(comment, include_author=True) for comment in comments],
            total=total,
            limit=request.limit,
            offset=request.offset,
            keywords=request.keywords
        )

    async def get_keyword_statistics(self) -> KeywordStatisticsResponse:
        """Получить статистику ключевых слов"""
        # Простая реализация - можно расширить
        return KeywordStatisticsResponse(
            total_keywords=0,
            total_matches=0,
            categories={},
            top_keywords=[]
        )

    def _to_response(self, comment: Comment, include_author: bool = False) -> CommentResponse:
        """Преобразовать модель в схему ответа"""
        author_data = None
        if include_author and comment.author:
            author_data = {
                "id": comment.author.id,
                "vk_id": comment.author.vk_id,
                "first_name": comment.author.first_name,
                "last_name": comment.author.last_name,
                "screen_name": comment.author.screen_name,
                "photo_url": comment.author.photo_url,
                "status": comment.author.status,
                "is_verified": comment.author.is_verified,
                "followers_count": comment.author.followers_count,
                "created_at": comment.author.created_at,
                "updated_at": comment.author.updated_at,
            }

        return CommentResponse(
            id=comment.id,
            vk_id=comment.vk_id,
            group_id=comment.group_id,
            post_id=comment.post_id,
            author_id=comment.author_id,
            text=comment.text,
            created_at=comment.created_at,
            is_deleted=comment.is_deleted,
            keyword_matches=[
                KeywordMatch(
                    keyword=match.keyword,
                    confidence=match.confidence,
                    created_at=match.created_at,
                )
                for match in comment.keyword_matches
            ],
            author=author_data,
        )

    async def get_total_comments_count(self) -> int:
        """Получить общее количество комментариев"""
        return await self.repository.get_total_count()

    async def get_comments_count_by_period(self, days: int = 30) -> int:
        """Получить количество комментариев за период"""
        return await self.repository.get_count_by_period(days)

    async def get_comments_growth_percentage(self, days: int = 30) -> float:
        """Получить процент роста комментариев за период"""
        current_period = await self.get_comments_count_by_period(days)
        total_previous = await self.get_comments_count_by_period(days * 2)
        previous_period = total_previous - current_period

        if previous_period == 0:
            return 100.0 if current_period > 0 else 0.0

        return ((current_period - previous_period) / previous_period) * 100
