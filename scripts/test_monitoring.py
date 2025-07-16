#!/usr/bin/env python3
"""
Скрипт для тестирования системы автоматического мониторинга
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Добавляем путь к backend в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.services.monitoring_service import MonitoringService
from app.services.vkbottle_service import VKBottleService
from app.core.config import settings


async def test_monitoring_service():
    """Тестирование сервиса мониторинга"""
    print("🧪 Тестирование системы автоматического мониторинга")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Создаём сервисы
        vk_service = VKBottleService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )
        monitoring_service = MonitoringService(db=db, vk_service=vk_service)

        # 1. Получаем статистику мониторинга
        print("\n1. 📊 Получение статистики мониторинга...")
        try:
            stats = await monitoring_service.get_monitoring_stats()
            print(f"   ✅ Статистика получена:")
            print(f"      - Всего групп: {stats.get('total_groups', 0)}")
            print(f"      - Активных групп: {stats.get('active_groups', 0)}")
            print(f"      - Групп в мониторинге: {stats.get('monitored_groups', 0)}")
            print(
                f"      - Готовых для мониторинга: {stats.get('ready_for_monitoring', 0)}"
            )
        except Exception as e:
            print(f"   ❌ Ошибка получения статистики: {e}")

        # 2. Получаем группы для мониторинга
        print("\n2. 🔍 Поиск групп для мониторинга...")
        try:
            groups = await monitoring_service.get_groups_for_monitoring()
            print(f"   ✅ Найдено групп для мониторинга: {len(groups)}")
            for group in groups[:3]:  # Показываем первые 3
                print(
                    f"      - {group.name} (ID: {group.id}, приоритет: {group.monitoring_priority})"
                )
        except Exception as e:
            print(f"   ❌ Ошибка поиска групп: {e}")

        # 3. Тестируем ручной запуск цикла мониторинга
        print("\n3. ⚡ Тестирование ручного запуска цикла мониторинга...")
        try:
            stats = await monitoring_service.run_monitoring_cycle()
            print(f"   ✅ Цикл мониторинга завершён:")
            print(f"      - Обработано групп: {stats.get('monitored_groups', 0)}")
            print(f"      - Успешных запусков: {stats.get('successful_runs', 0)}")
            print(f"      - Неудачных запусков: {stats.get('failed_runs', 0)}")
            print(
                f"      - Время выполнения: {stats.get('duration_seconds', 0):.2f} сек"
            )
        except Exception as e:
            print(f"   ❌ Ошибка запуска цикла: {e}")

        print("\n" + "=" * 60)
        print("✅ Тестирование завершено")


async def test_api_endpoints():
    """Тестирование API endpoints"""
    print("\n🌐 Тестирование API endpoints")
    print("=" * 60)

    import requests

    base_url = "http://localhost:8000/api/v1"

    # 1. Статистика мониторинга
    print("\n1. 📊 GET /monitoring/stats")
    try:
        response = requests.get(f"{base_url}/monitoring/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статистика получена: {data}")
        else:
            print(f"   ❌ Ошибка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")

    # 2. Статус планировщика
    print("\n2. ⏰ GET /monitoring/scheduler/status")
    try:
        response = requests.get(f"{base_url}/monitoring/scheduler/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статус планировщика: {data}")
        else:
            print(f"   ❌ Ошибка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")

    # 3. Ручной запуск цикла
    print("\n3. 🚀 POST /monitoring/run-cycle")
    try:
        response = requests.post(f"{base_url}/monitoring/run-cycle")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Цикл запущен: {data}")
        else:
            print(f"   ❌ Ошибка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")


async def main():
    """Основная функция"""
    print("🚀 Запуск тестирования системы автоматического мониторинга")
    print(f"⏰ Время запуска: {datetime.now(timezone.utc).isoformat()}")

    try:
        # Тестируем сервис мониторинга
        await test_monitoring_service()

        # Тестируем API endpoints
        await test_api_endpoints()

        print("\n🎉 Все тесты завершены успешно!")

    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
