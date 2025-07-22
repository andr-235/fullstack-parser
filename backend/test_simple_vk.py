#!/usr/bin/env python3
"""
Простой тест VK API
"""

import asyncio

import httpx

from app.core.config import settings


async def test_simple_vk_api():
    """Простой тест VK API"""
    print("🔍 Простой тест VK API...")

    url = "https://api.vk.com/method/groups.getById"

    # Тест 1: С group_id
    params1 = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
        "group_id": 1,
    }

    # Тест 2: С group_ids
    params2 = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
        "group_ids": 1,
    }

    # Тест 3: С screen_name
    params3 = {
        "access_token": settings.vk.access_token,
        "v": settings.vk.api_version,
        "screen_name": "durov",
    }

    async with httpx.AsyncClient() as client:
        print("\n📋 Тест 1: group_id")
        try:
            response = await client.post(url, data=params1)
            data = response.json()
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {data}")
        except Exception as e:
            print(f"Ошибка: {e}")

        print("\n📋 Тест 2: group_ids")
        try:
            response = await client.post(url, data=params2)
            data = response.json()
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {data}")
        except Exception as e:
            print(f"Ошибка: {e}")

        print("\n📋 Тест 3: screen_name")
        try:
            response = await client.post(url, data=params3)
            data = response.json()
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {data}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(test_simple_vk_api())
