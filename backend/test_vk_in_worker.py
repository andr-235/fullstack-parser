#!/usr/bin/env python3
"""
Тестовый скрипт для проверки VKBottleService в arq worker
"""

import asyncio

from app.core.config import settings
from app.services.vkbottle_service import VKBottleService


async def test_vk_in_worker():
    """Тестирует VKBottleService в arq worker"""
    print("🔍 Тестирование VKBottleService в arq worker...")
    print(f"Токен из settings: {settings.vk.access_token[:20]}...")

    try:
        vk_service = VKBottleService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

        print("✅ VKBottleService создан успешно")

        # Тестируем получение комментариев
        comments = await vk_service.get_all_post_comments(
            owner_id=-43377172, post_id=126563
        )

        print(f"✅ Получено комментариев: {len(comments)}")

        # Ищем комментарии с "гиви"
        for comment in comments:
            text = comment.get("text", "").lower()
            if "гиви" in text:
                print(
                    f"✅ Найден комментарий с 'гиви': {comment.get('text', '')[:100]}..."
                )
                print(
                    f"   ID: {comment.get('id')}, автор: {comment.get('from_id')}"
                )

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_vk_in_worker())
