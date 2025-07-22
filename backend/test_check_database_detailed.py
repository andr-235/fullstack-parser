#!/usr/bin/env python3
"""
Детальный тест для проверки комментариев с ключевыми словами в базе данных
"""

import asyncio

from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment


async def test_check_database_detailed():
    """Детально проверяет базу данных на наличие комментариев с ключевыми словами"""
    print("🔍 Детальная проверка базы данных...")

    async with AsyncSessionLocal() as db:
        # 1. Проверяем все комментарии с текстом "гиви"
        print("\n📋 1. Все комментарии с текстом 'гиви':")
        result = await db.execute(
            select(VKComment).where(VKComment.text.ilike("%гиви%"))
        )
        comments_with_givi = result.scalars().all()

        print(
            f"   Найдено комментариев с 'гиви' в тексте: {len(comments_with_givi)}"
        )
        for comment in comments_with_givi:
            print(f"   - ID: {comment.id}, VK ID: {comment.vk_id}")
            print(f"     Текст: {comment.text}")
            print(f"     is_processed: {comment.is_processed}")
            print(
                f"     matched_keywords_count: {comment.matched_keywords_count}"
            )
            print(f"     Обработан: {comment.processed_at}")
            print()

        # 2. Проверяем комментарии с matched_keywords_count > 0
        print("\n📋 2. Комментарии с matched_keywords_count > 0:")
        result = await db.execute(
            select(VKComment).where(VKComment.matched_keywords_count > 0)
        )
        comments_with_matches = result.scalars().all()

        print(
            f"   Найдено комментариев с matched_keywords_count > 0: {len(comments_with_matches)}"
        )
        for comment in comments_with_matches:
            print(f"   - ID: {comment.id}, VK ID: {comment.vk_id}")
            print(f"     Текст: {comment.text}")
            print(
                f"     matched_keywords_count: {comment.matched_keywords_count}"
            )
            print(f"     is_processed: {comment.is_processed}")
            print()

        # 3. Проверяем комментарии с is_processed = True
        print("\n📋 3. Комментарии с is_processed = True:")
        result = await db.execute(
            select(VKComment).where(VKComment.is_processed == True)
        )
        processed_comments = result.scalars().all()

        print(
            f"   Найдено обработанных комментариев: {len(processed_comments)}"
        )

        # 4. Проверяем комментарии, которые должны отображаться в API
        print(
            "\n📋 4. Комментарии, которые должны отображаться в API (is_processed=True AND matched_keywords_count>0):"
        )
        result = await db.execute(
            select(VKComment).where(
                and_(
                    VKComment.is_processed == True,
                    VKComment.matched_keywords_count > 0,
                )
            )
        )
        api_comments = result.scalars().all()

        print(f"   Найдено комментариев для API: {len(api_comments)}")
        for comment in api_comments:
            print(f"   - ID: {comment.id}, VK ID: {comment.vk_id}")
            print(f"     Текст: {comment.text}")
            print(
                f"     matched_keywords_count: {comment.matched_keywords_count}"
            )
            print()

        # 5. Проверяем таблицу совпадений ключевых слов
        print("\n📋 5. Записи в таблице CommentKeywordMatch:")
        result = await db.execute(
            select(CommentKeywordMatch)
            .options(selectinload(CommentKeywordMatch.comment))
            .options(selectinload(CommentKeywordMatch.keyword))
        )
        matches = result.scalars().all()

        print(f"   Найдено записей совпадений: {len(matches)}")
        for match in matches:
            print(f"   - Match ID: {match.id}")
            print(
                f"     Comment ID: {match.comment_id}, VK ID: {match.comment.vk_id if match.comment else 'N/A'}"
            )
            print(
                f"     Keyword ID: {match.keyword_id}, Word: {match.keyword.word if match.keyword else 'N/A'}"
            )
            print(f"     Matched Text: {match.matched_text}")
            print()

        # 6. Проверяем ключевое слово "гиви"
        print("\n📋 6. Ключевое слово 'гиви':")
        result = await db.execute(
            select(Keyword).where(Keyword.word.ilike("%гиви%"))
        )
        givi_keywords = result.scalars().all()

        print(f"   Найдено ключевых слов с 'гиви': {len(givi_keywords)}")
        for keyword in givi_keywords:
            print(
                f"   - ID: {keyword.id}, Word: {keyword.word}, Active: {keyword.is_active}"
            )

            # Проверяем совпадения для этого ключевого слова
            result = await db.execute(
                select(CommentKeywordMatch)
                .where(CommentKeywordMatch.keyword_id == keyword.id)
                .options(selectinload(CommentKeywordMatch.comment))
            )
            keyword_matches = result.scalars().all()
            print(
                f"     Совпадений для этого ключевого слова: {len(keyword_matches)}"
            )
            for match in keyword_matches:
                print(
                    f"       - Comment ID: {match.comment_id}, VK ID: {match.comment.vk_id if match.comment else 'N/A'}"
                )
                print(
                    f"         Text: {match.comment.text if match.comment else 'N/A'}"
                )
            print()


if __name__ == "__main__":
    asyncio.run(test_check_database_detailed())
