#!/usr/bin/env python3
"""
Скрипт для проверки прав токена VK API
"""

import asyncio
import httpx
from app.core.config import settings


async def check_vk_token():
    """Проверяет права токена VK API"""
    print("🔍 Проверка токена VK API...")
    print(
        f"Токен: {settings.vk.access_token[:10]}...{settings.vk.access_token[-10:]}"
    )
    print(f"Версия API: {settings.vk.api_version}")

    # Проверяем базовую информацию о токене
    url = "https://api.vk.com/method/account.getInfo"
    params = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            if "error" in data:
                print(f"❌ Ошибка токена: {data['error']}")
                return False

            print("✅ Токен валиден")
            print(f"   Информация: {data.get('response', {})}")

    except Exception as e:
        print(f"❌ Ошибка проверки токена: {e}")
        return False

    # Проверяем права на группы
    print("\n🔍 Проверка прав на группы...")
    url = "https://api.vk.com/method/groups.get"
    params = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
        "extended": 1,
        "count": 1,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            if "error" in data:
                print(f"❌ Ошибка доступа к группам: {data['error']}")
            else:
                print("✅ Права на группы: OK")

    except Exception as e:
        print(f"❌ Ошибка проверки групп: {e}")

    # Проверяем доступ к конкретной группе
    print(f"\n🔍 Проверка доступа к группе riabirobidzhan (43377172)...")
    url = "https://api.vk.com/method/wall.get"
    params = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
        "owner_id": -43377172,
        "count": 1,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            if "error" in data:
                print(f"❌ Ошибка доступа к стене группы: {data['error']}")
            else:
                print("✅ Доступ к стене группы: OK")
                posts_count = data.get("response", {}).get("count", 0)
                print(f"   Количество постов: {posts_count}")

    except Exception as e:
        print(f"❌ Ошибка проверки стены: {e}")

    # Проверяем доступ к комментариям конкретного поста
    print(f"\n🔍 Проверка доступа к комментариям поста 126563...")
    url = "https://api.vk.com/method/wall.getComments"
    params = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
        "owner_id": -43377172,
        "post_id": 126563,
        "count": 1,
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
                    print("   Возможные причины:")
                    print("   - Группа закрыта для комментариев")
                    print("   - Токен не имеет прав на чтение комментариев")
                    print("   - Пост закрыт для комментариев")
                    print("   - Требуется быть участником группы")
            else:
                print("✅ Доступ к комментариям: OK")
                comments_count = data.get("response", {}).get("count", 0)
                print(f"   Количество комментариев: {comments_count}")

    except Exception as e:
        print(f"❌ Ошибка проверки комментариев: {e}")

    print("\n📋 Рекомендации:")
    print("1. Проверьте права токена в настройках VK приложения")
    print("2. Убедитесь, что токен имеет права: groups, wall, comments")
    print("3. Проверьте настройки приватности группы riabirobidzhan")
    print(
        "4. Возможно, требуется быть участником группы для доступа к комментариям"
    )


if __name__ == "__main__":
    asyncio.run(check_vk_token())
