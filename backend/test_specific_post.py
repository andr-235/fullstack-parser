#!/usr/bin/env python3
"""
Тест для проверки конкретного поста с комментарием "гиви"
"""

import asyncio
from app.services.vk_api_service import VKAPIService
from app.core.config import settings


async def test_specific_post():
    """Тестирует конкретный пост с комментарием 'гиви'"""
    print("🔍 Тестируем конкретный пост с комментарием 'гиви'...")

    # Параметры из URL: https://vk.com/wall-43377172_126563
    group_id = 43377172
    post_id = 126563

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        # Тест 1: Получение информации о группе
        print(f"\n📋 Тест 1: Информация о группе {group_id}")
        try:
            group_info = await vk_service.get_group_info(group_id)
            if group_info:
                print(f"✅ Группа: {group_info.get('name', 'N/A')}")
                print(f"   ID: {group_info.get('id', 'N/A')}")
                print(
                    f"   Screen name: {group_info.get('screen_name', 'N/A')}"
                )
            else:
                print("❌ Группа не найдена")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

        # Тест 2: Получение конкретного поста
        print(f"\n📝 Тест 2: Получение поста {post_id}")
        try:
            posts = await vk_service.get_group_posts(
                group_id=group_id, count=100
            )

            # Ищем конкретный пост
            target_post = None
            for post in posts:
                if post.get("id") == post_id:
                    target_post = post
                    break

            if target_post:
                print(f"✅ Пост найден!")
                print(f"   ID: {target_post.get('id')}")
                print(f"   Дата: {target_post.get('date')}")
                print(f"   Текст: {target_post.get('text', '')[:200]}...")
                print(
                    f"   Комментариев: {target_post.get('comments', {}).get('count', 0)}"
                )
                print(
                    f"   Лайков: {target_post.get('likes', {}).get('count', 0)}"
                )
            else:
                print(f"❌ Пост {post_id} не найден в последних 100 постах")
                print(
                    f"   Доступные посты: {[p.get('id') for p in posts[:10]]}"
                )

        except Exception as e:
            print(f"❌ Ошибка: {e}")

        # Тест 3: Получение комментариев к конкретному посту
        print(f"\n💬 Тест 3: Комментарии к посту {post_id}")
        try:
            comments = await vk_service.get_all_post_comments(
                owner_id=-group_id,  # Отрицательный ID для групп
                post_id=post_id,
            )

            print(f"✅ Получено комментариев: {len(comments)}")

            if comments:
                print(f"\n📋 Первые 5 комментариев:")
                for i, comment in enumerate(comments[:5], 1):
                    print(f"   {i}. ID: {comment.get('id')}")
                    print(f"      Автор: {comment.get('from_id')}")
                    print(f"      Дата: {comment.get('date')}")
                    print(f"      Текст: {comment.get('text', '')[:100]}...")
                    print(
                        f"      Лайков: {comment.get('likes', {}).get('count', 0)}"
                    )
                    print()

                # Поиск комментариев с "гиви"
                keyword = "гиви"
                matching_comments = [
                    c for c in comments if keyword in c.get("text", "").lower()
                ]

                if matching_comments:
                    print(
                        f"🔍 Найдено комментариев с '{keyword}': {len(matching_comments)}"
                    )
                    for i, comment in enumerate(matching_comments, 1):
                        print(f"   {i}. ID: {comment.get('id')}")
                        print(f"      Автор: {comment.get('from_id')}")
                        print(f"      Текст: {comment.get('text', '')}")
                        print()
                else:
                    print(f"❌ Комментариев с '{keyword}' не найдено")
            else:
                print("❌ Комментариев нет")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_specific_post())
