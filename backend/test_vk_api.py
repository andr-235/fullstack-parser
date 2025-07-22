#!/usr/bin/env python3
"""
Тестовый скрипт для проверки VKAPIService
"""

import asyncio
from app.services.vk_api_service import VKAPIService
from app.core.config import settings


async def test_vk_api_service():
    """Тестирует VKAPIService"""
    print("🔍 Тестируем VKAPIService...")

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        # Тест 1: Получение информации о группе по ID
        print("\n📋 Тест 1: Получение информации о группе по ID")
        try:
            group_info = await vk_service.get_group_info(1)  # ID группы
            if group_info:
                print(f"✅ Группа найдена: {group_info.get('name', 'N/A')}")
                print(f"   ID: {group_info.get('id', 'N/A')}")
                print(
                    f"   Screen name: {group_info.get('screen_name', 'N/A')}"
                )
            else:
                print("❌ Группа не найдена")
        except Exception as e:
            print(f"❌ Ошибка при получении информации о группе: {e}")

        # Тест 2: Получение информации о группе по screen_name
        print("\n📋 Тест 2: Получение информации о группе по screen_name")
        try:
            group_info = await vk_service.get_group_info(
                "club1"
            )  # Реальный screen_name
            if group_info:
                print(f"✅ Группа найдена: {group_info.get('name', 'N/A')}")
                print(f"   ID: {group_info.get('id', 'N/A')}")
                print(
                    f"   Screen name: {group_info.get('screen_name', 'N/A')}"
                )
            else:
                print("❌ Группа не найдена")
        except Exception as e:
            print(f"❌ Ошибка при получении информации о группе: {e}")

        # Тест 3: Получение постов группы
        print("\n📝 Тест 3: Получение постов группы")
        try:
            posts = await vk_service.get_group_posts(group_id=1, count=5)
            print(f"✅ Получено постов: {len(posts)}")
            if posts:
                print(f"   Первый пост ID: {posts[0].get('id', 'N/A')}")
                print(f"   Дата: {posts[0].get('date', 'N/A')}")
        except Exception as e:
            print(f"❌ Ошибка при получении постов: {e}")

        # Тест 4: Поиск групп
        print("\n🔍 Тест 4: Поиск групп")
        try:
            groups = await vk_service.search_groups(
                "программирование", count=3
            )
            print(f"✅ Найдено групп: {len(groups)}")
            for i, group in enumerate(groups[:3], 1):
                print(
                    f"   {i}. {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})"
                )
        except Exception as e:
            print(f"❌ Ошибка при поиске групп: {e}")


if __name__ == "__main__":
    asyncio.run(test_vk_api_service())
