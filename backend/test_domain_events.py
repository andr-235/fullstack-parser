#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Domain Events системы
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.v1.infrastructure.events.domain_event_publisher import (
    DomainEventPublisher,
    domain_event_publisher,
    subscribe_to,
)


class TestEventHandler:
    """Тестовый обработчик событий"""

    def __init__(self):
        self.received_events = []

    async def handle_user_event(self, event):
        """Обработчик событий пользователей"""
        print(f"📧 ПОЛУЧЕНО СОБЫТИЕ ПОЛЬЗОВАТЕЛЯ: {event.event_type}")
        print(f"   ID: {event.aggregate_id}")
        print(f"   Данные: {event.to_dict()}")
        self.received_events.append(event)
        await asyncio.sleep(0.01)  # Имитация асинхронной обработки

    async def handle_settings_event(self, event):
        """Обработчик событий настроек"""
        print(f"⚙️ ПОЛУЧЕНО СОБЫТИЕ НАСТРОЕК: {event.event_type}")
        print(f"   Секция: {getattr(event, 'section', 'N/A')}")
        print(f"   Данные: {event.to_dict()}")
        self.received_events.append(event)
        await asyncio.sleep(0.01)

    async def handle_vk_api_event(self, event):
        """Обработчик событий VK API"""
        print(f"🔗 ПОЛУЧЕНО СОБЫТИЕ VK API: {event.event_type}")
        print(f"   Тип данных: {getattr(event, 'data_type', 'N/A')}")
        print(f"   Данные: {event.to_dict()}")
        self.received_events.append(event)
        await asyncio.sleep(0.01)


async def test_domain_events():
    """Основная функция тестирования"""
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ DOMAIN EVENTS СИСТЕМЫ")
    print("=" * 60)

    # Создаем тестовый обработчик
    handler = TestEventHandler()

    # Подписываемся на события
    print("📝 РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ СОБЫТИЙ...")

    # Импортируем события
    try:
        from app.api.v1.infrastructure.events.user_events import (
            UserCreatedEvent,
            UserUpdatedEvent,
            UserDeletedEvent,
            UserAuthenticatedEvent,
        )
        from app.api.v1.infrastructure.events.settings_events import (
            SettingsUpdatedEvent,
            SettingsResetEvent,
        )
        from app.api.v1.infrastructure.events.vk_api_events import (
            VKAPIDataFetchedEvent,
            VKAPITokenValidationEvent,
        )

        # Подписываемся на события пользователей
        domain_event_publisher.subscribe(
            "UserCreatedEvent", handler.handle_user_event
        )
        domain_event_publisher.subscribe(
            "UserUpdatedEvent", handler.handle_user_event
        )
        domain_event_publisher.subscribe(
            "UserDeletedEvent", handler.handle_user_event
        )
        domain_event_publisher.subscribe(
            "UserAuthenticatedEvent", handler.handle_user_event
        )

        # Подписываемся на события настроек
        domain_event_publisher.subscribe(
            "SettingsUpdatedEvent", handler.handle_settings_event
        )
        domain_event_publisher.subscribe(
            "SettingsResetEvent", handler.handle_settings_event
        )

        # Подписываемся на события VK API
        domain_event_publisher.subscribe(
            "VKAPIDataFetchedEvent", handler.handle_vk_api_event
        )
        domain_event_publisher.subscribe(
            "VKAPITokenValidationEvent", handler.handle_vk_api_event
        )

        print("✅ Обработчики зарегистрированы успешно")

    except ImportError as e:
        print(f"❌ ОШИБКА ИМПОРТА: {e}")
        return False

    # Тестируем создание и публикацию событий
    print("\n📤 ТЕСТИРОВАНИЕ СОЗДАНИЯ И ПУБЛИКАЦИИ СОБЫТИЙ...")

    test_events = []

    # Создаем тестовые события пользователей
    user_created = UserCreatedEvent(
        user_id=1,
        email="test@example.com",
        full_name="Test User",
        is_superuser=False,
    )
    test_events.append(("UserCreatedEvent", user_created))

    user_updated = UserUpdatedEvent(
        user_id=1,
        updated_fields=["email", "full_name"],
        old_values={"email": "old@example.com"},
        new_values={"email": "test@example.com"},
        updated_by="admin",
    )
    test_events.append(("UserUpdatedEvent", user_updated))

    user_authenticated = UserAuthenticatedEvent(
        user_id=1,
        email="test@example.com",
        login_method="password",
        ip_address="127.0.0.1",
    )
    test_events.append(("UserAuthenticatedEvent", user_authenticated))

    # Создаем тестовые события настроек
    settings_updated = SettingsUpdatedEvent(
        section="vk_api",
        updated_keys=["access_token", "api_version"],
        old_values={"api_version": "5.130"},
        new_values={"api_version": "5.131"},
        updated_by="admin",
    )
    test_events.append(("SettingsUpdatedEvent", settings_updated))

    settings_reset = SettingsResetEvent(
        reset_sections=["vk_api", "monitoring"],
        reset_by="admin",
        reason="manual",
    )
    test_events.append(("SettingsResetEvent", settings_reset))

    # Создаем тестовые события VK API
    data_fetched = VKAPIDataFetchedEvent(
        data_type="posts",
        object_id=12345,
        items_count=20,
        total_count=100,
        fetch_time=0.5,
    )
    test_events.append(("VKAPIDataFetchedEvent", data_fetched))

    token_validation = VKAPITokenValidationEvent(
        token_valid=True,
        user_id=123456,
        permissions=["wall", "groups"],
        validation_error=None,
    )
    test_events.append(("VKAPITokenValidationEvent", token_validation))

    # Публикуем события
    print("\n📡 ПУБЛИКАЦИЯ ТЕСТОВЫХ СОБЫТИЙ...")

    for event_name, event in test_events:
        try:
            print(f"\n🔄 Публикуем: {event_name}")
            await domain_event_publisher.publish(event)
            print(f"✅ Событие {event_name} опубликовано успешно")
        except Exception as e:
            print(f"❌ ОШИБКА при публикации {event_name}: {e}")
            return False

    # Проверяем результаты
    print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   Всего событий: {len(test_events)}")
    print(f"   Получено обработчиком: {len(handler.received_events)}")
    print(
        f"   Процент успешности: {(len(handler.received_events) / len(test_events)) * 100:.1f}%"
    )

    # Проверяем здоровье системы
    print("\n🏥 ПРОВЕРКА ЗДОРОВЬЯ DOMAIN EVENTS СИСТЕМЫ...")
    health = await domain_event_publisher.health_check()
    print(f"   Статус: {health.get('status', 'unknown')}")
    print(
        f"   Подписанных типов событий: {health.get('subscribed_event_types', 0)}"
    )
    print(f"   Всего обработчиков: {health.get('total_handlers', 0)}")
    print(f"   Middleware: {health.get('middleware_count', 0)}")
    print(f"   В обработке: {health.get('is_processing', False)}")

    # Проверяем импорты DDD сервисов
    print("\n🔍 ПРОВЕРКА ИМПОРТОВ DDD СЕРВИСОВ...")
    try:
        from app.api.v1.application.user_service import UserService
        from app.api.v1.application.settings_service import SettingsService
        from app.api.v1.application.vk_api_service import VKAPIService
        from app.api.v1.application.comment_service import CommentService
        from app.api.v1.application.group_service import GroupService
        from app.api.v1.application.keyword_service_migration import (
            KeywordService,
        )

        print("✅ Все DDD сервисы импортированы успешно")
        services_ok = True
    except ImportError as e:
        print(f"❌ ОШИБКА импорта DDD сервисов: {e}")
        services_ok = False

    # Финальный отчет
    print("\n" + "=" * 60)
    print("🎯 ФИНАЛЬНЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ:")

    all_tests_passed = (
        len(handler.received_events) == len(test_events)
        and health.get("status") == "healthy"
        and services_ok
    )

    if all_tests_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Domain Events система работает корректно")
        print("✅ DDD сервисы импортируются без ошибок")
        print("✅ Архитектура готова к продакшену")
        return True
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ!")
        print("❌ Требуется дополнительная отладка")
        return False


async def main():
    """Главная функция"""
    try:
        success = await test_domain_events()
        if success:
            print("\n🎉 СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!")
            print("🚀 Можно переходить к удалению старых сервисов")
            return 0
        else:
            print("\n❌ СИСТЕМА ТРЕБУЕТ ДОРАБОТКИ!")
            return 1
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
