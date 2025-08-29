"""
Тесты для StatsService

Тестирует все основные методы сервиса статистики
с использованием моков для изоляции от базы данных.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.services.stats_service import StatsService
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost


@pytest.fixture
def mock_db():
    """Фикстура для мок базы данных"""
    return AsyncMock()


@pytest.fixture
def stats_service(mock_db):
    """Фикстура для StatsService"""
    return StatsService(mock_db)


@pytest.fixture
def sample_vk_group():
    """Фикстура для примера VKGroup"""
    group = MagicMock(spec=VKGroup)
    group.id = 1
    group.vk_id = 123456789
    group.name = "Тестовая Группа"
    group.screen_name = "test_group"
    group.is_active = True
    group.member_count = 1000
    return group


@pytest.fixture
def sample_vk_post():
    """Фикстура для примера VKPost"""
    post = MagicMock(spec=VKPost)
    post.id = 1
    post.vk_id = 100
    post.group_id = 1
    post.created_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    return post


@pytest.fixture
def sample_comments():
    """Фикстура для списка комментариев"""
    comments = []
    for i in range(5):
        comment = MagicMock(spec=VKComment)
        comment.id = i + 1
        comment.text = f"Комментарий {i + 1}"
        comment.is_viewed = i % 2 == 0  # Каждый второй просмотрен
        comment.is_archived = i % 3 == 0  # Каждый третий архивирован
        comment.is_processed = True
        comment.matched_keywords_count = i + 1
        comment.post = MagicMock(spec=VKPost)
        comment.post.group_id = 1
        comment.created_at = datetime(
            2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc
        )
        comments.append(comment)
    return comments


class TestStatsService:
    """Тесты для StatsService"""

    @pytest.mark.asyncio
    async def test_get_global_stats_success(
        self, stats_service, mock_db, sample_vk_group, sample_comments
    ):
        """Тест успешного получения глобальной статистики"""
        # Настраиваем моки для различных запросов
        mock_groups_result = MagicMock()
        mock_groups_result.scalars.return_value.all.return_value = [
            sample_vk_group
        ]

        mock_comments_result = MagicMock()
        mock_comments_result.scalars.return_value.all.return_value = (
            sample_comments
        )

        mock_posts_result = MagicMock()
        mock_posts_result.scalars.return_value.all.return_value = [
            MagicMock()
        ] * 10

        mock_keywords_result = MagicMock()
        mock_keywords_result.scalars.return_value.all.return_value = [
            MagicMock()
        ] * 5

        # Настраиваем последовательные вызовы execute
        mock_db.execute.side_effect = [
            mock_groups_result,  # groups query
            mock_comments_result,  # comments query
            mock_posts_result,  # posts query
            mock_keywords_result,  # keywords query
        ]

        # Вызываем метод
        stats = await stats_service.get_global_stats()

        # Проверяем структуру результата
        assert isinstance(stats, dict)
        assert "overview" in stats
        assert "comments" in stats
        assert "engagement" in stats
        assert "keywords" in stats
        assert "generated_at" in stats

        # Проверяем значения
        assert stats["overview"]["total_groups"] == 1
        assert stats["overview"]["active_groups"] == 1
        assert stats["overview"]["total_comments"] == 5
        assert stats["overview"]["total_posts"] == 10
        assert stats["overview"]["total_keywords"] == 5

        # Проверяем метрики комментариев
        assert stats["comments"]["total"] == 5
        assert stats["comments"]["viewed"] == 3  # 0, 2, 4 индексы
        assert stats["comments"]["archived"] == 2  # 0, 3 индексы
        assert stats["comments"]["processed"] == 5

    @pytest.mark.asyncio
    async def test_get_global_stats_empty_database(
        self, stats_service, mock_db
    ):
        """Тест глобальной статистики для пустой базы данных"""
        # Настраиваем моки для пустых результатов
        mock_empty_result = MagicMock()
        mock_empty_result.scalars.return_value.all.return_value = []

        # Все запросы возвращают пустые результаты
        mock_db.execute.side_effect = [mock_empty_result] * 4

        # Вызываем метод
        stats = await stats_service.get_global_stats()

        # Проверяем что все счетчики равны 0
        assert stats["overview"]["total_groups"] == 0
        assert stats["overview"]["total_comments"] == 0
        assert stats["overview"]["total_posts"] == 0
        assert stats["overview"]["total_keywords"] == 0

        # Проверяем что проценты равны 0
        assert stats["comments"]["view_rate"] == 0
        assert stats["comments"]["archive_rate"] == 0
        assert stats["comments"]["processing_rate"] == 0

    @pytest.mark.asyncio
    async def test_get_group_stats_success(
        self, stats_service, mock_db, sample_vk_group, sample_comments
    ):
        """Тест успешного получения статистики группы"""
        # Настраиваем моки
        mock_group_result = MagicMock()
        mock_group_result.scalar_one_or_none.return_value = sample_vk_group

        mock_posts_result = MagicMock()
        mock_posts_result.scalars.return_value.all.return_value = [
            MagicMock()
        ] * 8

        mock_comments_result = MagicMock()
        mock_comments_result.scalars.return_value.all.return_value = (
            sample_comments
        )

        # Настраиваем последовательные вызовы
        mock_db.execute.side_effect = [
            mock_group_result,  # group query
            mock_posts_result,  # posts query
            mock_comments_result,  # comments query
        ]

        # Вызываем метод
        stats = await stats_service.get_group_stats(group_id=123456789)

        # Проверяем структуру результата
        assert isinstance(stats, dict)
        assert "group_info" in stats
        assert "posts" in stats
        assert "comments" in stats
        assert "engagement" in stats

        # Проверяем информацию о группе
        assert stats["group_info"]["id"] == 1
        assert stats["group_info"]["vk_id"] == 123456789
        assert stats["group_info"]["name"] == "Тестовая Группа"
        assert stats["group_info"]["is_active"] == True

        # Проверяем статистику постов и комментариев
        assert stats["posts"]["total"] == 8
        assert stats["comments"]["total"] == 5
        assert stats["engagement"]["avg_comments_per_post"] == 0.63  # 5/8

    @pytest.mark.asyncio
    async def test_get_group_stats_not_found(self, stats_service, mock_db):
        """Тест получения статистики для несуществующей группы"""
        # Настраиваем мок для None результата
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Проверяем что исключение пробрасывается
        with pytest.raises(ValueError, match="Group with ID 999 not found"):
            await stats_service.get_group_stats(group_id=999)

    @pytest.mark.asyncio
    async def test_get_keyword_stats_success(self, stats_service, mock_db):
        """Тест успешного получения статистики по ключевым словам"""
        # Создаем моки для ключевых слов
        keywords = []
        for i in range(3):
            keyword = MagicMock(spec=Keyword)
            keyword.id = i + 1
            keyword.word = f"ключевое_слово_{i + 1}"
            keyword.category = f"Категория {i + 1}"
            keyword.is_active = i % 2 == 0  # Каждый второй активен
            keyword.description = f"Описание {i + 1}"
            keywords.append(keyword)

        # Настраиваем моки
        mock_keywords_result = MagicMock()
        mock_keywords_result.scalars.return_value.all.return_value = keywords

        # Мок для поиска комментариев (будет вызван в _get_all_comments)
        mock_comments_result = MagicMock()
        mock_comments_result.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [
            mock_keywords_result,  # keywords query
            mock_comments_result,  # comments query for each keyword
            mock_comments_result,
            mock_comments_result,
        ]

        # Вызываем метод
        keyword_stats = await stats_service.get_keyword_stats()

        # Проверяем результат
        assert isinstance(keyword_stats, list)
        assert len(keyword_stats) == 3

        # Проверяем структуру каждого элемента
        for stat in keyword_stats:
            assert "keyword_id" in stat
            assert "word" in stat
            assert "category" in stat
            assert "is_active" in stat
            assert "comments_count" in stat
            assert "description" in stat

        # Проверяем сортировку по количеству комментариев (убывание)
        assert (
            keyword_stats[0]["comments_count"]
            >= keyword_stats[1]["comments_count"]
        )

    @pytest.mark.asyncio
    async def test_get_recent_activity_success(
        self, stats_service, mock_db, sample_comments
    ):
        """Тест успешного получения статистики недавней активности"""
        # Настраиваем моки
        mock_recent_comments_result = MagicMock()
        mock_recent_comments_result.scalars.return_value.all.return_value = (
            sample_comments[:3]
        )

        mock_recent_posts_result = MagicMock()
        mock_recent_posts_result.scalars.return_value.all.return_value = [
            MagicMock()
        ] * 2

        mock_viewed_comments_result = MagicMock()
        mock_viewed_comments_result.scalars.return_value.all.return_value = (
            sample_comments[:2]
        )

        # Настраиваем последовательные вызовы
        mock_db.execute.side_effect = [
            mock_recent_comments_result,  # recent comments
            mock_recent_posts_result,  # recent posts
            mock_viewed_comments_result,  # viewed comments
        ]

        # Вызываем метод
        activity = await stats_service.get_recent_activity(hours=24)

        # Проверяем структуру результата
        assert isinstance(activity, dict)
        assert "period_hours" in activity
        assert "recent_comments" in activity
        assert "recent_posts" in activity
        assert "viewed_comments" in activity
        assert "comments_per_hour" in activity
        assert "posts_per_hour" in activity
        assert "generated_at" in activity

        # Проверяем значения
        assert activity["period_hours"] == 24
        assert activity["recent_comments"] == 3
        assert activity["recent_posts"] == 2
        assert activity["viewed_comments"] == 2
        assert activity["comments_per_hour"] == 0.13  # 3/24
        assert activity["posts_per_hour"] == 0.08  # 2/24

    @pytest.mark.asyncio
    async def test_get_recent_activity_no_activity(
        self, stats_service, mock_db
    ):
        """Тест статистики недавней активности при отсутствии активности"""
        # Настраиваем моки для пустых результатов
        mock_empty_result = MagicMock()
        mock_empty_result.scalars.return_value.all.return_value = []

        # Все запросы возвращают пустые результаты
        mock_db.execute.side_effect = [mock_empty_result] * 3

        # Вызываем метод
        activity = await stats_service.get_recent_activity(hours=1)

        # Проверяем что все счетчики равны 0
        assert activity["recent_comments"] == 0
        assert activity["recent_posts"] == 0
        assert activity["viewed_comments"] == 0
        assert activity["comments_per_hour"] == 0
        assert activity["posts_per_hour"] == 0

    @pytest.mark.asyncio
    async def test_database_error_handling(self, stats_service, mock_db):
        """Тест обработки ошибок базы данных"""
        # Настраиваем мок для выброса исключения
        mock_db.execute.side_effect = Exception("Database connection error")

        # Проверяем что исключения пробрасываются для всех методов
        with pytest.raises(Exception, match="Database connection error"):
            await stats_service.get_global_stats()

        with pytest.raises(Exception, match="Database connection error"):
            await stats_service.get_group_stats(group_id=1)

        with pytest.raises(Exception, match="Database connection error"):
            await stats_service.get_keyword_stats()

        with pytest.raises(Exception, match="Database connection error"):
            await stats_service.get_recent_activity(hours=1)

    def test_stats_service_initialization(self, stats_service, mock_db):
        """Тест инициализации сервиса статистики"""
        # Проверяем что сервис правильно инициализирован
        assert stats_service.db == mock_db
        assert hasattr(stats_service, "get_global_stats")
        assert hasattr(stats_service, "get_group_stats")
        assert hasattr(stats_service, "get_keyword_stats")
        assert hasattr(stats_service, "get_recent_activity")

    @pytest.mark.asyncio
    async def test_get_global_stats_calculations(self, stats_service, mock_db):
        """Тест правильности расчетов в глобальной статистике"""
        # Создаем тестовые данные с известными значениями
        comments = []
        for i in range(10):
            comment = MagicMock(spec=VKComment)
            comment.is_viewed = i < 6  # 6 просмотренных
            comment.is_archived = i < 3  # 3 архивированных
            comment.is_processed = i < 8  # 8 обработанных
            comment.matched_keywords_count = i % 3  # 0, 1, 2, 0, 1, 2...
            comment.post = MagicMock(spec=VKPost)
            comment.post.group_id = 1
            comments.append(comment)

        # Настраиваем моки
        mock_groups_result = MagicMock()
        mock_groups_result.scalars.return_value.all.return_value = [
            MagicMock()
        ] * 2

        mock_comments_result = MagicMock()
        mock_comments_result.scalars.return_value.all.return_value = comments

        mock_posts_result = MagicMock()
        mock_posts_result.scalars.return_value.all.return_value = [
            MagicMock()
        ] * 5

        mock_keywords_result = MagicMock()
        mock_keywords_result.scalars.return_value.all.return_value = [
            MagicMock()
        ] * 3

        mock_db.execute.side_effect = [
            mock_groups_result,
            mock_comments_result,
            mock_posts_result,
            mock_keywords_result,
        ]

        # Вызываем метод
        stats = await stats_service.get_global_stats()

        # Проверяем расчеты
        assert stats["comments"]["viewed"] == 6
        assert stats["comments"]["archived"] == 3
        assert stats["comments"]["processed"] == 8
        assert stats["comments"]["view_rate"] == 60.0  # 6/10 * 100
        assert stats["comments"]["archive_rate"] == 30.0  # 3/10 * 100
        assert stats["comments"]["processing_rate"] == 80.0  # 8/10 * 100

        # Проверяем расчеты вовлеченности
        assert stats["engagement"]["avg_comments_per_group"] == 5.0  # 10/2
        assert stats["engagement"]["avg_comments_per_post"] == 2.0  # 10/5
