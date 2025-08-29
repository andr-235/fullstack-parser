"""
Тесты для VKDataParser

Тестирует все основные методы сервиса парсинга данных из VK API
с использованием моков для изоляции от внешних зависимостей.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.services.vk_data_parser import VKDataParser
from app.services.vk_api_service import VKAPIService


@pytest.fixture
def mock_vk_service():
    """Фикстура для мок VKAPIService"""
    service = AsyncMock(spec=VKAPIService)
    # Добавляем методы, которые используются в тестах
    service.get_group_posts = AsyncMock()
    service.get_post_comments = AsyncMock()
    service.get_user_info = AsyncMock()
    service.get_group_info = AsyncMock()
    return service


@pytest.fixture
def vk_data_parser(mock_vk_service):
    """Фикстура для VKDataParser"""
    return VKDataParser(mock_vk_service)


@pytest.fixture
def sample_post_data():
    """Фикстура для примера данных поста VK"""
    return {
        "id": 100,
        "owner_id": -123456789,
        "from_id": 123456789,
        "date": 1705320000,  # 2024-01-15 12:00:00 UTC
        "text": "Тестовый пост для парсинга",
        "comments": {"count": 5},
        "likes": {"count": 10},
        "reposts": {"count": 2},
        "views": {"count": 100},
    }


@pytest.fixture
def sample_comment_data():
    """Фикстура для примера данных комментария VK"""
    return {
        "id": 1,
        "post_id": 100,
        "from_id": 67890,
        "date": 1705323600,  # 2024-01-15 13:00:00 UTC
        "text": "Тестовый комментарий",
        "likes": {"count": 3},
        "thread": {"count": 0},
        "attachments": [],
    }


@pytest.fixture
def sample_user_data():
    """Фикстура для примера данных пользователя VK"""
    return {
        "id": 67890,
        "first_name": "Тестовый",
        "last_name": "Пользователь",
        "screen_name": "test_user",
        "photo_100": "https://example.com/photo.jpg",
    }


@pytest.fixture
def sample_group_data():
    """Фикстура для примера данных группы VK"""
    return {
        "id": 123456789,
        "name": "Тестовая Группа",
        "screen_name": "test_group",
        "members_count": 1000,
        "photo_100": "https://example.com/group_photo.jpg",
    }


class TestVKDataParser:
    """Тесты для VKDataParser"""

    @pytest.mark.asyncio
    async def test_parse_group_posts_success(
        self, vk_data_parser, mock_vk_service, sample_post_data
    ):
        """Тест успешного парсинга постов группы"""
        # Настраиваем мок VK API
        mock_vk_service.get_group_posts.return_value = [sample_post_data]

        # Вызываем метод
        posts = await vk_data_parser.parse_group_posts(
            group_id=123456789, limit=10, offset=0
        )

        # Проверяем результат
        assert len(posts) == 1
        assert posts[0]["id"] == 100
        assert posts[0]["owner_id"] == -123456789
        assert posts[0]["text"] == "Тестовый пост для парсинга"

        # Проверяем что VK API был вызван с правильными параметрами
        mock_vk_service.get_group_posts.assert_called_once_with(
            group_id=123456789, count=10, offset=0
        )

    @pytest.mark.asyncio
    async def test_parse_group_posts_no_posts(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест парсинга постов группы без результатов"""
        # Настраиваем мок для пустого результата
        mock_vk_service.get_group_posts.return_value = []

        # Вызываем метод
        posts = await vk_data_parser.parse_group_posts(group_id=123456789)

        # Проверяем результат
        assert len(posts) == 0

    @pytest.mark.asyncio
    async def test_parse_group_posts_api_error(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест обработки ошибки VK API при парсинге постов"""
        # Настраиваем мок для выброса исключения
        mock_vk_service.get_group_posts.side_effect = Exception("VK API error")

        # Проверяем что исключение пробрасывается
        with pytest.raises(Exception, match="VK API error"):
            await vk_data_parser.parse_group_posts(group_id=123456789)

    @pytest.mark.asyncio
    async def test_parse_post_comments_success(
        self, vk_data_parser, mock_vk_service, sample_comment_data
    ):
        """Тест успешного парсинга комментариев к посту"""
        # Настраиваем мок VK API
        mock_vk_service.get_post_comments.return_value = [sample_comment_data]

        # Вызываем метод
        comments = await vk_data_parser.parse_post_comments(
            post_id=100, owner_id=-123456789, limit=10, offset=0
        )

        # Проверяем результат
        assert len(comments) == 1
        assert comments[0]["id"] == 1
        assert comments[0]["post_id"] == 100
        assert comments[0]["text"] == "Тестовый комментарий"

        # Проверяем что VK API был вызван правильно
        mock_vk_service.get_post_comments.assert_called_once_with(
            owner_id=-123456789, post_id=100, count=10, offset=0
        )

    @pytest.mark.asyncio
    async def test_parse_user_info_success(
        self, vk_data_parser, mock_vk_service, sample_user_data
    ):
        """Тест успешного парсинга информации о пользователях"""
        # Настраиваем мок VK API
        mock_vk_service.get_user_info.return_value = sample_user_data

        # Вызываем метод
        users = await vk_data_parser.parse_user_info(user_ids=[67890])

        # Проверяем результат
        assert len(users) == 1
        assert 67890 in users
        assert users[67890]["id"] == 67890
        assert users[67890]["first_name"] == "Тестовый"
        assert users[67890]["last_name"] == "Пользователь"
        assert users[67890]["screen_name"] == "test_user"

    @pytest.mark.asyncio
    async def test_parse_group_info_success(
        self, vk_data_parser, mock_vk_service, sample_group_data
    ):
        """Тест успешного парсинга информации о группах"""
        # Настраиваем мок VK API
        mock_vk_service.get_group_info.return_value = sample_group_data

        # Вызываем метод
        groups = await vk_data_parser.parse_group_info(group_ids=[123456789])

        # Проверяем результат
        assert len(groups) == 1
        assert 123456789 in groups
        assert groups[123456789]["id"] == 123456789
        assert groups[123456789]["name"] == "Тестовая Группа"
        assert groups[123456789]["members_count"] == 1000

    @pytest.mark.asyncio
    async def test_validate_group_access_success(
        self, vk_data_parser, mock_vk_service, sample_post_data
    ):
        """Тест успешной проверки доступа к группе"""
        # Настраиваем мок VK API для успешного доступа
        mock_vk_service.get_group_posts.return_value = [sample_post_data]

        # Вызываем метод
        has_access = await vk_data_parser.validate_group_access(
            group_id=123456789
        )

        # Проверяем результат
        assert has_access == True

    @pytest.mark.asyncio
    async def test_validate_group_access_denied(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест проверки доступа к группе без доступа"""
        # Настраиваем мок VK API для отказа в доступе
        mock_vk_service.get_group_posts.return_value = []

        # Вызываем метод
        has_access = await vk_data_parser.validate_group_access(
            group_id=123456789
        )

        # Проверяем результат
        assert has_access == False

    @pytest.mark.asyncio
    async def test_get_group_posts_count_success(
        self, vk_data_parser, mock_vk_service, sample_post_data
    ):
        """Тест успешного получения количества постов группы"""
        # Настраиваем мок VK API
        mock_vk_service.get_group_posts.return_value = [sample_post_data]

        # Вызываем метод
        count = await vk_data_parser.get_group_posts_count(group_id=123456789)

        # Проверяем что метод был вызван
        assert isinstance(count, int)

    @pytest.mark.asyncio
    async def test_get_post_comments_count_success(
        self, vk_data_parser, mock_vk_service, sample_comment_data
    ):
        """Тест успешного получения количества комментариев к посту"""
        # Настраиваем мок VK API
        mock_vk_service.get_post_comments.return_value = [sample_comment_data]

        # Вызываем метод
        count = await vk_data_parser.get_post_comments_count(
            post_id=100, owner_id=-123456789
        )

        # Проверяем что метод был вызван
        assert isinstance(count, int)

    def test_parser_initialization(self, vk_data_parser, mock_vk_service):
        """Тест инициализации парсера"""
        # Проверяем что парсер правильно инициализирован
        assert vk_data_parser.vk_service == mock_vk_service
        assert vk_data_parser.db is None  # По умолчанию None
        assert hasattr(vk_data_parser, "parse_group_posts")
        assert hasattr(vk_data_parser, "parse_post_comments")
        assert hasattr(vk_data_parser, "parse_user_info")
        assert hasattr(vk_data_parser, "parse_group_info")

    @pytest.mark.asyncio
    async def test_group_id_conversion(
        self, vk_data_parser, mock_vk_service, sample_post_data
    ):
        """Тест правильного преобразования ID группы в owner_id"""
        # Настраиваем мок VK API
        mock_vk_service.get_group_posts.return_value = [sample_post_data]

        # Вызываем метод с положительным ID группы
        posts = await vk_data_parser.parse_group_posts(group_id=123456789)

        # Проверяем что VK API был вызван с правильным group_id
        mock_vk_service.get_group_posts.assert_called_once_with(
            group_id=123456789, count=10, offset=0
        )
