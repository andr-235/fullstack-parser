import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.parser_service import ParserService
from app.schemas.vk_comment import CommentSearchParams
from app.models.vk_comment import VKComment
from app.models.vk_post import VKPost
from app.models.vk_group import VKGroup
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_filter_by_author_screen_name(db_session: AsyncSession):
    """Тест фильтрации по author_screen_name"""

    # Создаем тестовые данные
    group = VKGroup(
        id=1, vk_id=123, name="Test Group", screen_name="test_group"
    )
    db_session.add(group)
    await db_session.commit()

    post = VKPost(id=1, vk_id=456, group_id=group.id, text="Test post")
    db_session.add(post)
    await db_session.commit()

    # Создаем комментарии от разных авторов
    comment1 = VKComment(
        id=1,
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
        id=2,
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

    comment3 = VKComment(
        id=3,
        text="Comment from author1 again",
        author_id=111,
        author_name="Author 1",
        author_screen_name="author1",
        vk_id=791,
        post_id=post.id,
        published_at=datetime.now(timezone.utc),
        is_processed=True,
        matched_keywords_count=1,
        is_viewed=False,
    )

    db_session.add_all([comment1, comment2, comment3])
    await db_session.commit()

    # Создаем сервис
    service = ParserService(db_session, None)

    # Тест 1: Без фильтра - должны быть все комментарии
    search_params = CommentSearchParams(is_viewed=False)
    result = await service.get_comments(search_params, page=1, size=20)
    assert result.total == 3

    # Тест 2: С фильтром по author_screen_name - должны быть только комментарии от author1
    search_params = CommentSearchParams(
        is_viewed=False, author_screen_name=["author1"]
    )
    result = await service.get_comments(search_params, page=1, size=20)
    assert result.total == 2
    assert all(
        comment.author_screen_name == "author1" for comment in result.items
    )

    # Тест 3: С фильтром по author_screen_name - должны быть только комментарии от author2
    search_params = CommentSearchParams(
        is_viewed=False, author_screen_name=["author2"]
    )
    result = await service.get_comments(search_params, page=1, size=20)
    assert result.total == 1
    assert result.items[0].author_screen_name == "author2"

    # Тест 4: С фильтром по нескольким авторам
    search_params = CommentSearchParams(
        is_viewed=False, author_screen_name=["author1", "author2"]
    )
    result = await service.get_comments(search_params, page=1, size=20)
    assert result.total == 3
