#!/usr/bin/env python3
"""
Тестовый скрипт для проверки ключевого слова "гиви"
"""

import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.keyword import Keyword
from app.services.morphological_service import morphological_service


async def test_keyword_search():
    """Тестирует поиск ключевого слова 'гиви'"""
    async with AsyncSessionLocal() as db:
        # Проверяем наличие ключевого слова "гиви" в базе
        result = await db.execute(
            select(Keyword).where(Keyword.word.ilike("%гиви%"))
        )
        keywords = result.scalars().all()

        print(f"Найдено ключевых слов с 'гиви': {len(keywords)}")
        for kw in keywords:
            print(
                f"  - ID: {kw.id}, слово: '{kw.word}', активен: {kw.is_active}"
            )

        # Проверяем все активные ключевые слова
        result = await db.execute(
            select(Keyword).where(Keyword.is_active == True)
        )
        active_keywords = result.scalars().all()

        print(f"\nВсего активных ключевых слов: {len(active_keywords)}")
        print("Первые 10 активных ключевых слов:")
        for kw in active_keywords[:10]:
            print(f"  - '{kw.word}' (категория: {kw.category})")

        # Тестируем морфологический поиск
        test_text = "гиви это круто, ГИВИ, гивишный"
        print(f"\nТестируем морфологический поиск в тексте: '{test_text}'")

        # Проверяем поиск слова "гиви"
        matches = morphological_service.find_morphological_matches(
            text=test_text,
            keyword="гиви",
            case_sensitive=False,
            whole_word=False,
        )

        print(f"Найдено совпадений для 'гиви': {len(matches)}")
        for matched_text, position in matches:
            print(f"  - '{matched_text}' на позиции {position}")

        # Проверяем поиск с учетом регистра
        matches_case = morphological_service.find_morphological_matches(
            text=test_text,
            keyword="гиви",
            case_sensitive=True,
            whole_word=False,
        )

        print(
            f"Найдено совпадений для 'гиви' (с учетом регистра): {len(matches_case)}"
        )
        for matched_text, position in matches_case:
            print(f"  - '{matched_text}' на позиции {position}")


if __name__ == "__main__":
    asyncio.run(test_keyword_search())
