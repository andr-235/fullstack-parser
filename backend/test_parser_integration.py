#!/usr/bin/env python3
"""
Тест интеграции парсера с новым VK API сервисом
"""

import asyncio
from app.services.vk_api_service import VKAPIService
from app.services.parser_service import ParserService
from app.core.database import AsyncSessionLocal
from app.core.config import settings


async def test_parser_integration():
    """Тестирует интеграцию парсера с новым VK API сервисом"""
    print("🔍 Тестируем интеграцию парсера с новым VK API сервисом...")

    async with AsyncSessionLocal() as db:
        # Создаем новый VK API сервис
        vk_service = VKAPIService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

        # Создаем парсер сервис
        parser_service = ParserService(db=db, vk_service=vk_service)

        # Параметры для тестирования
        group_id = 43377172  # РИА Биробиджан
        keywords = ["гиви"]  # Ключевые слова для поиска

        print(
            f"\n📋 Тест 1: Парсинг группы {group_id} с поиском ключевых слов {keywords}"
        )
        try:
            # Запускаем парсинг группы
            result = await parser_service.parse_group_posts(
                group_id=group_id,
                max_posts_count=5,  # Ограничиваем количество постов для теста
                force_reparse=False,
            )

            print(f"✅ Результат парсинга:")
            print(f"   Обработано постов: {result.posts_processed}")
            print(f"   Найдено комментариев: {result.comments_found}")
            print(f"   Найдено совпадений: {result.keyword_matches}")
            print(f"   Время выполнения: {result.duration_seconds:.2f} сек")

            # Проверяем, есть ли совпадения с ключевым словом "гиви"
            if result.keyword_matches > 0:
                print(f"\n🔍 Найдены совпадения с ключевым словом 'гиви'!")

                # Получаем комментарии с ключевыми словами
                comments = await parser_service.filter_comments(
                    search_params={"keywords": ["гиви"]},
                    pagination={"page": 1, "size": 10},
                )

                if comments.items:
                    print(
                        f"   Найдено комментариев с 'гиви': {len(comments.items)}"
                    )
                    for i, comment in enumerate(comments.items[:3], 1):
                        print(f"   {i}. Комментарий ID: {comment.id}")
                        print(f"      Автор: {comment.author_id}")
                        print(f"      Текст: {comment.text[:100]}...")
                        print(f"      Дата: {comment.date}")
                        print()
                else:
                    print(
                        "   ❌ Комментарии с 'гиви' не найдены в базе данных"
                    )
            else:
                print("   ❌ Совпадений с ключевым словом 'гиви' не найдено")

        except Exception as e:
            print(f"❌ Ошибка при парсинге: {e}")
            import traceback

            traceback.print_exc()

        # Закрываем VK сервис
        await vk_service.close()


if __name__ == "__main__":
    asyncio.run(test_parser_integration())
