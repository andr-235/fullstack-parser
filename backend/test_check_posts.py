#!/usr/bin/env python3
"""
Тест для проверки содержимого постов в группе
"""

import asyncio
from app.services.vk_api_service import VKAPIService
from app.core.config import settings


async def test_check_posts():
    """Проверяет содержимое постов в группе"""
    print("🔍 Проверяем содержимое постов в группе...")

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        group_id = 43377172  # РИА Биробиджан
        target_post_id = 126563  # Пост с комментарием "гиви"

        print(f"\n📋 Получаем первые 20 постов группы {group_id}")
        try:
            posts = await vk_service.get_group_posts(
                group_id=group_id, count=20
            )
            print(f"✅ Получено постов: {len(posts)}")

            # Ищем целевой пост
            target_post = None
            for i, post in enumerate(posts, 1):
                post_id = post.get("id")
                comments_count = post.get("comments", {}).get("count", 0)
                print(
                    f"{i:2d}. Пост ID: {post_id}, Комментариев: {comments_count}"
                )

                if post_id == target_post_id:
                    target_post = post
                    print(f"    ⭐ НАЙДЕН ЦЕЛЕВОЙ ПОСТ!")
                    print(f"    Текст: {post.get('text', '')[:100]}...")

            if target_post:
                print(
                    f"\n✅ Пост {target_post_id} найден в первых {len(posts)} постах!"
                )

                # Проверяем комментарии к этому посту
                print(f"\n💬 Проверяем комментарии к посту {target_post_id}")
                try:
                    comments = await vk_service.get_post_comments(
                        owner_id=group_id,  # Будет автоматически преобразован в отрицательный
                        post_id=target_post_id,
                        count=10,
                    )
                    print(f"✅ Получено комментариев: {len(comments)}")

                    for i, comment in enumerate(comments, 1):
                        print(f"   {i}. ID: {comment.get('id')}")
                        print(f"      Автор: {comment.get('from_id')}")
                        print(
                            f"      Текст: {comment.get('text', '')[:50]}..."
                        )
                        print(f"      Дата: {comment.get('date')}")
                        print()

                except Exception as e:
                    print(f"❌ Ошибка при получении комментариев: {e}")
            else:
                print(
                    f"\n❌ Пост {target_post_id} НЕ найден в первых {len(posts)} постах"
                )
                print(
                    f"   Диапазон ID постов: {posts[-1].get('id')} - {posts[0].get('id')}"
                )

        except Exception as e:
            print(f"❌ Ошибка при получении постов: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_check_posts())
