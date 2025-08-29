"""
Domain Event Publisher (DDD Infrastructure Layer)

Реализация Publisher паттерна для Domain Events в рамках DDD архитектуры.
Обеспечивает асинхронную обработку доменных событий.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any
from datetime import datetime

from ...domain.base import Entity

logger = logging.getLogger(__name__)


class DomainEvent:
    """
    Базовый класс для Domain Events (DDD)

    Domain Events представляют важные изменения в доменной модели
    и используются для обеспечения слабой связанности между компонентами.
    """

    def __init__(self, aggregate_id: Any, event_version: int = 1):
        """
        Инициализация Domain Event

        Args:
            aggregate_id: ID агрегата, породившего событие
            event_version: Версия события для поддержки версионирования
        """
        self.aggregate_id = aggregate_id
        self.event_id = str(uuid.uuid4())
        self.occurred_at = datetime.utcnow()
        self.event_version = event_version
        self._frozen = False

    @property
    def event_type(self) -> str:
        """Тип события (имя класса)"""
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализация события в словарь

        Returns:
            Словарь с данными события
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": str(self.aggregate_id),
            "occurred_at": self.occurred_at.isoformat(),
            "event_version": self.event_version,
            "event_data": self._get_event_data(),
        }

    def _get_event_data(self) -> Dict[str, Any]:
        """
        Получить специфические данные события

        Returns:
            Словарь с данными события
        """
        data = {}
        for attr_name in dir(self):
            if not attr_name.startswith("_") and attr_name not in [
                "event_type",
                "to_dict",
            ]:
                value = getattr(self, attr_name)
                if not callable(value):
                    data[attr_name] = value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """
        Десериализация события из словаря

        Args:
            data: Словарь с данными события

        Returns:
            Экземпляр DomainEvent
        """
        # Создаем базовый экземпляр
        event = cls.__new__(cls)
        event.event_id = data["event_id"]
        event.aggregate_id = data["aggregate_id"]
        event.occurred_at = datetime.fromisoformat(data["occurred_at"])
        event.event_version = data.get("event_version", 1)
        event._frozen = True

        # Восстанавливаем специфические атрибуты
        event_data = data.get("event_data", {})
        for key, value in event_data.items():
            setattr(event, key, value)

        return event


class DomainEventPublisher:
    """
    Publisher для Domain Events (DDD Infrastructure Service)

    Обеспечивает асинхронную публикацию и обработку Domain Events,
    реализуя паттерн Publisher-Subscriber для слабой связанности.
    """

    def __init__(self):
        """Инициализация Publisher"""
        self._handlers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
        self._is_processing = False

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Подписать обработчик на тип события

        Args:
            event_type: Тип события (имя класса)
            handler: Асинхронная функция-обработчик
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler for event type: {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Отписать обработчик от типа события

        Args:
            event_type: Тип события
            handler: Обработчик для удаления
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.info(
                    f"Unsubscribed handler for event type: {event_type}"
                )
            except ValueError:
                logger.warning(
                    f"Handler not found for event type: {event_type}"
                )

    def add_middleware(self, middleware: Callable) -> None:
        """
        Добавить middleware для обработки событий

        Args:
            middleware: Функция middleware (async def(event, next_handler))
        """
        self._middleware.append(middleware)

    async def publish(self, event: DomainEvent) -> None:
        """
        Опубликовать Domain Event

        Args:
            event: Domain Event для публикации
        """
        if self._is_processing:
            logger.warning("Event publishing already in progress, skipping")
            return

        try:
            self._is_processing = True
            logger.info(
                f"Publishing domain event: {event.event_type} (ID: {event.event_id})"
            )

            # Получаем обработчики для данного типа события
            handlers = self._handlers.get(event.event_type, [])

            if not handlers:
                logger.debug(
                    f"No handlers found for event type: {event.event_type}"
                )
                return

            # Создаем цепочку middleware + обработчиков
            async def execute_handlers():
                for handler in handlers:
                    try:
                        # Применяем middleware
                        current_handler = handler
                        for middleware in reversed(self._middleware):
                            current_handler = self._wrap_with_middleware(
                                middleware, current_handler
                            )

                        await current_handler(event)

                    except Exception as e:
                        logger.error(
                            f"Error in event handler for {event.event_type}: {e}",
                            exc_info=True,
                        )
                        # Продолжаем обработку других обработчиков даже при ошибке

            await execute_handlers()

        finally:
            self._is_processing = False

    async def publish_events(self, events: List[DomainEvent]) -> None:
        """
        Опубликовать несколько Domain Events

        Args:
            events: Список Domain Events
        """
        for event in events:
            await self.publish(event)

    def _wrap_with_middleware(
        self, middleware: Callable, handler: Callable
    ) -> Callable:
        """
        Обернуть обработчик middleware

        Args:
            middleware: Middleware функция
            handler: Исходный обработчик

        Returns:
            Обернутый обработчик
        """

        async def wrapped_handler(event: DomainEvent):
            return await middleware(event, handler)

        return wrapped_handler

    def get_subscribed_event_types(self) -> List[str]:
        """
        Получить список типов событий с подписками

        Returns:
            Список типов событий
        """
        return list(self._handlers.keys())

    def get_handlers_count(self, event_type: str) -> int:
        """
        Получить количество обработчиков для типа события

        Args:
            event_type: Тип события

        Returns:
            Количество обработчиков
        """
        return len(self._handlers.get(event_type, []))

    def clear_handlers(self, event_type: Optional[str] = None) -> None:
        """
        Очистить обработчики

        Args:
            event_type: Тип события (если None - все обработчики)
        """
        if event_type:
            self._handlers.pop(event_type, None)
            logger.info(f"Cleared handlers for event type: {event_type}")
        else:
            self._handlers.clear()
            logger.info("Cleared all event handlers")

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья Domain Event системы

        Returns:
            Информация о здоровье системы
        """
        return {
            "status": "healthy",
            "subscribed_event_types": len(self._handlers),
            "total_handlers": sum(
                len(handlers) for handlers in self._handlers.values()
            ),
            "middleware_count": len(self._middleware),
            "is_processing": self._is_processing,
        }


# Глобальный экземпляр Domain Event Publisher
domain_event_publisher = DomainEventPublisher()


# Декоратор для подписки на события
def subscribe_to(event_type: str):
    """
    Декоратор для автоматической подписки обработчика на событие

    Args:
        event_type: Тип события для подписки

    Returns:
        Декоратор
    """

    def decorator(handler: Callable):
        domain_event_publisher.subscribe(event_type, handler)
        return handler

    return decorator


# Вспомогательные функции для работы с Domain Events
async def publish_domain_event(event: DomainEvent) -> None:
    """
    Опубликовать Domain Event через глобальный publisher

    Args:
        event: Domain Event для публикации
    """
    await domain_event_publisher.publish(event)


async def publish_domain_events(events: List[DomainEvent]) -> None:
    """
    Опубликовать несколько Domain Events через глобальный publisher

    Args:
        events: Список Domain Events
    """
    await domain_event_publisher.publish_events(events)
