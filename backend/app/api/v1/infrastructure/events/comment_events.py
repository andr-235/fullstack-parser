"""
Domain Events для комментариев (DDD Infrastructure Layer)

Конкретные реализации Domain Events для работы с комментариями
в рамках DDD архитектуры.
"""

from typing import List, Optional, Dict, Any
from .domain_event_publisher import DomainEvent


class CommentCreatedEvent(DomainEvent):
    """
    Событие создания комментария

    Генерируется при создании нового комментария в системе.
    """

    def __init__(
        self,
        comment_id: int,
        group_id: int,
        post_id: int,
        author_id: Optional[int] = None,
        text_length: int = 0,
    ):
        """
        Args:
            comment_id: ID созданного комментария
            group_id: ID группы VK
            post_id: ID поста VK
            author_id: ID автора комментария
            text_length: Длина текста комментария
        """
        super().__init__(comment_id)
        self.group_id = group_id
        self.post_id = post_id
        self.author_id = author_id
        self.text_length = text_length

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "group_id": self.group_id,
            "post_id": self.post_id,
            "author_id": self.author_id,
            "text_length": self.text_length,
        }


class CommentViewedEvent(DomainEvent):
    """
    Событие просмотра комментария

    Генерируется при первом просмотре комментария модератором.
    """

    def __init__(
        self,
        comment_id: int,
        viewer_id: Optional[str] = None,
        viewed_at: Optional[str] = None,
    ):
        """
        Args:
            comment_id: ID просмотренного комментария
            viewer_id: ID пользователя, просмотревшего комментарий
            viewed_at: Время просмотра (ISO формат)
        """
        super().__init__(comment_id)
        self.viewer_id = viewer_id
        self.viewed_at = viewed_at

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {"viewer_id": self.viewer_id, "viewed_at": self.viewed_at}


class CommentProcessedEvent(DomainEvent):
    """
    Событие обработки комментария

    Генерируется при завершении обработки комментария системой.
    """

    def __init__(
        self,
        comment_id: int,
        processing_result: str = "success",
        processing_time: Optional[float] = None,
        matched_keywords: Optional[List[str]] = None,
    ):
        """
        Args:
            comment_id: ID обработанного комментария
            processing_result: Результат обработки (success, failed, etc.)
            processing_time: Время обработки в секундах
            matched_keywords: Список найденных ключевых слов
        """
        super().__init__(comment_id)
        self.processing_result = processing_result
        self.processing_time = processing_time
        self.matched_keywords = matched_keywords or []
        self.keywords_count = len(self.matched_keywords)

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "processing_result": self.processing_result,
            "processing_time": self.processing_time,
            "matched_keywords": self.matched_keywords,
            "keywords_count": self.keywords_count,
        }


class CommentArchivedEvent(DomainEvent):
    """
    Событие архивирования комментария

    Генерируется при перемещении комментария в архив.
    """

    def __init__(
        self,
        comment_id: int,
        reason: str = "manual",
        archived_by: Optional[str] = None,
    ):
        """
        Args:
            comment_id: ID архивированного комментария
            reason: Причина архивирования
            archived_by: Пользователь, выполнивший архивирование
        """
        super().__init__(comment_id)
        self.reason = reason
        self.archived_by = archived_by

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {"reason": self.reason, "archived_by": self.archived_by}


class CommentKeywordMatchedEvent(DomainEvent):
    """
    Событие совпадения комментария с ключевыми словами

    Генерируется при обнаружении совпадений комментария с ключевыми словами.
    """

    def __init__(
        self,
        comment_id: int,
        keyword_id: int,
        keyword_word: str,
        match_positions: Optional[List[int]] = None,
        match_context: Optional[str] = None,
    ):
        """
        Args:
            comment_id: ID комментария
            keyword_id: ID ключевого слова
            keyword_word: Текст ключевого слова
            match_positions: Позиции совпадений в тексте
            match_context: Контекст совпадения
        """
        super().__init__(comment_id)
        self.keyword_id = keyword_id
        self.keyword_word = keyword_word
        self.match_positions = match_positions or []
        self.match_context = match_context

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "keyword_id": self.keyword_id,
            "keyword_word": self.keyword_word,
            "match_positions": self.match_positions,
            "match_context": self.match_context,
        }


class CommentBulkOperationEvent(DomainEvent):
    """
    Событие массовой операции с комментариями

    Генерируется при выполнении операций над несколькими комментариями.
    """

    def __init__(
        self,
        operation_type: str,
        comment_ids: List[int],
        operation_params: Optional[Dict[str, Any]] = None,
        affected_count: int = 0,
    ):
        """
        Args:
            operation_type: Тип операции (archive, process, delete, etc.)
            comment_ids: Список ID комментариев
            operation_params: Параметры операции
            affected_count: Количество затронутых комментариев
        """
        super().__init__(
            comment_ids[0] if comment_ids else 0
        )  # Используем первый ID как aggregate_id
        self.operation_type = operation_type
        self.comment_ids = comment_ids
        self.operation_params = operation_params or {}
        self.affected_count = affected_count

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "operation_type": self.operation_type,
            "comment_ids": self.comment_ids,
            "operation_params": self.operation_params,
            "affected_count": self.affected_count,
        }


# Вспомогательные функции для создания событий


def create_comment_created_event(
    comment_id: int,
    group_id: int,
    post_id: int,
    author_id: Optional[int] = None,
    text_length: int = 0,
) -> CommentCreatedEvent:
    """
    Создать событие создания комментария

    Args:
        comment_id: ID комментария
        group_id: ID группы
        post_id: ID поста
        author_id: ID автора
        text_length: Длина текста

    Returns:
        CommentCreatedEvent
    """
    return CommentCreatedEvent(
        comment_id=comment_id,
        group_id=group_id,
        post_id=post_id,
        author_id=author_id,
        text_length=text_length,
    )


def create_comment_viewed_event(
    comment_id: int, viewer_id: Optional[str] = None
) -> CommentViewedEvent:
    """
    Создать событие просмотра комментария

    Args:
        comment_id: ID комментария
        viewer_id: ID просмотра

    Returns:
        CommentViewedEvent
    """
    return CommentViewedEvent(comment_id=comment_id, viewer_id=viewer_id)


def create_comment_processed_event(
    comment_id: int,
    matched_keywords: Optional[List[str]] = None,
    processing_time: Optional[float] = None,
) -> CommentProcessedEvent:
    """
    Создать событие обработки комментария

    Args:
        comment_id: ID комментария
        matched_keywords: Найденные ключевые слова
        processing_time: Время обработки

    Returns:
        CommentProcessedEvent
    """
    return CommentProcessedEvent(
        comment_id=comment_id,
        matched_keywords=matched_keywords,
        processing_time=processing_time,
    )


def create_comment_keyword_matched_event(
    comment_id: int,
    keyword_id: int,
    keyword_word: str,
    match_context: Optional[str] = None,
) -> CommentKeywordMatchedEvent:
    """
    Создать событие совпадения с ключевым словом

    Args:
        comment_id: ID комментария
        keyword_id: ID ключевого слова
        keyword_word: Текст ключевого слова
        match_context: Контекст совпадения

    Returns:
        CommentKeywordMatchedEvent
    """
    return CommentKeywordMatchedEvent(
        comment_id=comment_id,
        keyword_id=keyword_id,
        keyword_word=keyword_word,
        match_context=match_context,
    )


def create_comment_bulk_operation_event(
    operation_type: str,
    comment_ids: List[int],
    operation_params: Optional[Dict[str, Any]] = None,
) -> CommentBulkOperationEvent:
    """
    Создать событие массовой операции

    Args:
        operation_type: Тип операции
        comment_ids: ID комментариев
        operation_params: Параметры операции

    Returns:
        CommentBulkOperationEvent
    """
    return CommentBulkOperationEvent(
        operation_type=operation_type,
        comment_ids=comment_ids,
        operation_params=operation_params,
        affected_count=len(comment_ids),
    )
