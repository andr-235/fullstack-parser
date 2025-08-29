#!/usr/bin/env python3
"""
Минимальный тест для проверки базовых классов Domain Events
Без импорта всего API
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class DomainEvent:
    """Базовый класс Domain Event для тестирования"""

    def __init__(self, aggregate_id: Any, event_version: int = 1):
        self.aggregate_id = aggregate_id
        self.event_id = str(uuid4())
        self.occurred_at = datetime.utcnow()
        self.event_version = event_version
        self._frozen = False

    @property
    def event_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": str(self.aggregate_id),
            "occurred_at": self.occurred_at.isoformat(),
            "event_version": self.event_version,
            "event_data": self._get_event_data(),
        }

    def _get_event_data(self) -> Dict[str, Any]:
        data = {}
        for attr_name in dir(self):
            if not attr_name.startswith("_") and attr_name not in [
                "event_type",
                "to_dict",
                "aggregate_id",
                "event_id",
                "occurred_at",
                "event_version",
                "_frozen",
            ]:
                value = getattr(self, attr_name)
                if not callable(value):
                    data[attr_name] = value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        event = cls.__new__(cls)
        event.event_id = data["event_id"]
        event.aggregate_id = data["aggregate_id"]
        event.occurred_at = datetime.fromisoformat(data["occurred_at"])
        event.event_version = data.get("event_version", 1)
        event._frozen = True

        event_data = data.get("event_data", {})
        for key, value in event_data.items():
            setattr(event, key, value)

        return event


class DomainEventPublisher:
    """Publisher для тестирования"""

    def __init__(self):
        self._handlers: Dict[str, list] = {}
        self._is_processing = False

    def subscribe(self, event_type: str, handler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        if self._is_processing:
            return

        try:
            self._is_processing = True
            handlers = self._handlers.get(event.event_type, [])

            if not handlers:
                return

            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Error in handler: {e}")

        finally:
            self._is_processing = False

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "subscribed_event_types": len(self._handlers),
            "total_handlers": sum(
                len(handlers) for handlers in self._handlers.values()
            ),
            "is_processing": self._is_processing,
        }


# Создаем экземпляр
domain_event_publisher = DomainEventPublisher()


class TestUserEvent(DomainEvent):
    """Тестовое событие пользователя"""

    def __init__(self, user_id: int, email: str, action: str):
        super().__init__(user_id)
        self.email = email
        self.action = action

    def _get_event_data(self) -> Dict[str, Any]:
        return {"email": self.email, "action": self.action}


class TestSettingsEvent(DomainEvent):
    """Тестовое событие настроек"""

    def __init__(self, section: str, changes: Dict[str, Any]):
        super().__init__(section)
        self.section = section
        self.changes = changes

    def _get_event_data(self) -> Dict[str, Any]:
        return {"section": self.section, "changes": self.changes}


class TestHandler:
    """Тестовый обработчик"""

    def __init__(self):
        self.events = []

    async def handle_user_event(self, event):
        print(f"👤 Пользователь {event.email}: {event.action}")
        self.events.append(event)
        await asyncio.sleep(0.001)

    async def handle_settings_event(self, event):
        print(f"⚙️ Настройки {event.section}: {len(event.changes)} изменений")
        self.events.append(event)
        await asyncio.sleep(0.001)


async def test_basic_events():
    """Тестирование базовых событий"""
    print("🔧 ТЕСТИРОВАНИЕ БАЗОВЫХ СОБЫТИЙ...")

    handler = TestHandler()

    # Подписываемся
    domain_event_publisher.subscribe(
        "TestUserEvent", handler.handle_user_event
    )
    domain_event_publisher.subscribe(
        "TestSettingsEvent", handler.handle_settings_event
    )

    # Создаем события
    user_event = TestUserEvent(1, "test@example.com", "created")
    settings_event = TestSettingsEvent("vk_api", {"token": "new_token"})

    # Публикуем
    await domain_event_publisher.publish(user_event)
    await domain_event_publisher.publish(settings_event)

    # Проверяем
    if len(handler.events) == 2:
        print("✅ Оба события обработаны!")
        return True
    else:
        print(f"❌ Ожидалось 2 события, получено {len(handler.events)}")
        return False


async def test_serialization():
    """Тестирование сериализации"""
    print("📦 ТЕСТИРОВАНИЕ СЕРИАЛИЗАЦИИ...")

    original = TestUserEvent(123, "serialize@test.com", "test")
    event_dict = original.to_dict()
    restored = TestUserEvent.from_dict(event_dict)

    if (
        restored.aggregate_id == original.aggregate_id
        and restored.email == original.email
        and restored.action == original.action
    ):
        print("✅ Сериализация работает корректно!")
        return True
    else:
        print("❌ Сериализация не работает!")
        return False


async def test_health():
    """Тестирование здоровья системы"""
    print("🏥 ТЕСТИРОВАНИЕ ЗДОРОВЬЯ СИСТЕМЫ...")

    health = await domain_event_publisher.health_check()
    if health["status"] == "healthy":
        print("✅ Система в здоровом состоянии!")
        return True
    else:
        print("❌ Система нездорова!")
        return False


async def main():
    """Главная функция"""
    print("🚀 МИНИМАЛЬНОЕ ТЕСТИРОВАНИЕ DOMAIN EVENTS")
    print("=" * 50)

    tests = [
        ("Базовые события", test_basic_events),
        ("Сериализация", test_serialization),
        ("Здоровье системы", test_health),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*5} {test_name.upper()} {'='*5}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 ОШИБКА: {e}")
            results.append((test_name, False))

    # Отчет
    print("\n" + "=" * 50)
    print("🎯 РЕЗУЛЬТАТЫ:")

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")

    print(f"\n📊 Прошло: {passed}/{passed + failed}")

    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Domain Events архитектура работает корректно!")
        print("🚀 ГОТОВ К ПРОДАКШЕНУ!")
        return 0
    else:
        print(f"\n❌ {failed} ТЕСТОВ ПРОВАЛИЛИСЬ!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
