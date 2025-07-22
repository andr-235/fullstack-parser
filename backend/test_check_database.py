#!/usr/bin/env python3
"""
Тест для проверки базы данных на наличие комментариев с "гиви"
"""

import asyncio

from app.core.database import AsyncSessionLocal
from app.services.parser_service import ParserService


async def test_check_database():
    """Проверяет базу данных на наличие комментариев с "гиви" """
    print("🔍 Проверяем базу данных на наличие комментариев с 'гиви'...")

    async with AsyncSessionLocal() as db:
        # Создаем парсер сервис
        parser_service = ParserService(
            db=db, vk_service=None
        )  # Не нужен VK сервис для чтения БД

        print("\n📋 Поиск комментариев с ключевым словом 'гиви'")
        try:
            # Получаем комментарии с ключевыми словами
            from app.schemas.base import PaginationParams
            from app.schemas.vk_comment import CommentSearchParams

            search_params = CommentSearchParams(keywords=["гиви"])
            pagination = PaginationParams(page=1, size=10)

            comments = await parser_service.filter_comments(
                search_params=search_params, pagination=pagination
            )

            if comments.items:
                print(
                    f"✅ Найдено комментариев с 'гиви': {len(comments.items)}"
                )
                for i, comment in enumerate(comments.items, 1):
                    print(f"\n   {i}. Комментарий ID: {comment.id}")
                    print(f"      VK ID: {comment.vk_id}")
                    print(f"      Автор: {comment.author_id}")
                    print(f"      Текст: {comment.text}")
                    print(f"      Дата: {comment.created_at}")
                    print(f"      Пост ID: {comment.post_id}")
                    print(
                        f"      Группа: {comment.group.name if comment.group else 'N/A'}"
                    )

                    # Получаем детальную информацию о комментарии с ключевыми словами
                    try:
                        comment_with_keywords = (
                            await parser_service.get_comment_with_keywords(
                                comment.id
                            )
                        )
                        if (
                            comment_with_keywords
                            and comment_with_keywords.keyword_matches
                        ):
                            print("      Найденные ключевые слова:")
                            for match in comment_with_keywords.keyword_matches:
                                print(
                                    f"        - {match.keyword.word} (позиция: {match.position})"
                                )
                    except Exception as e:
                        print(
                            f"      ❌ Ошибка при получении ключевых слов: {e}"
                        )
            else:
                print("❌ Комментарии с 'гиви' не найдены в базе данных")

        except Exception as e:
            print(f"❌ Ошибка при поиске комментариев: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_check_database())
