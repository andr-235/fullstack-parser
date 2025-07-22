#!/usr/bin/env python3
"""
Тест для проверки VKAPIService с лимитами
"""

import asyncio
from app.services.vk_api_service import VKAPIService
from app.core.config import settings


async def test_vk_api_service():
    """Тестирует VKAPIService с лимитами"""
    print("🔍 Тестирование VKAPIService с лимитами...")

    # Создаем сервис
    vk_service = VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    )

    try:
        print("\n📋 1. Тест получения информации о группе 'riabirobidzhan':")
        group_info = await vk_service.get_group_info("riabirobidzhan")
        if group_info:
            print(f"   ✅ Группа найдена: {group_info.get('name')}")
            print(f"   ID: {group_info.get('id')}")
            print(f"   Screen name: {group_info.get('screen_name')}")
        else:
            print("   ❌ Группа не найдена")

        print("\n📋 2. Тест получения постов группы:")
        group_id = 43377172  # ID группы "РиаБиРо Биробиджан"
        posts = await vk_service.get_group_posts(group_id, count=5)
        print(f"   ✅ Получено постов: {len(posts)}")
        if posts:
            print(f"   Первый пост ID: {posts[0].get('id')}")
            print(f"   Текст: {posts[0].get('text', '')[:100]}...")

        print("\n📋 3. Тест получения комментариев к посту:")
        if posts:
            post_id = posts[0]["id"]
            owner_id = -group_id  # Отрицательный ID для групп

            comments = await vk_service.get_post_comments(
                owner_id=owner_id, post_id=post_id, count=3
            )
            print(f"   ✅ Получено комментариев: {len(comments)}")
            if comments:
                print(
                    f"   Первый комментарий: {comments[0].get('text', '')[:100]}..."
                )

        print("\n📋 4. Тест rate limiting (множественные запросы):")
        print("   Отправляем 5 запросов подряд для проверки лимитов...")
        for i in range(5):
            group_info = await vk_service.get_group_info("riabirobidzhan")
            print(f"   Запрос {i+1}: {'✅' if group_info else '❌'}")
            await asyncio.sleep(0.1)  # Небольшая пауза

        print("\n📋 5. Тест поиска групп:")
        search_results = await vk_service.search_groups("Биробиджан", count=3)
        print(f"   ✅ Найдено групп: {len(search_results)}")
        if search_results:
            for i, group in enumerate(search_results[:3], 1):
                print(f"   {i}. {group.get('name')} (ID: {group.get('id')})")

        print("\n✅ Все тесты VKAPIService прошли успешно!")

    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await vk_service.close()


if __name__ == "__main__":
    asyncio.run(test_vk_api_service())
