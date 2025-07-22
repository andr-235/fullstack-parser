#!/usr/bin/env python3
"""
Тест для получения комментариев с большими задержками
"""

import asyncio
from app.services.vk_api_service import VKAPIService
from app.core.config import settings


async def test_comments_with_delays():
    """Тестирует получение комментариев с большими задержками"""
    print("🔍 Тестируем получение комментариев с большими задержками...")

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        group_id = 43377172  # РИА Биробиджан
        target_post_id = 126563  # Пост с комментарием "гиви"

        print(f"\n📋 Получаем первые 10 постов с комментариями")
        try:
            posts = await vk_service.get_group_posts(
                group_id=group_id, count=10
            )
            print(f"✅ Получено постов: {len(posts)}")

            # Фильтруем посты с комментариями
            posts_with_comments = []
            for post in posts:
                comments_count = post.get("comments", {}).get("count", 0)
                if comments_count > 0:
                    posts_with_comments.append(post)

            print(f"📝 Постов с комментариями: {len(posts_with_comments)}")

            # Обрабатываем каждый пост с комментариями отдельно
            for i, post in enumerate(posts_with_comments, 1):
                post_id = post.get("id")
                comments_count = post.get("comments", {}).get("count", 0)

                print(
                    f"\n{i}. Обрабатываем пост {post_id} ({comments_count} комментариев)"
                )
                print(f"   Текст: {post.get('text', '')[:100]}...")

                try:
                    # Большая задержка перед запросом комментариев
                    await asyncio.sleep(2)

                    comments = await vk_service.get_post_comments(
                        owner_id=group_id,
                        post_id=post_id,
                        count=min(comments_count, 10),
                    )

                    print(f"   ✅ Получено комментариев: {len(comments)}")

                    # Ищем комментарии с "гиви"
                    for j, comment in enumerate(comments, 1):
                        text = comment.get("text", "").lower()
                        if "гиви" in text:
                            print(f"   🔍 НАЙДЕН КОММЕНТАРИЙ С 'ГИВИ'!")
                            print(f"      ID: {comment.get('id')}")
                            print(f"      Автор: {comment.get('from_id')}")
                            print(f"      Текст: {comment.get('text', '')}")
                            print(f"      Дата: {comment.get('date')}")
                        else:
                            print(
                                f"   {j}. ID: {comment.get('id')}, Текст: {comment.get('text', '')[:50]}..."
                            )

                except Exception as e:
                    print(f"   ❌ Ошибка при получении комментариев: {e}")

                # Задержка между постами
                if i < len(posts_with_comments):
                    print("   ⏳ Ждем 3 секунды перед следующим постом...")
                    await asyncio.sleep(3)

            # Теперь попробуем получить комментарии к целевому посту
            print(f"\n🎯 Проверяем целевой пост {target_post_id}")
            try:
                await asyncio.sleep(5)  # Большая задержка

                comments = await vk_service.get_post_comments(
                    owner_id=group_id, post_id=target_post_id, count=10
                )

                print(
                    f"✅ Получено комментариев к целевому посту: {len(comments)}"
                )

                for i, comment in enumerate(comments, 1):
                    print(f"   {i}. ID: {comment.get('id')}")
                    print(f"      Автор: {comment.get('from_id')}")
                    print(f"      Текст: {comment.get('text', '')}")
                    print(f"      Дата: {comment.get('date')}")
                    print()

            except Exception as e:
                print(
                    f"❌ Ошибка при получении комментариев к целевому посту: {e}"
                )

        except Exception as e:
            print(f"❌ Ошибка при получении постов: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_comments_with_delays())
