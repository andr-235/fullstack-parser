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
    service.get_group_posts_count = AsyncMock()
    service.get_post_comments_count = AsyncMock()
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
        mock_vk_service.get_wall_posts.return_value = {
            "items": [sample_post_data],
            "count": 1,
        }

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
        mock_vk_service.get_wall_posts.assert_called_once_with(
            owner_id=-123456789, count=10, offset=0
        )

    @pytest.mark.asyncio
    async def test_parse_group_posts_no_posts(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест парсинга постов группы без результатов"""
        # Настраиваем мок для пустого результата
        mock_vk_service.get_wall_posts.return_value = {"items": [], "count": 0}

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
        mock_vk_service.get_wall_posts.side_effect = Exception("VK API error")

        # Проверяем что исключение пробрасывается
        with pytest.raises(Exception, match="VK API error"):
            await vk_data_parser.parse_group_posts(group_id=123456789)

    @pytest.mark.asyncio
    async def test_parse_post_comments_success(
        self, vk_data_parser, mock_vk_service, sample_comment_data
    ):
        """Тест успешного парсинга комментариев к посту"""
        # Настраиваем мок VK API
        mock_vk_service.get_post_comments.return_value = {
            "items": [sample_comment_data],
            "count": 1,
        }

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
    async def test_parse_post_comments_no_comments(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест парсинга комментариев без результатов"""
        # Настраиваем мок для пустого результата
        mock_vk_service.get_post_comments.return_value = {
            "items": [],
            "count": 0,
        }

        # Вызываем метод
        comments = await vk_data_parser.parse_post_comments(
            post_id=100, owner_id=-123456789
        )

        # Проверяем результат
        assert len(comments) == 0

    @pytest.mark.asyncio
    async def test_parse_user_info_success(
        self, vk_data_parser, mock_vk_service, sample_user_data
    ):
        """Тест успешного парсинга информации о пользователях"""
        # Настраиваем мок VK API
        mock_vk_service.get_users_info.return_value = [sample_user_data]

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
    async def test_parse_user_info_multiple_users(
        self, vk_data_parser, mock_vk_service, sample_user_data
    ):
        """Тест парсинга информации о нескольких пользователях"""
        # Создаем данные для двух пользователей
        user2_data = sample_user_data.copy()
        user2_data["id"] = 98765
        user2_data["first_name"] = "Второй"
        user2_data["last_name"] = "Пользователь"

        # Настраиваем мок VK API
        mock_vk_service.get_users_info.return_value = [
            sample_user_data,
            user2_data,
        ]

        # Вызываем метод
        users = await vk_data_parser.parse_user_info(user_ids=[67890, 98765])

        # Проверяем результат
        assert len(users) == 2
        assert 67890 in users
        assert 98765 in users

    @pytest.mark.asyncio
    async def test_parse_user_info_empty_list(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест парсинга информации с пустым списком пользователей"""
        # Вызываем метод с пустым списком
        users = await vk_data_parser.parse_user_info(user_ids=[])

        # Проверяем результат
        assert len(users) == 0

        # Проверяем что VK API не был вызван
        mock_vk_service.get_users_info.assert_not_called()

    @pytest.mark.asyncio
    async def test_parse_user_info_large_list(
        self, vk_data_parser, mock_vk_service, sample_user_data
    ):
        """Тест парсинга информации с большим количеством пользователей"""
        # Создаем список из 150 пользователей (больше лимита VK API)
        user_ids = list(range(1, 151))
        users_data = []
        for i, user_id in enumerate(
            user_ids[:100]
        ):  # VK API вернет только первые 100
            user_data = sample_user_data.copy()
            user_data["id"] = user_id
            users_data.append(user_data)

        # Настраиваем мок VK API
        mock_vk_service.get_users_info.return_value = users_data

        # Вызываем метод
        users = await vk_data_parser.parse_user_info(user_ids=user_ids)

        # Проверяем что VK API был вызван с правильными параметрами
        mock_vk_service.get_users_info.assert_called_once_with(
            user_ids=user_ids[:100],  # Только первые 100
            fields=["screen_name", "photo_100"],
        )

    @pytest.mark.asyncio
    async def test_parse_group_info_success(
        self, vk_data_parser, mock_vk_service, sample_group_data
    ):
        """Тест успешного парсинга информации о группах"""
        # Настраиваем мок VK API
        mock_vk_service.get_groups_info.return_value = [sample_group_data]

        # Вызываем метод
        groups = await vk_data_parser.parse_group_info(group_ids=[123456789])

        # Проверяем результат
        assert len(groups) == 1
        assert 123456789 in groups
        assert groups[123456789]["id"] == 123456789
        assert groups[123456789]["name"] == "Тестовая Группа"
        assert groups[123456789]["members_count"] == 1000

    @pytest.mark.asyncio
    async def test_parse_group_info_multiple_groups(
        self, vk_data_parser, mock_vk_service, sample_group_data
    ):
        """Тест парсинга информации о нескольких группах"""
        # Создаем данные для двух групп
        group2_data = sample_group_data.copy()
        group2_data["id"] = 987654321
        group2_data["name"] = "Вторая Группа"

        # Настраиваем мок VK API
        mock_vk_service.get_groups_info.return_value = [
            sample_group_data,
            group2_data,
        ]

        # Вызываем метод
        groups = await vk_data_parser.parse_group_info(
            group_ids=[123456789, 987654321]
        )

        # Проверяем результат
        assert len(groups) == 2
        assert 123456789 in groups
        assert 987654321 in groups

    @pytest.mark.asyncio
    async def test_validate_group_access_success(
        self, vk_data_parser, mock_vk_service, sample_post_data
    ):
        """Тест успешной проверки доступа к группе"""
        # Настраиваем мок VK API для успешного доступа
        mock_vk_service.get_wall_posts.return_value = {
            "items": [sample_post_data],
            "count": 1,
        }

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
        mock_vk_service.get_wall_posts.return_value = {"items": [], "count": 0}

        # Вызываем метод
        has_access = await vk_data_parser.validate_group_access(
            group_id=123456789
        )

        # Проверяем результат
        assert has_access == False

    @pytest.mark.asyncio
    async def test_validate_group_access_error(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест проверки доступа к группе при ошибке API"""
        # Настраиваем мок для выброса исключения
        mock_vk_service.get_wall_posts.side_effect = Exception("Access denied")

        # Вызываем метод
        has_access = await vk_data_parser.validate_group_access(
            group_id=123456789
        )

        # Проверяем результат
        assert has_access == False

    @pytest.mark.asyncio
    async def test_get_group_posts_count_success(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест успешного получения количества постов группы"""
        # Настраиваем мок VK API
        mock_vk_service.get_group_posts_count.return_value = 150

        # Вызываем метод
        count = await vk_data_parser.get_group_posts_count(group_id=123456789)

        # Проверяем результат
        assert count == 150
        mock_vk_service.get_group_posts_count.assert_called_once_with(
            123456789
        )

    @pytest.mark.asyncio
    async def test_get_group_posts_count_no_posts(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест получения количества постов для группы без постов"""
        # Настраиваем мок для пустого результата
        mock_vk_service.get_wall_posts.return_value = {"items": [], "count": 0}

        # Вызываем метод
        count = await vk_data_parser.get_group_posts_count(group_id=123456789)

        # Проверяем результат
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_post_comments_count_success(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест успешного получения количества комментариев к посту"""
        # Настраиваем мок VK API
        mock_vk_service.get_post_comments_count.return_value = 75

        # Вызываем метод
        count = await vk_data_parser.get_post_comments_count(
            post_id=100, owner_id=-123456789
        )

        # Проверяем результат
        assert count == 75
        mock_vk_service.get_post_comments_count.assert_called_once_with(
            -123456789, 100
        )

    @pytest.mark.asyncio
    async def test_get_post_comments_count_no_comments(
        self, vk_data_parser, mock_vk_service
    ):
        """Тест получения количества комментариев для поста без комментариев"""
        # Настраиваем мок для пустого результата
        mock_vk_service.get_post_comments_count.return_value = 0

        # Вызываем метод
        count = await vk_data_parser.get_post_comments_count(
            post_id=100, owner_id=-123456789
        )

        # Проверяем результат
        assert count == 0
        mock_vk_service.get_post_comments_count.assert_called_once_with(-123456789, 100)

    def test_parser_initialization(self, vk_data_parser, mock_vk_service):
        """Тест инициализации парсера"""
        # Проверяем что парсер правильно инициализирован
        assert vk_data_parser.vk_service == mock_vk_service
        assert vk_data_parser.db is None  # По умолчанию None
        assert hasattr(vk_data_parser, "parse_group_posts")
        assert hasattr(vk_data_parser, "parse_post_comments")
        assert hasattr(vk_data_parser, "parse_user_info")
        assert hasattr(vk_data_parser, "parse_group_info")

    def test_parser_initialization_with_db(self, mock_vk_service):
        """Тест инициализации парсера с базой данных"""
        from unittest.mock import MagicMock

        # Создаем мок базы данных
        mock_db = MagicMock()

        # Создаем парсер с базой данных
        parser = VKDataParser(mock_vk_service, mock_db)

        # Проверяем что база данных установлена
        assert parser.db == mock_db

    @pytest.mark.asyncio
    async def test_api_error_handling(self, vk_data_parser, mock_vk_service):
        """Тест обработки ошибок VK API во всех методах"""
        # Настраиваем мок для выброса исключения
        mock_vk_service.get_wall_posts.side_effect = Exception(
            "VK API unavailable"
        )
        mock_vk_service.get_post_comments.side_effect = Exception(
            "VK API unavailable"
        )
        mock_vk_service.get_users_info.side_effect = Exception(
            "VK API unavailable"
        )
        mock_vk_service.get_groups_info.side_effect = Exception(
            "VK API unavailable"
        )

        # Проверяем что все методы правильно обрабатывают ошибки
        with pytest.raises(Exception, match="VK API unavailable"):
            await vk_data_parser.parse_group_posts(group_id=123456789)

        with pytest.raises(Exception, match="VK API unavailable"):
            await vk_data_parser.parse_post_comments(
                post_id=100, owner_id=-123456789
            )

        with pytest.raises(Exception, match="VK API unavailable"):
            await vk_data_parser.parse_user_info(user_ids=[67890])

        with pytest.raises(Exception, match="VK API unavailable"):
            await vk_data_parser.parse_group_info(group_ids=[123456789])

    @pytest.mark.asyncio
    async def test_group_id_conversion(
        self, vk_data_parser, mock_vk_service, sample_post_data
    ):
        """Тест правильного преобразования ID группы в owner_id"""
        # Настраиваем мок VK API
        mock_vk_service.get_wall_posts.return_value = {
            "items": [sample_post_data],
            "count": 1,
        }

        # Вызываем метод с положительным ID группы
        posts = await vk_data_parser.parse_group_posts(group_id=123456789)

        # Проверяем что VK API был вызван с правильным owner_id (отрицательным)
        mock_vk_service.get_wall_posts.assert_called_once_with(
            owner_id=-123456789,  # Преобразовано в отрицательное значение
            count=10,
            offset=0,
        )
