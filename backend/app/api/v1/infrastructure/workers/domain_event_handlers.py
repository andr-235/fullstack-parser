"""
Domain Event Handlers (DDD Infrastructure Layer)

Обработчики Domain Events для асинхронной обработки важных событий домена.
Реализуют паттерн Event Handler в рамках DDD архитектуры.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from ..events.domain_event_publisher import (
    DomainEvent,
    domain_event_publisher,
    subscribe_to,
)
from ..events.comment_events import (
    CommentCreatedEvent,
    CommentViewedEvent,
    CommentProcessedEvent,
    CommentArchivedEvent,
    CommentKeywordMatchedEvent,
    CommentBulkOperationEvent,
)
from ..services.cache_service import RedisCacheService
from ..services.base import NotificationService, MonitoringService

logger = logging.getLogger(__name__)


class DomainEventHandler:
    """
    Базовый класс для обработчиков Domain Events

    Обеспечивает унифицированный интерфейс для обработки различных типов событий.
    """

    def __init__(
        self,
        cache_service: RedisCacheService,
        notification_service: NotificationService = None,
        monitoring_service: MonitoringService = None,
    ):
        """
        Инициализация обработчика

        Args:
            cache_service: Сервис кеширования
            notification_service: Сервис уведомлений (опционально)
            monitoring_service: Сервис мониторинга (опционально)
        """
        self.cache_service = cache_service
        self.notification_service = notification_service
        self.monitoring_service = monitoring_service

    async def handle_event(self, event: DomainEvent) -> None:
        """
        Обработать Domain Event

        Args:
            event: Domain Event для обработки
        """
        event_type = event.event_type

        # Логируем обработку события
        logger.info(
            f"Processing domain event: {event_type} (ID: {event.event_id})"
        )

        # Отправляем метрику в систему мониторинга
        if self.monitoring_service:
            await self.monitoring_service.increment_counter(
                "domain_events_processed", tags={"event_type": event_type}
            )

        try:
            # Маршрутизируем событие соответствующему обработчику
            if isinstance(event, CommentCreatedEvent):
                await self.handle_comment_created(event)
            elif isinstance(event, CommentViewedEvent):
                await self.handle_comment_viewed(event)
            elif isinstance(event, CommentProcessedEvent):
                await self.handle_comment_processed(event)
            elif isinstance(event, CommentArchivedEvent):
                await self.handle_comment_archived(event)
            elif isinstance(event, CommentKeywordMatchedEvent):
                await self.handle_comment_keyword_matched(event)
            elif isinstance(event, CommentBulkOperationEvent):
                await self.handle_comment_bulk_operation(event)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(
                f"Error handling domain event {event_type}: {e}", exc_info=True
            )

            # Отправляем метрику об ошибке
            if self.monitoring_service:
                await self.monitoring_service.increment_counter(
                    "domain_event_errors",
                    tags={"event_type": event_type, "error": str(e)},
                )

    async def handle_comment_created(self, event: CommentCreatedEvent) -> None:
        """
        Обработать событие создания комментария

        Args:
            event: CommentCreatedEvent
        """
        logger.info(f"Comment created: {event.aggregate_id}")

        # Инвалидируем кеш для списка комментариев группы
        await self.cache_service.invalidate_entity_collection("comment")

        # Инвалидируем кеш для статистики группы
        await self.cache_service.delete(f"group_stats:{event.group_id}")

        # Отправляем уведомление о новом комментарии
        if self.notification_service:
            await self._notify_new_comment(event)

        # Логируем событие
        if self.monitoring_service:
            await self.monitoring_service.log_event(
                "comment_created",
                f"New comment {event.aggregate_id} in group {event.group_id}",
                context={
                    "comment_id": event.aggregate_id,
                    "group_id": event.group_id,
                    "post_id": event.post_id,
                    "author_id": event.author_id,
                    "text_length": event.text_length,
                },
            )

    async def handle_comment_viewed(self, event: CommentViewedEvent) -> None:
        """
        Обработать событие просмотра комментария

        Args:
            event: CommentViewedEvent
        """
        logger.info(f"Comment viewed: {event.aggregate_id}")

        # Инвалидируем кеш комментария
        await self.cache_service.invalidate_domain_entity(
            "comment", str(event.aggregate_id)
        )

        # Обновляем статистику просмотров
        if self.monitoring_service:
            await self.monitoring_service.increment_counter(
                "comments_viewed",
                tags={"group_id": "unknown"},  # Можно получить из контекста
            )

    async def handle_comment_processed(
        self, event: CommentProcessedEvent
    ) -> None:
        """
        Обработать событие обработки комментария

        Args:
            event: CommentProcessedEvent
        """
        logger.info(f"Comment processed: {event.aggregate_id}")

        # Инвалидируем кеш комментария
        await self.cache_service.invalidate_domain_entity(
            "comment", str(event.aggregate_id)
        )

        # Обновляем статистику обработанных комментариев
        if self.monitoring_service:
            await self.monitoring_service.increment_counter(
                "comments_processed", tags={"result": event.processing_result}
            )

            # Логируем время обработки
            if event.processing_time:
                await self.monitoring_service.record_histogram(
                    "comment_processing_time", event.processing_time
                )

        # Если найдены ключевые слова, отправляем уведомление
        if event.matched_keywords and self.notification_service:
            await self._notify_keyword_match(event)

    async def handle_comment_archived(
        self, event: CommentArchivedEvent
    ) -> None:
        """
        Обработать событие архивирования комментария

        Args:
            event: CommentArchivedEvent
        """
        logger.info(f"Comment archived: {event.aggregate_id}")

        # Инвалидируем кеш комментария
        await self.cache_service.invalidate_domain_entity(
            "comment", str(event.aggregate_id)
        )

        # Обновляем статистику архивированных комментариев
        if self.monitoring_service:
            await self.monitoring_service.increment_counter(
                "comments_archived", tags={"reason": event.reason}
            )

    async def handle_comment_keyword_matched(
        self, event: CommentKeywordMatchedEvent
    ) -> None:
        """
        Обработать событие совпадения с ключевым словом

        Args:
            event: CommentKeywordMatchedEvent
        """
        logger.info(
            f"Comment keyword matched: {event.aggregate_id} -> {event.keyword_word}"
        )

        # Инвалидируем кеш комментария
        await self.cache_service.invalidate_domain_entity(
            "comment", str(event.aggregate_id)
        )

        # Обновляем статистику совпадений с ключевыми словами
        if self.monitoring_service:
            await self.monitoring_service.increment_counter(
                "keyword_matches", tags={"keyword": event.keyword_word}
            )

        # Отправляем уведомление о совпадении
        if self.notification_service:
            await self._notify_keyword_match_single(event)

    async def handle_comment_bulk_operation(
        self, event: CommentBulkOperationEvent
    ) -> None:
        """
        Обработать событие массовой операции

        Args:
            event: CommentBulkOperationEvent
        """
        logger.info(
            f"Bulk operation: {event.operation_type} on {event.affected_count} comments"
        )

        # Инвалидируем кеш коллекций комментариев
        await self.cache_service.invalidate_entity_collection("comment")

        # Логируем массовую операцию
        if self.monitoring_service:
            await self.monitoring_service.log_event(
                "bulk_operation",
                f"Bulk {event.operation_type} on {event.affected_count} comments",
                context={
                    "operation_type": event.operation_type,
                    "comment_ids": event.comment_ids[:10],  # Первые 10 ID
                    "affected_count": event.affected_count,
                    "operation_params": event.operation_params,
                },
            )

    async def _notify_new_comment(self, event: CommentCreatedEvent) -> None:
        """
        Отправить уведомление о новом комментарии

        Args:
            event: CommentCreatedEvent
        """
        try:
            message = (
                f"New comment in group {event.group_id}, post {event.post_id}"
            )
            await self.notification_service.send_email(
                to="moderators@vkcomments.com",
                subject="New Comment Requires Review",
                body=message,
            )
        except Exception as e:
            logger.error(f"Failed to send new comment notification: {e}")

    async def _notify_keyword_match(
        self, event: CommentProcessedEvent
    ) -> None:
        """
        Отправить уведомление о совпадениях с ключевыми словами

        Args:
            event: CommentProcessedEvent
        """
        try:
            keywords_str = ", ".join(
                event.matched_keywords[:5]
            )  # Первые 5 слов
            if len(event.matched_keywords) > 5:
                keywords_str += f" (+{len(event.matched_keywords) - 5} more)"

            message = f"Comment {event.aggregate_id} matched keywords: {keywords_str}"

            await self.notification_service.send_email(
                to="analysts@vkcomments.com",
                subject="Keyword Match Detected",
                body=message,
            )
        except Exception as e:
            logger.error(f"Failed to send keyword match notification: {e}")

    async def _notify_keyword_match_single(
        self, event: CommentKeywordMatchedEvent
    ) -> None:
        """
        Отправить уведомление об одиночном совпадении с ключевым словом

        Args:
            event: CommentKeywordMatchedEvent
        """
        try:
            # Можно реализовать более детализированные уведомления
            # в зависимости от важности ключевого слова
            pass
        except Exception as e:
            logger.error(
                f"Failed to send single keyword match notification: {e}"
            )


# Функции-обработчики для подписки


@subscribe_to("CommentCreatedEvent")
async def handle_comment_created_event(event: CommentCreatedEvent) -> None:
    """
    Глобальный обработчик события создания комментария

    Args:
        event: CommentCreatedEvent
    """
    # Создаем временный обработчик для демонстрации
    handler = DomainEventHandler(
        cache_service=RedisCacheService(),
        # notification_service и monitoring_service можно добавить позже
    )
    await handler.handle_comment_created(event)


@subscribe_to("CommentProcessedEvent")
async def handle_comment_processed_event(event: CommentProcessedEvent) -> None:
    """
    Глобальный обработчик события обработки комментария

    Args:
        event: CommentProcessedEvent
    """
    handler = DomainEventHandler(cache_service=RedisCacheService())
    await handler.handle_comment_processed(event)


@subscribe_to("CommentKeywordMatchedEvent")
async def handle_comment_keyword_matched_event(
    event: CommentKeywordMatchedEvent,
) -> None:
    """
    Глобальный обработчик события совпадения с ключевым словом

    Args:
        event: CommentKeywordMatchedEvent
    """
    handler = DomainEventHandler(cache_service=RedisCacheService())
    await handler.handle_comment_keyword_matched(event)


# Функция для настройки всех обработчиков событий
def setup_domain_event_handlers(
    cache_service: RedisCacheService,
    notification_service: NotificationService = None,
    monitoring_service: MonitoringService = None,
) -> DomainEventHandler:
    """
    Настроить все обработчики Domain Events

    Args:
        cache_service: Сервис кеширования
        notification_service: Сервис уведомлений
        monitoring_service: Сервис мониторинга

    Returns:
        Настроенный обработчик
    """
    handler = DomainEventHandler(
        cache_service=cache_service,
        notification_service=notification_service,
        monitoring_service=monitoring_service,
    )

    # Подписываемся на все типы событий
    domain_event_publisher.subscribe(
        "CommentCreatedEvent", handler.handle_comment_created
    )
    domain_event_publisher.subscribe(
        "CommentViewedEvent", handler.handle_comment_viewed
    )
    domain_event_publisher.subscribe(
        "CommentProcessedEvent", handler.handle_comment_processed
    )
    domain_event_publisher.subscribe(
        "CommentArchivedEvent", handler.handle_comment_archived
    )
    domain_event_publisher.subscribe(
        "CommentKeywordMatchedEvent", handler.handle_comment_keyword_matched
    )
    domain_event_publisher.subscribe(
        "CommentBulkOperationEvent", handler.handle_comment_bulk_operation
    )

    logger.info("Domain Event handlers configured successfully")
    return handler
