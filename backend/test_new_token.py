#!/usr/bin/env python3
"""
Скрипт для тестирования нового токена с конкретным постом
"""

import asyncio
import httpx


async def test_new_token():
    """Тестирует новый токен с конкретным постом"""
    # Новый токен
    token = "vk1.a.EwV_6ctsK5EH6XvL4-GIep-yY9xbiGn1xluN6dj4UhPEeS9ATWXl7OAe_KAvqdBOb8ZMXt9CRmhzsupqQiLhpwCEUPGgvYHGK_zB2cVmubiezx36CuX7rkWLVSDlBXzdhY9QYY5qv7M3G3dMGSZ1g7v_QFqkgYXenlNNSQsVnbvtl5JDDcgt2-v-U5Y1ArnEueVOOTmj2DNJmEqfjDPrtQ"
    api_version = "5.131"

    print("🔍 Тестирование нового токена с постом 126563...")

    # Проверяем доступ к комментариям конкретного поста
    url = "https://api.vk.com/method/wall.getComments"
    params = {
        "access_token": token,
        "v": api_version,
        "owner_id": -43377172,  # Отрицательный ID для группы
        "post_id": 126563,
        "count": 100,
        "sort": "asc",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            if "error" in data:
                error_code = data["error"].get("error_code", "unknown")
                error_msg = data["error"].get("error_msg", "unknown")
                print(
                    f"❌ Ошибка доступа к комментариям: {error_code} - {error_msg}"
                )

                if error_code == 15:
                    print(
                        "   💡 Код 15: Access denied - комментарии недоступны"
                    )
                    print(
                        "   Проблема НЕ в токене, а в настройках группы/поста"
                    )
                elif error_code == 5:
                    print(
                        "   💡 Код 5: Authorization failed - проблема с токеном"
                    )
                else:
                    print(f"   💡 Код {error_code}: {error_msg}")
            else:
                print("✅ Доступ к комментариям: OK")
                response_data = data.get("response", {})
                comments_count = response_data.get("count", 0)
                comments = response_data.get("items", [])

                print(f"   Количество комментариев: {comments_count}")
                print(f"   Получено комментариев: {len(comments)}")

                # Ищем комментарии с "гиви"
                found_givi = False
                for comment in comments:
                    text = comment.get("text", "").lower()
                    if "гиви" in text:
                        found_givi = True
                        print(
                            f"   ✅ Найден комментарий с 'гиви': {comment.get('text', '')[:100]}..."
                        )
                        print(
                            f"      ID: {comment.get('id')}, автор: {comment.get('from_id')}"
                        )

                if not found_givi:
                    print("   ❌ Комментарии с 'гиви' не найдены")

                # Показываем первые несколько комментариев
                print(f"\n📝 Первые 3 комментария:")
                for i, comment in enumerate(comments[:3]):
                    print(
                        f"   {i+1}. ID: {comment.get('id')}, текст: {comment.get('text', '')[:50]}..."
                    )

    except Exception as e:
        print(f"❌ Ошибка при получении комментариев: {e}")

    # Также проверим доступ к стене группы
    print(f"\n🔍 Проверка доступа к стене группы...")
    url = "https://api.vk.com/method/wall.get"
    params = {
        "access_token": token,
        "v": api_version,
        "owner_id": -43377172,
        "count": 1,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            if "error" in data:
                print(f"❌ Ошибка доступа к стене: {data['error']}")
            else:
                print("✅ Доступ к стене группы: OK")
                posts_count = data.get("response", {}).get("count", 0)
                print(f"   Количество постов: {posts_count}")

    except Exception as e:
        print(f"❌ Ошибка при получении постов: {e}")


if __name__ == "__main__":
    asyncio.run(test_new_token())
