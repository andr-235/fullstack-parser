#!/usr/bin/env python3
"""
Тест для парсинга комментариев в группе РиаБиРо Биробиджан
"""

import asyncio

from app.core.config import settings
from app.services.vk_api_service import VKAPIService


async def test_riabirobidzhan():
    """Тестирует парсинг комментариев в группе РиаБиРо Биробиджан"""
    print("🔍 Тестируем парсинг комментариев в группе РиаБиРо Биробиджан...")

    # ID группы из URL: https://vk.com/riabirobidzhan
    # Из URL видно, что это группа с ID 43377172
    group_id = 43377172

    # ID поста из URL: https://vk.com/wall-43377172_126563
    # Формат: wall-{group_id}_{post_id}
    post_id = 126563

    async with VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    ) as vk_service:

        # Тест 1: Получение информации о группе
        print(f"\n📋 Тест 1: Получение информации о группе {group_id}")
        try:
            group_info = await vk_service.get_group_info(group_id)
            if group_info:
                print(f"✅ Группа найдена: {group_info.get('name', 'N/A')}")
                print(f"   ID: {group_info.get('id', 'N/A')}")
                print(
                    f"   Screen name: {group_info.get('screen_name', 'N/A')}"
                )
                print(f"   Тип: {group_info.get('type', 'N/A')}")
            else:
                print("❌ Группа не найдена")
        except Exception as e:
            print(f"❌ Ошибка при получении информации о группе: {e}")

        # Тест 2: Получение постов группы
        print(f"\n📝 Тест 2: Получение постов группы {group_id}")
        try:
            posts = await vk_service.get_group_posts(
                group_id=group_id, count=10
            )
            print(f"✅ Получено постов: {len(posts)}")
            if posts:
                print(f"   Последний пост ID: {posts[0].get('id', 'N/A')}")
                print(f"   Дата: {posts[0].get('date', 'N/A')}")
                print(f"   Текст: {posts[0].get('text', 'N/A')[:100]}...")
        except Exception as e:
            print(f"❌ Ошибка при получении постов: {e}")

        # Тест 3: Получение комментариев к конкретному посту
        print(f"\n💬 Тест 3: Получение комментариев к посту {post_id}")
        try:
            comments = await vk_service.get_post_comments(
                owner_id=-group_id,  # Отрицательный ID для групп
                post_id=post_id,
                count=50,
            )
            print(f"✅ Получено комментариев: {len(comments)}")

            # Ищем комментарии с ключевым словом "гиви"
            keyword = "гиви"
            matching_comments = []

            for comment in comments:
                text = comment.get("text", "").lower()
                if keyword in text:
                    matching_comments.append(comment)

            print(
                f"🔍 Найдено комментариев с ключевым словом '{keyword}': {len(matching_comments)}"
            )

            for i, comment in enumerate(matching_comments[:5], 1):
                print(f"   {i}. ID: {comment.get('id', 'N/A')}")
                print(f"      Автор: {comment.get('from_id', 'N/A')}")
                print(f"      Дата: {comment.get('date', 'N/A')}")
                print(f"      Текст: {comment.get('text', 'N/A')[:100]}...")
                print(
                    f"      Лайков: {comment.get('likes', {}).get('count', 0)}"
                )
                print()

        except Exception as e:
            print(f"❌ Ошибка при получении комментариев: {e}")

        # Тест 4: Получение всех комментариев к посту
        print(f"\n💬 Тест 4: Получение всех комментариев к посту {post_id}")
        try:
            all_comments = await vk_service.get_all_post_comments(
                owner_id=-group_id, post_id=post_id
            )
            print(f"✅ Получено всех комментариев: {len(all_comments)}")

            # Статистика по комментариям
            total_likes = sum(
                comment.get("likes", {}).get("count", 0)
                for comment in all_comments
            )
            print(f"   Общее количество лайков: {total_likes}")

            # Поиск комментариев с "гиви"
            keyword = "гиви"
            matching_comments = [
                c for c in all_comments if keyword in c.get("text", "").lower()
            ]
            print(f"   Комментариев с '{keyword}': {len(matching_comments)}")

        except Exception as e:
            print(f"❌ Ошибка при получении всех комментариев: {e}")


if __name__ == "__main__":
    asyncio.run(test_riabirobidzhan())
