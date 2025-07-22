#!/usr/bin/env python3
"""
Тест для поиска целевого поста в большем количестве постов
"""

import asyncio
from app.services.vk_api_service import VKAPIService
from app.core.config import settings


async def test_find_target_post():
    """Ищет целевой пост в большем количестве постов"""
    print("🔍 Ищем целевой пост в большем количестве постов...")

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        group_id = 43377172  # РИА Биробиджан
        target_post_id = 126563  # Пост с комментарием "гиви"

        # Пробуем разные количества постов
        for count in [50, 100, 150, 200]:
            print(f"\n📋 Получаем первые {count} постов группы {group_id}")
            try:
                posts = await vk_service.get_group_posts(
                    group_id=group_id, count=count
                )
                print(f"✅ Получено постов: {len(posts)}")

                # Ищем целевой пост
                target_post = None
                for post in posts:
                    if post.get("id") == target_post_id:
                        target_post = post
                        break

                if target_post:
                    print(
                        f"✅ Пост {target_post_id} найден в первых {count} постах!"
                    )
                    print(f"   Текст: {target_post.get('text', '')[:100]}...")
                    print(
                        f"   Комментариев: {target_post.get('comments', {}).get('count', 0)}"
                    )

                    # Проверяем комментарии к этому посту
                    print(
                        f"\n💬 Проверяем комментарии к посту {target_post_id}"
                    )
                    try:
                        comments = await vk_service.get_post_comments(
                            owner_id=group_id, post_id=target_post_id, count=10
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

                    break  # Нашли пост, выходим из цикла
                else:
                    print(
                        f"❌ Пост {target_post_id} НЕ найден в первых {count} постах"
                    )
                    print(
                        f"   Диапазон ID постов: {posts[-1].get('id')} - {posts[0].get('id')}"
                    )

            except Exception as e:
                print(f"❌ Ошибка при получении {count} постов: {e}")
                break


if __name__ == "__main__":
    asyncio.run(test_find_target_post())
