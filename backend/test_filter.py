#!/usr/bin/env python3
"""
Простой тест фильтрации по author_screen_name
"""

import asyncio
import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, "/app")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.parser_service import ParserService
from app.schemas.vk_comment import CommentSearchParams
from app.models.vk_comment import VKComment
from app.models.vk_post import VKPost
from app.models.vk_group import VKGroup
from datetime import datetime, timezone


async def test_filter():
    """Тест фильтрации"""

    # Подключаемся к БД
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@postgres:5432/vk_parser",
    )
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Создаем тестовые данные
        group = VKGroup(
            id=999, vk_id=123, name="Test Group", screen_name="test_group"
        )
        session.add(group)
        await session.commit()

        post = VKPost(id=999, vk_id=456, group_id=group.id, text="Test post")
        session.add(post)
        await session.commit()

        # Создаем комментарии от разных авторов
        comment1 = VKComment(
            id=999,
            text="Comment from author1",
            author_id=111,
            author_name="Author 1",
            author_screen_name="author1",
            vk_id=789,
            post_id=post.id,
            published_at=datetime.now(timezone.utc),
            is_processed=True,
            matched_keywords_count=1,
            is_viewed=False,
        )

        comment2 = VKComment(
            id=1000,
            text="Comment from author2",
            author_id=222,
            author_name="Author 2",
            author_screen_name="author2",
            vk_id=790,
            post_id=post.id,
            published_at=datetime.now(timezone.utc),
            is_processed=True,
            matched_keywords_count=1,
            is_viewed=False,
        )

        session.add_all([comment1, comment2])
        await session.commit()

        # Создаем сервис
        service = ParserService(session, None)

        print("=== ТЕСТ ФИЛЬТРАЦИИ ===")

        # Тест 1: Без фильтра
        search_params = CommentSearchParams(is_viewed=False)
        result = await service.get_comments(search_params, page=1, size=20)
        print(f"Без фильтра: {result.total} комментариев")

        # Тест 2: С фильтром по author1
        search_params = CommentSearchParams(
            is_viewed=False, author_screen_name=["author1"]
        )
        result = await service.get_comments(search_params, page=1, size=20)
        print(f"С фильтром author1: {result.total} комментариев")
        for comment in result.items:
            print(f"  - {comment.author_screen_name}: {comment.text}")

        # Тест 3: С фильтром по author2
        search_params = CommentSearchParams(
            is_viewed=False, author_screen_name=["author2"]
        )
        result = await service.get_comments(search_params, page=1, size=20)
        print(f"С фильтром author2: {result.total} комментариев")
        for comment in result.items:
            print(f"  - {comment.author_screen_name}: {comment.text}")

        # Тест 4: С фильтром по id217878560 (реальный автор)
        search_params = CommentSearchParams(
            is_viewed=False, author_screen_name=["id217878560"]
        )
        result = await service.get_comments(search_params, page=1, size=20)
        print(f"С фильтром id217878560: {result.total} комментариев")
        for comment in result.items:
            print(f"  - {comment.author_screen_name}: {comment.text}")

        # Очищаем тестовые данные
        await session.delete(comment1)
        await session.delete(comment2)
        await session.delete(post)
        await session.delete(group)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(test_filter())
