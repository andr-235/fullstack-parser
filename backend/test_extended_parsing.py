#!/usr/bin/env python3
"""
Тест для расширенного парсинга с большим количеством постов
"""

import asyncio

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.parser_service import ParserService
from app.services.vk_api_service import VKAPIService


async def test_extended_parsing():
    """Тестирует расширенный парсинг с большим количеством постов"""
    print("🔍 Тестируем расширенный парсинг с большим количеством постов...")

    async with AsyncSessionLocal() as db:
        # Создаем новый VK API сервис
        vk_service = VKAPIService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

        # Создаем парсер сервис
        parser_service = ParserService(db=db, vk_service=vk_service)

        # Параметры для тестирования
        group_id = 43377172  # РИА Биробиджан
        target_post_id = 126563  # Пост с комментарием "гиви"
        keywords = ["гиви"]  # Ключевые слова для поиска

        print(
            f"\n📋 Тест 1: Проверяем, есть ли пост {target_post_id} в последних постах"
        )
        try:
            # Получаем больше постов для проверки
            posts = await vk_service.get_group_posts(
                group_id=group_id, count=100
            )
            print(f"✅ Получено постов: {len(posts)}")

            # Ищем целевой пост
            target_post = None
            for post in posts:
                if post.get("id") == target_post_id:
                    target_post = post
                    break

            if target_post:
                print(
                    f"✅ Пост {target_post_id} найден в последних {len(posts)} постах!"
                )
                print(f"   Текст: {target_post.get('text', '')[:100]}...")
                print(
                    f"   Комментариев: {target_post.get('comments', {}).get('count', 0)}"
                )
            else:
                print(
                    f"❌ Пост {target_post_id} НЕ найден в последних {len(posts)} постах"
                )
                print(
                    f"   Диапазон ID постов: {posts[-1].get('id')} - {posts[0].get('id')}"
                )

        except Exception as e:
            print(f"❌ Ошибка при получении постов: {e}")

        print(
            f"\n📋 Тест 2: Расширенный парсинг группы {group_id} (50 постов)"
        )
        try:
            # Запускаем парсинг с меньшим количеством постов
            result = await parser_service.parse_group_posts(
                group_id=group_id,
                max_posts_count=50,  # Уменьшаем до 50 постов
                force_reparse=False,
            )

            print("✅ Результат парсинга:")
            print(f"   Обработано постов: {result.posts_processed}")
            print(f"   Найдено комментариев: {result.comments_found}")
            print(f"   Найдено совпадений: {result.keyword_matches}")
            print(f"   Время выполнения: {result.duration_seconds:.2f} сек")

            # Проверяем, есть ли совпадения с ключевым словом "гиви"
            if result.keyword_matches > 0:
                print("\n🔍 Найдены совпадения с ключевым словом 'гиви'!")

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
    asyncio.run(test_extended_parsing())
