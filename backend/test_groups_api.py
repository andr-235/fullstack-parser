#!/usr/bin/env python3
"""
Простой тест для проверки API групп с поиском
"""

import asyncio
import httpx
import json


async def test_groups_api():
    """Тестируем API групп с поиском"""
    base_url = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient() as client:
        # Тест 1: Получение всех групп
        print("🔍 Тест 1: Получение всех групп...")
        response = await client.get(f"{base_url}/groups/")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Всего групп: {data.get('total', 0)}")
            print(f"Элементов на странице: {len(data.get('items', []))}")
        else:
            print(f"Ошибка: {response.text}")

        print()

        # Тест 2: Поиск групп
        print("🔍 Тест 2: Поиск групп...")
        response = await client.get(f"{base_url}/groups/?search=test")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Найдено групп: {data.get('total', 0)}")
            print(f"Элементов на странице: {len(data.get('items', []))}")
        else:
            print(f"Ошибка: {response.text}")

        print()

        # Тест 3: Пагинация
        print("🔍 Тест 3: Пагинация...")
        response = await client.get(f"{base_url}/groups/?page=1&size=5")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Всего групп: {data.get('total', 0)}")
            print(f"Страница: {data.get('page', 0)}")
            print(f"Размер страницы: {data.get('size', 0)}")
            print(f"Элементов на странице: {len(data.get('items', []))}")
        else:
            print(f"Ошибка: {response.text}")


if __name__ == "__main__":
    asyncio.run(test_groups_api())
