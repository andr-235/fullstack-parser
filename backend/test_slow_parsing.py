#!/usr/bin/env python3
"""
Тест для медленного парсинга с большими задержками
"""

import asyncio

from app.core.config import settings
from app.services.vk_api_service import VKAPIService


async def test_slow_parsing():
    """Тестирует медленный парсинг с большими задержками"""
    print("🔍 Тестируем медленный парсинг с большими задержками...")

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        group_id = 43377172  # РИА Биробиджан
        target_post_id = 126563  # Пост с комментарием "гиви"

        print("\n📋 Получаем первые 20 постов")
        try:
            posts = await vk_service.get_group_posts(
                group_id=group_id, count=20
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
                    # Очень большая задержка перед запросом комментариев
                    print("   ⏳ Ждем 5 секунд перед запросом комментариев...")
                    await asyncio.sleep(5)

                    comments = await vk_service.get_all_post_comments(
                        owner_id=group_id, post_id=post_id
                    )

                    print(f"   ✅ Получено комментариев: {len(comments)}")

                    # Ищем комментарии с "гиви"
                    found_givi = False
                    for j, comment in enumerate(comments, 1):
                        text = comment.get("text", "").lower()
                        if "гиви" in text:
                            print("   🔍 НАЙДЕН КОММЕНТАРИЙ С 'ГИВИ'!")
                            print(f"      ID: {comment.get('id')}")
                            print(f"      Автор: {comment.get('from_id')}")
                            print(f"      Текст: {comment.get('text', '')}")
                            print(f"      Дата: {comment.get('date')}")
                            found_givi = True
                        else:
                            print(
                                f"   {j}. ID: {comment.get('id')}, Текст: {comment.get('text', '')[:50]}..."
                            )

                    if found_givi:
                        print(
                            f"   🎉 УСПЕХ! Найден комментарий с 'гиви' в посте {post_id}"
                        )

                except Exception as e:
                    print(f"   ❌ Ошибка при получении комментариев: {e}")

                # Задержка между постами
                if i < len(posts_with_comments):
                    print("   ⏳ Ждем 10 секунд перед следующим постом...")
                    await asyncio.sleep(10)

            # Проверяем, есть ли целевой пост в списке
            target_found = False
            for post in posts_with_comments:
                if post.get("id") == target_post_id:
                    target_found = True
                    break

            if not target_found:
                print(
                    f"\n🎯 Целевой пост {target_post_id} не найден в первых 20 постах"
                )
                print("   Попробуем получить больше постов...")

                # Получаем больше постов
                more_posts = await vk_service.get_group_posts(
                    group_id=group_id, count=50
                )
                print(f"✅ Получено постов: {len(more_posts)}")

                # Ищем целевой пост
                for post in more_posts:
                    if post.get("id") == target_post_id:
                        comments_count = post.get("comments", {}).get(
                            "count", 0
                        )
                        print(
                            f"🎯 Найден целевой пост {target_post_id} с {comments_count} комментариями"
                        )

                        if comments_count > 0:
                            print(
                                "   ⏳ Ждем 5 секунд перед запросом комментариев..."
                            )
                            await asyncio.sleep(5)

                            try:
                                comments = (
                                    await vk_service.get_all_post_comments(
                                        owner_id=group_id,
                                        post_id=target_post_id,
                                    )
                                )

                                print(
                                    f"   ✅ Получено комментариев: {len(comments)}"
                                )

                                for i, comment in enumerate(comments, 1):
                                    text = comment.get("text", "").lower()
                                    if "гиви" in text:
                                        print(
                                            "   🔍 НАЙДЕН КОММЕНТАРИЙ С 'ГИВИ'!"
                                        )
                                        print(f"      ID: {comment.get('id')}")
                                        print(
                                            f"      Автор: {comment.get('from_id')}"
                                        )
                                        print(
                                            f"      Текст: {comment.get('text', '')}"
                                        )
                                        print(
                                            f"      Дата: {comment.get('date')}"
                                        )
                                    else:
                                        print(
                                            f"   {i}. ID: {comment.get('id')}, Текст: {comment.get('text', '')[:50]}..."
                                        )

                            except Exception as e:
                                print(
                                    f"   ❌ Ошибка при получении комментариев: {e}"
                                )

                        break

        except Exception as e:
            print(f"❌ Ошибка при получении постов: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_slow_parsing())
