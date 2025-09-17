"""
Адаптер для издателя событий
"""

from typing import Any, Dict

from ..interfaces import IEventPublisher


class EventPublisherAdapter(IEventPublisher):
    """Адаптер для существующего издателя событий"""

    def __init__(self, event_publisher: Any):
        self.event_publisher = event_publisher

    async def publish_security_event(self, event_type: str, user_id: str, data: Dict[str, Any]) -> None:
        """Опубликовать событие безопасности"""
        await self.event_publisher.log_security_event(event_type, user_id, data)

    async def publish_user_event(self, event_type: str, user_id: str, data: Dict[str, Any]) -> None:
        """Опубликовать событие пользователя"""
        await self.event_publisher.log_user_event(event_type, user_id, data)

    async def send_email_notification(self, email: str, subject: str, template: str, data: Dict[str, Any]) -> None:
        """Отправить email уведомление"""
        await self.event_publisher.send_email_notification(email, subject, template, data)


class NoOpEventPublisher(IEventPublisher):
    """Заглушка для случаев, когда события не нужны"""

    async def publish_security_event(self, event_type: str, user_id: str, data: Dict[str, Any]) -> None:
        """Не делать ничего"""
        pass

    async def publish_user_event(self, event_type: str, user_id: str, data: Dict[str, Any]) -> None:
        """Не делать ничего"""
        pass

    async def send_email_notification(self, email: str, subject: str, template: str, data: Dict[str, Any]) -> None:
        """Не делать ничего"""
        pass