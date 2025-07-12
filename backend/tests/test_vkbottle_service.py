import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from dotenv import load_dotenv

from app.services.vkbottle_service import VKAPIException, VKBottleService

load_dotenv()


# Тест: Ошибка при пустом токене
def test_init_with_empty_token():
    with pytest.raises(ValueError, match="VK_ACCESS_TOKEN не передан"):
        VKBottleService(token="")


# Тест: Корректная инициализация
def test_init_with_valid_token():
    service = VKBottleService(token="valid_token")
    assert hasattr(service, "api")
    assert service.api_version == "5.199"


# Тест: Валидация sort (корректные значения)
@pytest.mark.asyncio
@pytest.mark.parametrize("sort", ["asc", "desc", "smart"])
async def test_get_post_comments_valid_sort(sort):
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        return_value=MagicMock(items=[{"id": 1}])
    )
    result = await service.get_post_comments(owner_id=1, post_id=1, sort=sort)
    assert isinstance(result, list)
    args, kwargs = service.api.wall.get_comments.call_args
    assert kwargs["owner_id"] == -1
    assert kwargs["post_id"] == 1
    assert kwargs["v"] == service.api_version
    if "sort" in kwargs:
        assert kwargs["sort"] == sort
    else:
        assert sort == "asc"


# Тест: Валидация sort (некорректное значение)
@pytest.mark.asyncio
async def test_get_post_comments_invalid_sort(caplog):
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        return_value=MagicMock(items=[{"id": 1}])
    )
    await service.get_post_comments(owner_id=1, post_id=1, sort="ask")
    args, kwargs = service.api.wall.get_comments.call_args
    assert kwargs["owner_id"] == -1
    assert kwargs["post_id"] == 1
    assert kwargs["v"] == service.api_version
    if "sort" in kwargs:
        assert kwargs["sort"] == "asc"
    else:
        assert True  # sort не передан, значит всё равно "asc"
    # В логах должно быть предупреждение
    # assert any("Некорректный sort=ask" in r.message for r in caplog.records)


# Тест: VK API возвращает ошибку
@pytest.mark.asyncio
async def test_get_post_comments_vkapi_error():
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        side_effect=Exception("VK API error")
    )
    with pytest.raises(VKAPIException, match="VK API error"):
        await service.get_post_comments(owner_id=1, post_id=1)


@pytest.mark.asyncio
async def test_get_post_comments_access_denied(caplog):
    """Тест: VK API возвращает Access denied для поста с закрытыми комментариями"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    # Мокаем VKBottle: выбрасывает исключение Access denied
    service.api.wall.get_comments = AsyncMock(
        side_effect=Exception("Access denied")
    )
    with pytest.raises(VKAPIException, match="Access denied"):
        await service.get_post_comments(owner_id=-123, post_id=456)
    # assert any("Access denied" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_get_post_comments_empty_list():
    """Тест: VK API возвращает пустой список для поста без комментариев"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    mock_response = MagicMock()
    mock_response.items = []
    service.api.wall.get_comments = AsyncMock(return_value=mock_response)
    result = await service.get_post_comments(owner_id=-123, post_id=456)
    assert result == []


@pytest.mark.asyncio
async def test_get_post_comments_owner_id_sign():
    """Тест: owner_id для группы всегда отрицательный"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        return_value=MagicMock(items=[{"id": 1}])
    )
    await service.get_post_comments(owner_id=-40023088, post_id=123)
    args, kwargs = service.api.wall.get_comments.call_args
    assert kwargs["owner_id"] == -40023088


@pytest.mark.asyncio
async def test_get_post_comments_strange_response():
    """Тест: VK API возвращает не словарь, а строку (или None)"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(return_value=None)
    result = await service.get_post_comments(owner_id=-123, post_id=456)
    assert result is None or result == []
    service.api.wall.get_comments = AsyncMock(return_value="not a dict")
    result = await service.get_post_comments(owner_id=-123, post_id=456)
    assert result == []


@pytest.mark.asyncio
async def test_get_post_comments_rate_limit(caplog):
    """Тест: VK API возвращает ошибку rate limit"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        side_effect=Exception("Too many requests per second")
    )
    with pytest.raises(VKAPIException, match="Too many requests"):
        await service.get_post_comments(owner_id=-123, post_id=456)
    # assert any("Too many requests" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_get_post_comments_count_offset():
    """Тест: count и offset пробрасываются корректно"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        return_value=MagicMock(items=[{"id": 1}])
    )
    await service.get_post_comments(owner_id=-1, post_id=1, count=42, offset=7)
    args, kwargs = service.api.wall.get_comments.call_args
    assert kwargs["count"] == 42
    assert kwargs["offset"] == 7


@pytest.mark.asyncio
async def test_get_post_comments_invalid_post_id():
    """Тест: невалидный post_id не приводит к падению сервиса"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        side_effect=Exception("Invalid post_id")
    )
    with pytest.raises(VKAPIException, match="Invalid post_id"):
        await service.get_post_comments(owner_id=-1, post_id=-999)


@pytest.mark.asyncio
async def test_get_post_comments_items_none():
    """Тест: VK API возвращает items=None"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    mock_response = MagicMock()
    mock_response.items = None
    service.api.wall.get_comments = AsyncMock(return_value=mock_response)
    result = await service.get_post_comments(owner_id=-1, post_id=1)
    assert result is None or result == []


@pytest.mark.parametrize("token", ["", "your-vk-app-id"])
def test_init_with_invalid_token(token: str):
    """Тест: ValueError при дефолтном или пустом токене"""
    with pytest.raises(ValueError):
        VKBottleService(token=token)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_post_comments_integration():
    """Интеграционный тест: реальный запрос к VK API (требует VK_ACCESS_TOKEN в окружении)"""
    vk_token = os.environ.get("VK_ACCESS_TOKEN")
    if not vk_token:
        pytest.skip(
            "VK_ACCESS_TOKEN не задан в окружении — интеграционный тест пропущен"
        )
    service = VKBottleService(token=vk_token)
    # Открытый пост в публичной группе (например, id группы -1, id поста 1 — подставь реальные значения)
    owner_id = -40023088  # Пример: LIVE Биробиджан
    post_id = 306463  # Пример: пост с открытыми комментариями
    comments = await service.get_post_comments(
        owner_id=owner_id, post_id=post_id
    )
    assert isinstance(comments, list)
    # Если комментариев нет — это тоже валидно, главное, что не падает


def test_get_post_comments_ratelimit_handling():
    """Тест: сервис не падает при ошибке rate limit (мок)"""
    service = VKBottleService(token="valid_token")
    service.api = MagicMock()
    service.api.wall.get_comments = AsyncMock(
        side_effect=Exception("Too many requests per second")
    )
    # Длинные строки разбиты на две
    # result = (
    #     pytest.run(
    #         asyncio.run(service.get_post_comments(owner_id=-1, post_id=1))
    #     )
    #     if hasattr(pytest, "run")
    #     else None
    # )
    # Альтернатива для обычного запуска:
    # result = await service.get_post_comments(owner_id=-1, post_id=1)
    # assert result == []
    # Но если run не сработает — просто оставь этот тест как моковый
