#!/usr/bin/env python3
"""
Тестовый скрипт для проверки VK API
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()


async def test_vk_api():
    """Тестируем VK API для получения постов и комментариев"""

    token = os.getenv("VK_ACCESS_TOKEN")
    if not token:
        print("VK_ACCESS_TOKEN не найден в .env файле")
        return

    print(f"Используем токен: {token[:8]}...")

    # Получаем посты группы
    group_id = 40023088
    owner_id = -group_id  # Отрицательный ID для группы

    async with httpx.AsyncClient() as client:
        # Получаем посты
        url = "https://api.vk.com/method/wall.get"
        params = {
            "owner_id": owner_id,
            "count": 5,
            "access_token": token,
            "v": "5.199",
        }

        print(f"Запрашиваем посты для группы {group_id} (owner_id={owner_id})")
        response = await client.get(url, params=params)
        data = response.json()

        if "error" in data:
            print(f"Ошибка VK API: {data['error']}")
            return

        if "response" in data and data["response"]:
            posts = data["response"]["items"]
            print(f"Получено {len(posts)} постов")

            for i, post in enumerate(posts):
                print(f"\nПост {i+1}:")
                print(f"  ID: {post.get('id')}")
                print(f"  Owner ID: {post.get('owner_id')}")
                print(f"  Комментарии: {post.get('comments', {}).get('count', 0)}")
                print(f"  Текст: {post.get('text', '')[:100]}...")

                # Получаем комментарии к посту
                comments_count = post.get("comments", {}).get("count", 0)
                if comments_count > 0:
                    print(f"  Получаем комментарии к посту {post.get('id')}...")

                    comments_url = "https://api.vk.com/method/wall.getComments"
                    comments_params = {
                        "owner_id": owner_id,
                        "post_id": post.get("id"),
                        "count": 10,
                        "access_token": token,
                        "v": "5.199",
                    }

                    comments_response = await client.get(
                        comments_url, params=comments_params
                    )
                    comments_data = comments_response.json()

                    if "error" in comments_data:
                        print(
                            f"    Ошибка получения комментариев: {comments_data['error']}"
                        )
                    elif "response" in comments_data and comments_data["response"]:
                        comments = comments_data["response"]["items"]
                        print(f"    Получено {len(comments)} комментариев")

                        for j, comment in enumerate(comments):
                            print(f"    Комментарий {j+1}:")
                            print(f"      ID: {comment.get('id')}")
                            print(f"      Автор: {comment.get('from_id')}")
                            print(f"      Текст: {comment.get('text', '')[:100]}...")

                            # Проверяем, содержит ли комментарий слово "Биробиджан"
                            text = comment.get("text", "").lower()
                            if "биробиджан" in text:
                                print(f"      ✅ Содержит 'Биробиджан'!")
                            else:
                                print(f"      ❌ Не содержит 'Биробиджан'")
        else:
            print("Пустой ответ от VK API")


if __name__ == "__main__":
    asyncio.run(test_vk_api())
