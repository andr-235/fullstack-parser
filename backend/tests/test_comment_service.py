"""
Тесты для CommentService

Тестирует все основные методы сервиса с использованием моков
для изоляции от базы данных и внешних зависимостей.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select

from app.services.comment_service import CommentService
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentUpdateRequest,
    CommentWithKeywords,
    VKCommentResponse,
)


@pytest.fixture
def mock_db():
    """Фикстура для мок базы данных"""
    return AsyncMock()


@pytest.fixture
def comment_service(mock_db):
    """Фикстура для CommentService"""
    return CommentService(mock_db)


@pytest.fixture
def sample_vk_comment():
    """Фикстура для примера VKComment"""
    # Создаем реальный объект с правильными типами вместо MagicMock
    comment = MagicMock(spec=VKComment)

    # Основные поля
    comment.id = 1
    comment.vk_id = 12345
    comment.text = "Это тестовый комментарий"
    comment.author_id = 67890
    comment.author_name = "Тестовый Автор"
    comment.author_screen_name = "test_author"
    comment.author_photo_url = "https://example.com/photo.jpg"
    comment.published_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    comment.likes_count = 5
    comment.parent_comment_id = None
    comment.has_attachments = False
    comment.matched_keywords_count = 0
    comment.is_processed = False
    comment.processed_at = None
    comment.is_viewed = False
    comment.is_archived = False
    comment.viewed_at = None
    comment.archived_at = None
    comment.created_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    comment.updated_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Связи
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

    # Мок для ключевых слов (пустой по умолчанию)
    comment.keyword_matches = []

    return comment


@pytest.fixture
def sample_comment_response():
    """Фикстура для примера VKCommentResponse"""
    return VKCommentResponse(
        id=1,
        vk_id=12345,
        text="Это тестовый комментарий",
        author_id=67890,
        author_name="Тестовый Автор",
        published_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        likes_count=5,
        is_viewed=False,
        is_archived=False,
        viewed_at=None,
        archived_at=None,
        created_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )


class TestCommentService:
    """Тесты для CommentService"""

    @pytest.mark.asyncio
    async def test_get_comments_by_group_success(
        self, comment_service, mock_db, sample_vk_comment
    ):
        """Тест успешного получения комментариев группы"""
        # Настраиваем мок для execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_vk_comment]
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        comments = await comment_service.get_comments_by_group(
            group_id=50, limit=10, offset=0, include_group=True
        )

        # Проверяем вызовы
        assert len(comments) == 1
        assert isinstance(comments[0], VKCommentResponse)
        assert comments[0].vk_id == 12345
        assert comments[0].text == "Это тестовый комментарий"

        # Проверяем что execute был вызван с правильным запросом
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_comments_by_group_empty_result(
        self, comment_service, mock_db
    ):
        """Тест получения пустого списка комментариев"""
        # Настраиваем мок для пустого результата
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        comments = await comment_service.get_comments_by_group(group_id=50)

        # Проверяем результат
        assert len(comments) == 0
        assert isinstance(comments, list)

    @pytest.mark.asyncio
    async def test_get_comments_by_group_database_error(
        self, comment_service, mock_db
    ):
        """Тест обработки ошибки базы данных"""
        # Настраиваем мок для выброса исключения
        mock_db.execute.side_effect = Exception("Database connection error")

        # Проверяем что исключение пробрасывается
        with pytest.raises(Exception, match="Database connection error"):
            await comment_service.get_comments_by_group(group_id=50)

    @pytest.mark.asyncio
    async def test_search_comments_with_filters(
        self, comment_service, mock_db, sample_vk_comment
    ):
        """Тест поиска комментариев с фильтрами"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_vk_comment]
        mock_db.execute.return_value = mock_result

        # Создаем параметры поиска
        search_params = CommentSearchParams(
            text="тестовый",
            group_id=50,
            date_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
            date_to=datetime(2024, 1, 31, tzinfo=timezone.utc),
        )

        # Вызываем метод
        comments = await comment_service.search_comments(
            search_params=search_params, limit=20, offset=0
        )

        # Проверяем результат
        assert len(comments) == 1
        assert isinstance(comments[0], CommentWithKeywords)
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_comments_no_results(self, comment_service, mock_db):
        """Тест поиска без результатов"""
        # Настраиваем мок для пустого результата
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Создаем параметры поиска
        search_params = CommentSearchParams(text="несуществующий текст")

        # Вызываем метод
        comments = await comment_service.search_comments(search_params)

        # Проверяем результат
        assert len(comments) == 0

    @pytest.mark.asyncio
    async def test_get_comment_by_id_found(
        self, comment_service, mock_db, sample_vk_comment
    ):
        """Тест получения комментария по ID - найден"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_vk_comment
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        comment = await comment_service.get_comment_by_id(1)

        # Проверяем результат
        assert comment is not None
        assert isinstance(comment, VKCommentResponse)
        assert comment.id == 1
        assert comment.vk_id == 12345

    @pytest.mark.asyncio
    async def test_get_comment_by_id_not_found(self, comment_service, mock_db):
        """Тест получения комментария по ID - не найден"""
        # Настраиваем мок для None результата
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        comment = await comment_service.get_comment_by_id(999)

        # Проверяем результат
        assert comment is None

    @pytest.mark.asyncio
    async def test_update_comment_success(
        self, comment_service, mock_db, sample_vk_comment
    ):
        """Тест успешного обновления комментария"""
        # Настраиваем мок для get_comment_by_id (используется внутри update_comment)
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = sample_vk_comment

        # Настраиваем мок для получения объекта для обновления
        mock_update_result = MagicMock()
        mock_update_result.scalar_one.return_value = sample_vk_comment

        # Настраиваем последовательные вызовы execute
        mock_db.execute.side_effect = [mock_get_result, mock_update_result]

        # Создаем данные для обновления
        update_data = CommentUpdateRequest(is_viewed=True, is_archived=False)

        # Вызываем метод
        result = await comment_service.update_comment(1, update_data)

        # Проверяем результат
        assert result is not None
        assert isinstance(result, VKCommentResponse)
        assert result.id == 1

        # Проверяем что commit был вызван
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_comment_not_found(self, comment_service, mock_db):
        """Тест обновления несуществующего комментария"""
        # Настраиваем мок для None результата
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Создаем данные для обновления
        update_data = CommentUpdateRequest(is_viewed=True)

        # Вызываем метод
        result = await comment_service.update_comment(999, update_data)

        # Проверяем результат
        assert result is None

    @pytest.mark.asyncio
    async def test_update_comment_database_error(
        self, comment_service, mock_db, sample_vk_comment
    ):
        """Тест обработки ошибки при обновлении"""
        # Настраиваем моки для успешного получения комментария
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = sample_vk_comment

        mock_update_result = MagicMock()
        mock_update_result.scalar_one.return_value = sample_vk_comment

        # Настраиваем последовательные вызовы execute, а потом исключение при commit
        mock_db.execute.side_effect = [mock_get_result, mock_update_result]
        mock_db.commit.side_effect = Exception("Commit failed")

        # Создаем данные для обновления
        update_data = CommentUpdateRequest(is_viewed=True)

        # Вызываем метод и проверяем исключение
        with pytest.raises(Exception, match="Commit failed"):
            await comment_service.update_comment(1, update_data)

        # Проверяем что rollback был вызван
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_comment_stats_all_groups(
        self, comment_service, mock_db, sample_vk_comment
    ):
        """Тест получения статистики по всем группам"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_vk_comment]
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        stats = await comment_service.get_comment_stats()

        # Проверяем результат
        assert isinstance(stats, dict)
        assert "total_comments" in stats
        assert "viewed_comments" in stats
        assert "archived_comments" in stats
        assert stats["total_comments"] == 1
        assert (
            stats["viewed_comments"] == 0
        )  # sample_comment.is_viewed = False
        assert stats["archived_comments"] == 0

    @pytest.mark.asyncio
    async def test_get_comment_stats_specific_group(
        self, comment_service, mock_db, sample_vk_comment
    ):
        """Тест получения статистики по конкретной группе"""
        # Настраиваем мок
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_vk_comment]
        mock_db.execute.return_value = mock_result

        # Вызываем метод для конкретной группы
        stats = await comment_service.get_comment_stats(group_id=50)

        # Проверяем результат
        assert isinstance(stats, dict)
        assert stats["total_comments"] == 1

    @pytest.mark.asyncio
    async def test_get_comment_stats_empty_result(
        self, comment_service, mock_db
    ):
        """Тест получения статистики при пустом результате"""
        # Настраиваем мок для пустого результата
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        stats = await comment_service.get_comment_stats()

        # Проверяем результат
        assert stats["total_comments"] == 0
        assert stats["viewed_comments"] == 0
        assert stats["archived_comments"] == 0
        assert stats["view_rate"] == 0
        assert stats["archive_rate"] == 0

    def test_comment_to_response_conversion(
        self, comment_service, sample_vk_comment
    ):
        """Тест преобразования комментария в response"""
        # Вызываем приватный метод
        response = comment_service._comment_to_response(sample_vk_comment)

        # Проверяем результат
        assert isinstance(response, VKCommentResponse)
        assert response.id == sample_vk_comment.id
        assert response.vk_id == sample_vk_comment.vk_id
        assert response.text == sample_vk_comment.text
        assert response.author_id == sample_vk_comment.author_id
        assert response.likes_count == sample_vk_comment.likes_count

    def test_comment_to_response_with_keywords(
        self, comment_service, sample_vk_comment
    ):
        """Тест преобразования комментария в response с ключевыми словами"""
        # Добавляем keyword_matches к комментарию
        keyword_match = MagicMock()
        keyword_match.keyword.word = "тест"
        keyword_match.position = 10
        keyword_match.matched_text = "тестовый текст"

        sample_vk_comment.keyword_matches = [keyword_match]

        # Вызываем метод
        response = comment_service._comment_to_response_with_keywords(
            sample_vk_comment
        )

        # Проверяем результат
        assert isinstance(response, CommentWithKeywords)
        assert "тест" in response.matched_keywords
        assert len(response.keyword_matches) == 1
        assert response.keyword_matches[0]["keyword"] == "тест"
