#!/usr/bin/env python3
"""
Скрипт для тестирования API комментариев и проверки исправлений
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any


async def test_comments_api():
    """Тестирует API комментариев"""

    # Базовый URL API
    base_url = "https://localhost/api/v1"

    async with httpx.AsyncClient(
        verify=False
    ) as client:  # Отключаем проверку SSL для локального тестирования
        print("🔍 Тестирование API комментариев...")

        # Тест 1: Получение комментариев с пагинацией
        print("\n1. Тест пагинации комментариев:")
        try:
            response = await client.get(
                f"{base_url}/parser/comments", params={"page": 1, "size": 10}
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Успешно получено {len(data['items'])} комментариев")
                print(f"   Всего комментариев: {data['total']}")
                print(f"   Страница: {data['page']}")
                print(f"   Размер страницы: {data['size']}")

                if data["items"]:
                    first_comment = data["items"][0]
                    print(f"   Первый комментарий ID: {first_comment.get('id')}")
                    print(f"   Текст: {first_comment.get('text', '')[:50]}...")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"   Ответ: {response.text}")

        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

        # Тест 2: Фильтрация по группе
        print("\n2. Тест фильтрации по группе:")
        try:
            response = await client.get(
                f"{base_url}/parser/comments",
                params={
                    "page": 1,
                    "size": 5,
                    "group_id": 1,  # Предполагаем, что группа с ID 1 существует
                },
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Фильтрация по группе: {len(data['items'])} комментариев")
            else:
                print(f"❌ Ошибка фильтрации: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

        # Тест 3: Фильтрация по ключевому слову
        print("\n3. Тест фильтрации по ключевому слову:")
        try:
            response = await client.get(
                f"{base_url}/parser/comments",
                params={
                    "page": 1,
                    "size": 5,
                    "keyword_id": 1,  # Предполагаем, что ключевое слово с ID 1 существует
                },
            )

            if response.status_code == 200:
                data = response.json()
                print(
                    f"✅ Фильтрация по ключевому слову: {len(data['items'])} комментариев"
                )
            else:
                print(f"❌ Ошибка фильтрации: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

        # Тест 4: Проверка глобальной статистики
        print("\n4. Тест глобальной статистики:")
        try:
            response = await client.get(f"{base_url}/stats/global")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Глобальная статистика:")
                print(f"   Всего групп: {data.get('total_groups', 0)}")
                print(f"   Активных групп: {data.get('active_groups', 0)}")
                print(f"   Всего ключевых слов: {data.get('total_keywords', 0)}")
                print(f"   Активных ключевых слов: {data.get('active_keywords', 0)}")
                print(f"   Всего комментариев: {data.get('total_comments', 0)}")
                print(
                    f"   Комментариев с ключевыми словами: {data.get('comments_with_keywords', 0)}"
                )
            else:
                print(f"❌ Ошибка статистики: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

        # Тест 5: Проверка состояния парсера
        print("\n5. Тест состояния парсера:")
        try:
            response = await client.get(f"{base_url}/parser/state")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Состояние парсера: {data.get('status', 'unknown')}")
                if data.get("task"):
                    task = data["task"]
                    print(f"   Текущая задача: {task.get('task_id', 'N/A')}")
                    print(f"   Группа: {task.get('group_id', 'N/A')}")
                    print(f"   Прогресс: {task.get('progress', 0)}%")
            else:
                print(f"❌ Ошибка состояния парсера: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")


async def test_arq_worker_logs():
    """Проверяет логи arq_worker на наличие ошибок"""
    print("\n🔍 Проверка логов arq_worker...")

    try:
        # Используем docker logs для проверки
        import subprocess

        result = subprocess.run(
            ["docker", "logs", "fullstack_prod_arq_worker", "--tail", "50"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logs = result.stdout

            # Проверяем на наличие ошибок
            error_count = (
                logs.count("ERROR") + logs.count("error") + logs.count("Error")
            )
            sort_error_count = logs.count("sort should be asc, desc or smart")

            print(f"✅ Логи получены (последние 50 строк)")
            print(f"   Найдено ошибок: {error_count}")
            print(f"   Ошибок сортировки: {sort_error_count}")

            if sort_error_count > 0:
                print("   ⚠️  Обнаружены ошибки сортировки VK API")
            else:
                print("   ✅ Ошибки сортировки не найдены")

            # Показываем последние ошибки
            lines = logs.split("\n")
            error_lines = [
                line
                for line in lines
                if any(err in line.lower() for err in ["error", "exception"])
            ]

            if error_lines:
                print("\n   Последние ошибки:")
                for line in error_lines[-5:]:  # Последние 5 ошибок
                    print(f"   {line}")

        else:
            print(f"❌ Ошибка получения логов: {result.stderr}")

    except Exception as e:
        print(f"❌ Ошибка проверки логов: {e}")


async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования исправлений...")

    # Тестируем API
    await test_comments_api()

    # Проверяем логи
    await test_arq_worker_logs()

    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())
