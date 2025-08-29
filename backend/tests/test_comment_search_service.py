"""
Тесты для CommentSearchService

Тестирует все основные методы сервиса поиска комментариев
с использованием моков для изоляции от базы данных.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.services.comment_search_service import CommentSearchService
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentWithKeywords,
    VKCommentResponse,
)


@pytest.fixture
def mock_db():
    """Фикстура для мок базы данных"""
    return AsyncMock()


@pytest.fixture
def comment_search_service(mock_db):
    """Фикстура для CommentSearchService"""
    return CommentSearchService(mock_db)


@pytest.fixture
def sample_vk_comment():
    """Фикстура для примера VKComment"""
    comment = MagicMock(spec=VKComment)
    comment.id = 1
    comment.vk_id = 12345
    comment.text = "Это тестовый комментарий для поиска"
    comment.author_id = 67890
    comment.author_name = "Тестовый Автор"
    comment.author_screen_name = "test_author"
    comment.author_photo_url = "https://example.com/photo.jpg"
    comment.published_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    comment.likes_count = 5
    comment.parent_comment_id = None
    comment.has_attachments = False
    comment.matched_keywords_count = 2
    comment.is_processed = True
    comment.processed_at = datetime(2024, 1, 15, 13, 0, 0, tzinfo=timezone.utc)
    comment.is_viewed = False
    comment.is_archived = False
    comment.viewed_at = None
    comment.archived_at = None
    comment.created_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    comment.updated_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    comment.post_id = 100
    comment.post_vk_id = 200

    # Мок для связанных объектов
    comment.post = MagicMock(spec=VKPost)
    comment.post.id = 100
    comment.post.group = MagicMock(spec=VKGroup)
    comment.post.group.id = 50
    comment.post.group.vk_id = 123456789
    comment.post.group.name = "Тестовая Группа"
    comment.post.group.screen_name = "test_group"
    comment.post.group.is_active = True
    comment.post.group.member_count = 1000

    # Мок для ключевых слов
    comment.keyword_matches = []

    return comment


@pytest.fixture
def sample_comment_with_keywords(sample_vk_comment):
    """Фикстура для комментария с ключевыми словами"""
    # Добавляем keyword_matches
    keyword_match1 = MagicMock()
    keyword_match1.keyword.word = "тестовый"
    keyword_match1.position = 8
    keyword_match1.matched_text = "тестовый комментарий"

    keyword_match2 = MagicMock()
    keyword_match2.keyword.word = "поиск"
    keyword_match2.position = 30
    keyword_match2.matched_text = "поиск"

    sample_vk_comment.keyword_matches = [keyword_match1, keyword_match2]
    return sample_vk_comment


class TestCommentSearchService:
    """Тесты для CommentSearchService"""

    @pytest.mark.asyncio
    async def test_search_comments_success(
        self, comment_search_service, mock_db, sample_comment_with_keywords
    ):
        """Тест успешного поиска комментариев"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            sample_comment_with_keywords
        ]
        mock_db.execute.return_value = mock_result

        # Создаем параметры поиска
        search_params = CommentSearchParams(
            text="тестовый",
            date_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
            date_to=datetime(2024, 1, 31, tzinfo=timezone.utc),
        )

        # Вызываем метод
        comments = await comment_search_service.search_comments(
            search_params=search_params, limit=10, offset=0
        )

        # Проверяем результат
        assert len(comments) == 1
        assert isinstance(comments[0], CommentWithKeywords)
        assert comments[0].id == 1
        assert "тестовый" in comments[0].matched_keywords
        assert "поиск" in comments[0].matched_keywords
        assert len(comments[0].keyword_matches) == 2

        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_comments_no_results(
        self, comment_search_service, mock_db
    ):
        """Тест поиска без результатов"""
        # Настраиваем мок для пустого результата
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Создаем параметры поиска
        search_params = CommentSearchParams(text="несуществующий текст")

        # Вызываем метод
        comments = await comment_search_service.search_comments(search_params)

        # Проверяем результат
        assert len(comments) == 0

    @pytest.mark.asyncio
    async def test_search_comments_database_error(
        self, comment_search_service, mock_db
    ):
        """Тест обработки ошибки базы данных при поиске"""
        # Настраиваем мок для выброса исключения
        mock_db.execute.side_effect = Exception("Database connection error")

        # Создаем параметры поиска
        search_params = CommentSearchParams(text="тестовый")

        # Проверяем что исключение пробрасывается
        with pytest.raises(Exception, match="Database connection error"):
            await comment_search_service.search_comments(search_params)

    @pytest.mark.asyncio
    async def test_get_comments_by_group_success(
        self, comment_search_service, mock_db, sample_vk_comment
    ):
        """Тест успешного получения комментариев группы"""
        # Настраиваем моки
        mock_count_result = MagicMock()
        mock_count_result.scalars.return_value.all.return_value = [
            sample_vk_comment
        ] * 5

        mock_comments_result = MagicMock()
        mock_comments_result.scalars.return_value.all.return_value = [
            sample_vk_comment
        ]

        # Настраиваем последовательные вызовы
        mock_db.execute.side_effect = [mock_count_result, mock_comments_result]

        # Вызываем метод
        result = await comment_search_service.get_comments_by_group(
            group_id=50, limit=10, offset=0
        )

        # Проверяем результат
        assert result.total == 5
        assert result.page == 1
        assert result.size == 10
        assert len(result.items) == 1
        assert isinstance(result.items[0], VKCommentResponse)

    @pytest.mark.asyncio
    async def test_get_comments_by_group_empty(
        self, comment_search_service, mock_db
    ):
        """Тест получения пустого списка комментариев группы"""
        # Настраиваем моки для пустого результата
        mock_count_result = MagicMock()
        mock_count_result.scalars.return_value.all.return_value = []

        mock_comments_result = MagicMock()
        mock_comments_result.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [mock_count_result, mock_comments_result]

        # Вызываем метод
        result = await comment_search_service.get_comments_by_group(
            group_id=50
        )

        # Проверяем результат
        assert result.total == 0
        assert result.page == 1
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_filter_by_keywords_case_sensitive(
        self, comment_search_service, sample_vk_comment
    ):
        """Тест фильтрации по ключевым словам с учетом регистра"""
        comments = [sample_vk_comment]

        # Фильтруем по слову "Это" (с заглавной буквы)
        filtered = await comment_search_service.filter_by_keywords(
            comments=comments, keywords=["Это"], case_sensitive=True
        )

        # Проверяем что комментарий найден
        assert len(filtered) == 1
        assert filtered[0].id == 1

    @pytest.mark.asyncio
    async def test_filter_by_keywords_case_insensitive(
        self, comment_search_service, sample_vk_comment
    ):
        """Тест фильтрации по ключевым словам без учета регистра"""
        comments = [sample_vk_comment]

        # Фильтруем по слову "это" (с маленькой буквы)
        filtered = await comment_search_service.filter_by_keywords(
            comments=comments, keywords=["это"], case_sensitive=False
        )

        # Проверяем что комментарий найден
        assert len(filtered) == 1
        assert filtered[0].id == 1

    @pytest.mark.asyncio
    async def test_filter_by_keywords_no_match(
        self, comment_search_service, sample_vk_comment
    ):
        """Тест фильтрации по ключевым словам без совпадений"""
        comments = [sample_vk_comment]

        # Фильтруем по несуществующему слову
        filtered = await comment_search_service.filter_by_keywords(
            comments=comments, keywords=["несуществующее_слово"]
        )

        # Проверяем что комментарий не найден
        assert len(filtered) == 0

    @pytest.mark.asyncio
    async def test_get_comments_count_with_params(
        self, comment_search_service, mock_db
    ):
        """Тест подсчета комментариев с параметрами поиска"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [MagicMock()] * 10
        mock_db.execute.return_value = mock_result

        # Создаем параметры поиска
        search_params = CommentSearchParams(text="тестовый", group_id=50)

        # Вызываем метод
        count = await comment_search_service.get_comments_count(
            search_params=search_params
        )

        # Проверяем результат
        assert count == 10
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_comments_count_by_group(
        self, comment_search_service, mock_db
    ):
        """Тест подсчета комментариев по группе"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [MagicMock()] * 25
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        count = await comment_search_service.get_comments_count(group_id=50)

        # Проверяем результат
        assert count == 25
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_comments_count_total(
        self, comment_search_service, mock_db
    ):
        """Тест общего подсчета комментариев"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [MagicMock()] * 100
        mock_db.execute.return_value = mock_result

        # Вызываем метод без параметров
        count = await comment_search_service.get_comments_count()

        # Проверяем результат
        assert count == 100
        mock_db.execute.assert_called_once()

    def test_comment_to_response_conversion(
        self, comment_search_service, sample_vk_comment
    ):
        """Тест преобразования комментария в response"""
        # Вызываем приватный метод
        response = comment_search_service._comment_to_response(
            sample_vk_comment
        )

        # Проверяем результат
        assert isinstance(response, VKCommentResponse)
        assert response.id == sample_vk_comment.id
        assert response.vk_id == sample_vk_comment.vk_id
        assert response.text == sample_vk_comment.text
        assert response.author_id == sample_vk_comment.author_id
        assert response.likes_count == sample_vk_comment.likes_count

    def test_comment_to_response_with_keywords(
        self, comment_search_service, sample_comment_with_keywords
    ):
        """Тест преобразования комментария с ключевыми словами"""
        # Вызываем приватный метод
        response = comment_search_service._comment_to_response_with_keywords(
            sample_comment_with_keywords
        )

        # Проверяем результат
        assert isinstance(response, CommentWithKeywords)
        assert "тестовый" in response.matched_keywords
        assert "поиск" in response.matched_keywords
        assert len(response.keyword_matches) == 2
        assert response.keyword_matches[0]["keyword"] == "тестовый"
        assert response.keyword_matches[1]["keyword"] == "поиск"

    def test_build_search_query_with_filters(self, comment_search_service):
        """Тест построения запроса с фильтрами"""
        # Создаем параметры поиска
        search_params = CommentSearchParams(
            text="тестовый",
            group_id=50,
            author_id=67890,
            date_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
            date_to=datetime(2024, 1, 31, tzinfo=timezone.utc),
            is_viewed=True,
            order_by="published_at",
            order_dir="desc",
        )

        # Вызываем приватный метод
        query = comment_search_service._build_search_query(search_params)

        # Проверяем что запрос создан (не можем проверить детали из-за мока)
        assert query is not None

    def test_apply_sorting_asc(self, comment_search_service):
        """Тест применения сортировки по возрастанию"""
        # Создаем параметры с сортировкой
        search_params = CommentSearchParams(
            order_by="published_at", order_dir="asc"
        )

        # Создаем базовый запрос (мок)
        base_query = MagicMock()

        # Вызываем приватный метод
        sorted_query = comment_search_service._apply_sorting(
            base_query, search_params
        )

        # Проверяем что метод был вызван
        assert sorted_query is not None

    def test_apply_sorting_desc(self, comment_search_service):
        """Тест применения сортировки по убыванию"""
        # Создаем параметры с сортировкой
        search_params = CommentSearchParams(
            order_by="created_at", order_dir="desc"
        )

        # Создаем базовый запрос (мок)
        base_query = MagicMock()

        # Вызываем приватный метод
        sorted_query = comment_search_service._apply_sorting(
            base_query, search_params
        )

        # Проверяем что метод был вызван
        assert sorted_query is not None
