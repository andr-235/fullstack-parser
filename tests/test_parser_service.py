import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.parser_service import ParserService
from app.services.vkbottle_service import VKBottleService


@pytest.mark.asyncio
def test_parse_group_posts_basic(monkeypatch):
    # Мокаем VKBottleService
    vk_service = MagicMock(spec=VKBottleService)
    vk_service.get_group_posts = AsyncMock(
        return_value=[{"id": 1, "text": "test post"}]
    )
    vk_service.get_post_comments = AsyncMock(
        return_value=[{"id": 1, "text": "test comment"}]
    )

    # Мокаем асинхронную сессию БД
    db = MagicMock()

    # Создаём ParserService
    parser = ParserService(db=db, vk_service=vk_service)

    # Мокаем внутренние методы, чтобы не трогать реальную БД
    parser._save_post = AsyncMock()
    parser._save_comment = AsyncMock()
    parser._find_keywords = MagicMock(return_value=["test"])

    # Запускаем парсинг
    stats = (
        pytest.run(
            asyncio.run(
                parser.parse_group_posts(
                    group_id=1,
                    max_posts_count=1,
                    force_reparse=True,
                    progress_callback=None,
                )
            )
        )
        if hasattr(pytest, "run")
        else None
    )
    # Проверяем, что методы были вызваны
    parser._save_post.assert_called()
    parser._save_comment.assert_called()
    parser._find_keywords.assert_called()
