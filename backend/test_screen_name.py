#!/usr/bin/env python3
"""
Тест для screen_name
"""

import asyncio
import httpx
from app.core.config import settings


async def test_screen_name():
    """Тест для screen_name"""
    print("🔍 Тест screen_name...")

    url = "https://api.vk.com/method/groups.getById"

    # Тест с group_id=0 и screen_name
    params = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
        "group_id": 0,
        "screen_name": "durov",
    }

    async with httpx.AsyncClient() as client:
        print("\n📋 Тест: group_id=0, screen_name=durov")
        try:
            response = await client.post(url, data=params)
            data = response.json()
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {data}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(test_screen_name())
