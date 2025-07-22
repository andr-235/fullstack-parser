#!/usr/bin/env python3
"""
Тест для отладки owner_id
"""

import asyncio

from app.core.config import settings
from app.services.vk_api_service import VKAPIService


async def test_debug_owner_id():
    """Тестирует отладку owner_id"""
    print("🔍 Тестируем отладку owner_id...")

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        group_id = 43377172  # РИА Биробиджан
        post_id = 126563  # Пост с комментарием "гиви"

        print(
            "\n📋 Тест 1: Прямой вызов get_post_comments с положительным owner_id"
        )
        try:
            comments = await vk_service.get_post_comments(
                owner_id=group_id,  # Положительный ID
                post_id=post_id,
                count=10,
            )
            print(f"✅ Получено комментариев: {len(comments)}")
            for i, comment in enumerate(comments, 1):
                print(
                    f"   {i}. ID: {comment.get('id')}, Текст: {comment.get('text', '')[:50]}..."
                )
        except Exception as e:
            print(f"❌ Ошибка: {e}")

        print(
            "\n📋 Тест 2: Прямой вызов get_post_comments с отрицательным owner_id"
        )
        try:
            comments = await vk_service.get_post_comments(
                owner_id=-group_id,  # Отрицательный ID
                post_id=post_id,
                count=10,
            )
            print(f"✅ Получено комментариев: {len(comments)}")
            for i, comment in enumerate(comments, 1):
                print(
                    f"   {i}. ID: {comment.get('id')}, Текст: {comment.get('text', '')[:50]}..."
                )
        except Exception as e:
            print(f"❌ Ошибка: {e}")

        print(
            "\n📋 Тест 3: Прямой вызов get_all_post_comments с положительным owner_id"
        )
        try:
            comments = await vk_service.get_all_post_comments(
                owner_id=group_id, post_id=post_id  # Положительный ID
            )
            print(f"✅ Получено комментариев: {len(comments)}")
            for i, comment in enumerate(comments, 1):
                print(
                    f"   {i}. ID: {comment.get('id')}, Текст: {comment.get('text', '')[:50]}..."
                )
        except Exception as e:
            print(f"❌ Ошибка: {e}")

        print(
            "\n📋 Тест 4: Прямой вызов get_all_post_comments с отрицательным owner_id"
        )
        try:
            comments = await vk_service.get_all_post_comments(
                owner_id=-group_id, post_id=post_id  # Отрицательный ID
            )
            print(f"✅ Получено комментариев: {len(comments)}")
            for i, comment in enumerate(comments, 1):
                print(
                    f"   {i}. ID: {comment.get('id')}, Текст: {comment.get('text', '')[:50]}..."
                )
        except Exception as e:
            print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(test_debug_owner_id())
