#!/usr/bin/env python3
"""
Упрощенный тестовый скрипт для проверки Domain Events системы
Без зависимостей от FastAPI и других внешних библиотек
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем только необходимые компоненты Domain Events
try:
    from app.api.v1.infrastructure.events.domain_event_publisher import (
        DomainEvent,
        DomainEventPublisher,
        domain_event_publisher,
    )

    print("✅ Domain Events инфраструктура импортирована успешно")
except ImportError as e:
    print(f"❌ ОШИБКА импорта Domain Events: {e}")
    sys.exit(1)


class TestEventHandler:
    """Тестовый обработчик событий"""

    def __init__(self):
        self.received_events = []

    async def handle_event(self, event):
        """Обработчик всех событий"""
        print(f"📧 ПОЛУЧЕНО СОБЫТИЕ: {event.event_type}")
        print(f"   ID: {event.aggregate_id}")
        print(f"   Время: {event.occurred_at}")
        self.received_events.append(event)
        await asyncio.sleep(0.001)  # Имитация обработки


class TestEvent(DomainEvent):
    """Тестовое событие"""

    def __init__(self, event_id: int, message: str):
        super().__init__(event_id)
        self.message = message

    def _get_event_data(self) -> Dict[str, Any]:
        return {"message": self.message}


async def test_basic_functionality():
    """Тестирование базовой функциональности"""
    print("\n🔧 ТЕСТИРОВАНИЕ БАЗОВОЙ ФУНКЦИОНАЛЬНОСТИ...")

    # Создаем тестовый обработчик
    handler = TestEventHandler()

    # Подписываемся на событие
    domain_event_publisher.subscribe("TestEvent", handler.handle_event)
    print("✅ Обработчик подписан на TestEvent")

    # Создаем и публикуем тестовое событие
    test_event = TestEvent(event_id=123, message="Тестовое сообщение")
    print("📤 Публикуем тестовое событие...")

    await domain_event_publisher.publish(test_event)

    # Проверяем результат
    if len(handler.received_events) == 1:
        print("✅ Событие успешно обработано!")
        return True
    else:
        print(
            f"❌ Ожидалось 1 событие, получено {len(handler.received_events)}"
        )
        return False


async def test_multiple_events():
    """Тестирование множественных событий"""
    print("\n🔄 ТЕСТИРОВАНИЕ МНОЖЕСТВЕННЫХ СОБЫТИЙ...")

    handler = TestEventHandler()

    # Подписываемся на разные типы событий
    domain_event_publisher.subscribe("Event1", handler.handle_event)
    domain_event_publisher.subscribe("Event2", handler.handle_event)

    # Создаем несколько событий
    events = [
        TestEvent(1, "Сообщение 1"),
        TestEvent(2, "Сообщение 2"),
        TestEvent(3, "Сообщение 3"),
    ]

    # Меняем типы событий для тестирования
    events[0].__class__.__name__ = "Event1"
    events[1].__class__.__name__ = "Event2"
    events[2].__class__.__name__ = "Event1"

    # Публикуем события
    for event in events:
        await domain_event_publisher.publish(event)

    # Проверяем результаты
    expected_count = 3
    actual_count = len(handler.received_events)

    if actual_count == expected_count:
        print(f"✅ Все {expected_count} события обработаны!")
        return True
    else:
        print(
            f"❌ Ожидалось {expected_count} событий, получено {actual_count}"
        )
        return False


async def test_health_check():
    """Тестирование проверки здоровья системы"""
    print("\n🏥 ТЕСТИРОВАНИЕ ЗДОРОВЬЯ СИСТЕМЫ...")

    try:
        health = await domain_event_publisher.health_check()
        print("✅ Проверка здоровья выполнена успешно")
        print(f"   Статус: {health.get('status', 'unknown')}")
        print(
            f"   Подписанных типов: {health.get('subscribed_event_types', 0)}"
        )
        print(f"   Всего обработчиков: {health.get('total_handlers', 0)}")

        if health.get("status") == "healthy":
            print("✅ Система в здоровом состоянии!")
            return True
        else:
            print("❌ Система в нездоровом состоянии!")
            return False
    except Exception as e:
        print(f"❌ ОШИБКА при проверке здоровья: {e}")
        return False


async def test_event_serialization():
    """Тестирование сериализации событий"""
    print("\n📦 ТЕСТИРОВАНИЕ СЕРИАЛИЗАЦИИ СОБЫТИЙ...")

    try:
        # Создаем событие
        original_event = TestEvent(999, "Тест сериализации")

        # Сериализуем
        event_dict = original_event.to_dict()
        print("✅ Событие сериализовано успешно")

        # Имитируем десериализацию
        restored_event = TestEvent.from_dict(event_dict)
        print("✅ Событие десериализовано успешно")

        # Проверяем данные
        if (
            restored_event.aggregate_id == original_event.aggregate_id
            and restored_event.message == original_event.message
        ):
            print("✅ Данные события совпадают!")
            return True
        else:
            print("❌ Данные события не совпадают!")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА при сериализации: {e}")
        return False


async def test_imports():
    """Тестирование импортов Domain Events"""
    print("\n📚 ТЕСТИРОВАНИЕ ИМПОРТОВ DOMAIN EVENTS...")

    import_tests = [
        ("User Events", "app.api.v1.infrastructure.events.user_events"),
        (
            "Settings Events",
            "app.api.v1.infrastructure.events.settings_events",
        ),
        ("VK API Events", "app.api.v1.infrastructure.events.vk_api_events"),
        ("Comment Events", "app.api.v1.infrastructure.events.comment_events"),
    ]

    success_count = 0

    for test_name, module_path in import_tests:
        try:
            module = __import__(module_path, fromlist=[""])
            print(f"✅ {test_name} импортированы успешно")
            success_count += 1
        except ImportError as e:
            print(f"❌ ОШИБКА импорта {test_name}: {e}")
        except Exception as e:
            print(f"⚠️ ПРОБЛЕМА с {test_name}: {e}")

    if success_count == len(import_tests):
        print("✅ Все импорты Domain Events успешны!")
        return True
    else:
        print(f"❌ {len(import_tests) - success_count} импортов неудачных")
        return False


async def main():
    """Главная функция тестирования"""
    print("🚀 ЗАПУСК УПРОЩЕННОГО ТЕСТИРОВАНИЯ DOMAIN EVENTS")
    print("=" * 60)

    tests = [
        ("Базовая функциональность", test_basic_functionality),
        ("Множественные события", test_multiple_events),
        ("Здоровье системы", test_health_check),
        ("Сериализация событий", test_event_serialization),
        ("Импорты Domain Events", test_imports),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*10} {test_name.upper()} {'='*10}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 КРИТИЧЕСКАЯ ОШИБКА в {test_name}: {e}")
            results.append((test_name, False))

    # Финальный отчет
    print("\n" + "=" * 60)
    print("🎯 ФИНАЛЬНЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ:")

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛИЛ"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n📊 ИТОГО:")
    print(f"   Прошло: {passed}")
    print(f"   Провалило: {failed}")
    print(f"   Успешность: {(passed / (passed + failed) * 100):.1f}%")
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Domain Events система работает корректно!")
        print("🚀 ГОТОВ К ПРОДАКШЕНУ!")
        return 0
    else:
        print(f"\n❌ {failed} ТЕСТОВ ПРОВАЛИЛИСЬ!")
        print("⚠️ Требуется дополнительная отладка")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ ТЕСТИРОВАНИЕ ПРЕРВАНО ПОЛЬЗОВАТЕЛЕМ")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
