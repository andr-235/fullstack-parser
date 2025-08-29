"""
Тесты для улучшенного KeywordService - сервиса управления ключевыми словами

Тестируемые возможности:
- Новые методы: статистика, массовые операции, поиск, проверка дубликатов
- Расширенная функциональность по категориям
- Улучшенная обработка ошибок
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.keyword_service import KeywordService
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate
from app.schemas.base import (
    StatusResponse,
    PaginatedResponse,
    PaginationParams,
)


class TestKeywordServiceEnhanced:
    """Тесты для улучшенного KeywordService"""

    @pytest.fixture
    def mock_db(self):
        """Мок для базы данных"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def keyword_service(self):
        """Экземпляр KeywordService для тестирования"""
        return KeywordService()

    @pytest.fixture
    def sample_keyword_data(self):
        """Пример данных ключевого слова для создания"""
        return KeywordCreate(
            word="тестовое слово",
            category="тестовая категория",
            description="Описание тестового слова",
        )

    @pytest.fixture
    def sample_keyword(self):
        """Пример объекта ключевого слова"""
        keyword = MagicMock(spec=Keyword)
        keyword.id = 1
        keyword.word = "тестовое слово"
        keyword.category = "тестовая категория"
        keyword.description = "Описание тестового слова"
        keyword.is_active = True
        return keyword

    # Тесты для get_keyword_statistics

    @pytest.mark.asyncio
    async def test_get_keyword_statistics_success(
        self, keyword_service, mock_db
    ):
        """Тест успешного получения статистики ключевых слов"""
        # Настройка моков
        mock_result_total = MagicMock()
        mock_result_total.scalar.return_value = 100
        mock_result_active = MagicMock()
        mock_result_active.scalar.return_value = 80
        mock_result_categories = MagicMock()
        mock_result_categories.all.return_value = [
            ("категория1", 30),
            ("категория2", 25),
        ]
        mock_result_longest = MagicMock()
        mock_result_longest.all.return_value = [
            ("длинное_слово", 12),
            ("очень_длинное_слово", 18),
        ]
        mock_result_avg = MagicMock()
        mock_result_avg.scalar.return_value = 8.5

        # Настройка последовательных вызовов
        mock_db.execute.side_effect = [
            mock_result_total,  # SELECT COUNT(*)
            mock_result_active,  # SELECT COUNT(*) WHERE is_active = True
            mock_result_categories,  # SELECT category, COUNT(*)
            mock_result_longest,  # SELECT word, LENGTH(word)
            mock_result_avg,  # SELECT AVG(LENGTH(word))
        ]

        # Выполнение
        result = await keyword_service.get_keyword_statistics(mock_db)

        # Проверки
        assert result["total_keywords"] == 100
        assert result["active_keywords"] == 80
        assert result["inactive_keywords"] == 20
        assert len(result["categories_stats"]) == 2
        assert result["categories_stats"]["категория1"] == 30
        assert result["average_word_length"] == 8.5
        assert result["longest_keywords"]["длинное_слово"] == 12

    @pytest.mark.asyncio
    async def test_get_keyword_statistics_empty(
        self, keyword_service, mock_db
    ):
        """Тест получения статистики для пустой базы"""
        # Настройка моков для пустой базы
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_result.all.return_value = []

        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await keyword_service.get_keyword_statistics(mock_db)

        # Проверки
        assert result["total_keywords"] == 0
        assert result["active_keywords"] == 0
        assert result["inactive_keywords"] == 0
        assert len(result["categories_stats"]) == 0
        assert result["average_word_length"] == 0.0

    @pytest.mark.asyncio
    async def test_get_keyword_statistics_error(
        self, keyword_service, mock_db
    ):
        """Тест обработки ошибки при получении статистики"""
        # Настройка мока для ошибки
        mock_db.execute.side_effect = Exception("Database error")

        # Выполнение
        result = await keyword_service.get_keyword_statistics(mock_db)

        # Проверки
        assert result == {}

    # Тесты для bulk_update_status

    @pytest.mark.asyncio
    async def test_bulk_update_status_success(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест успешного массового обновления статуса"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_keyword]
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()

        # Выполнение
        result = await keyword_service.bulk_update_status(mock_db, [1], False)

        # Проверки
        assert isinstance(result, StatusResponse)
        assert result.status == "success"
        assert "Обновлено 1 ключевых слов" in result.message
        assert "неактивно" in result.message
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_update_status_activate(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест массового активации ключевых слов"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_keyword]
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()

        # Выполнение
        result = await keyword_service.bulk_update_status(mock_db, [1], True)

        # Проверки
        assert result.status == "success"
        assert "активно" in result.message
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_update_status_empty_list(
        self, keyword_service, mock_db
    ):
        """Тест массового обновления с пустым списком ID"""
        # Выполнение
        result = await keyword_service.bulk_update_status(mock_db, [], True)

        # Проверки
        assert result.status == "error"
        assert "Не указаны ID ключевых слов" in result.message
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_bulk_update_status_error(self, keyword_service, mock_db):
        """Тест обработки ошибки при массовом обновлении"""
        # Настройка мока для ошибки
        mock_db.execute.side_effect = Exception("Database error")

        # Выполнение
        result = await keyword_service.bulk_update_status(
            mock_db, [1, 2], True
        )

        # Проверки
        assert result.status == "error"
        assert "Ошибка при массовом обновлении статуса" in result.message
        mock_db.rollback.assert_called_once()

    # Тесты для search_keywords

    @pytest.mark.asyncio
    async def test_search_keywords_success(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест успешного поиска ключевых слов"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 1
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = [
            sample_keyword
        ]

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Выполнение
        result = await keyword_service.search_keywords(mock_db, "тест")

        # Проверки
        assert isinstance(result, PaginatedResponse)
        assert result.total == 1
        assert result.page == 1
        assert result.size == 20
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_search_keywords_with_category(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест поиска с фильтром по категории"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 1
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = [
            sample_keyword
        ]

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Выполнение
        result = await keyword_service.search_keywords(
            mock_db, "тест", category="тестовая категория"
        )

        # Проверки
        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_search_keywords_inactive_only(
        self, keyword_service, mock_db
    ):
        """Тест поиска только неактивных слов"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 0
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Выполнение
        result = await keyword_service.search_keywords(
            mock_db, "тест", active_only=False
        )

        # Проверки
        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_search_keywords_with_pagination(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест поиска с пагинацией"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 1
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = [
            sample_keyword
        ]

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Выполнение
        result = await keyword_service.search_keywords(
            mock_db, "тест", limit=5, offset=10
        )

        # Проверки
        assert result.page == 3  # (10 // 5) + 1
        assert result.size == 5
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_search_keywords_empty_query(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест поиска с пустым запросом"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 1
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = [
            sample_keyword
        ]

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Выполнение
        result = await keyword_service.search_keywords(mock_db, "")

        # Проверки
        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_search_keywords_no_results(self, keyword_service, mock_db):
        """Тест поиска без результатов"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 0
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Выполнение
        result = await keyword_service.search_keywords(
            mock_db, "несуществующее_слово"
        )

        # Проверки
        assert result.total == 0
        assert len(result.items) == 0
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_search_keywords_error(self, keyword_service, mock_db):
        """Тест обработки ошибки при поиске"""
        # Настройка мока для ошибки
        mock_db.execute.side_effect = Exception("Database error")

        # Выполнение
        result = await keyword_service.search_keywords(mock_db, "тест")

        # Проверки
        assert result.total == 0
        assert len(result.items) == 0
        assert result.page == 1

    # Тесты для get_keywords_by_category

    @pytest.mark.asyncio
    async def test_get_keywords_by_category_success(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест успешного получения ключевых слов по категории"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 5
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = [
            sample_keyword
        ]

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Параметры пагинации
        pagination = PaginationParams(page=1, size=10)

        # Выполнение
        result = await keyword_service.get_keywords_by_category(
            mock_db, "тестовая категория", pagination
        )

        # Проверки
        assert isinstance(result, PaginatedResponse)
        assert result.total == 5
        assert result.page == 1
        assert result.size == 10
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_get_keywords_by_category_empty(
        self, keyword_service, mock_db
    ):
        """Тест получения ключевых слов по несуществующей категории"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 0
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Параметры пагинации
        pagination = PaginationParams(page=1, size=10)

        # Выполнение
        result = await keyword_service.get_keywords_by_category(
            mock_db, "несуществующая категория", pagination
        )

        # Проверки
        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_get_keywords_by_category_with_pagination(
        self, keyword_service, mock_db, sample_keyword
    ):
        """Тест получения ключевых слов по категории с пагинацией"""
        # Настройка моков
        mock_result_count = MagicMock()
        mock_result_count.scalar.return_value = 25
        mock_result_data = MagicMock()
        mock_result_data.scalars.return_value.all.return_value = [
            sample_keyword
        ]

        mock_db.execute.side_effect = [mock_result_count, mock_result_data]

        # Параметры пагинации (вторая страница)
        pagination = PaginationParams(page=2, size=10)

        # Выполнение
        result = await keyword_service.get_keywords_by_category(
            mock_db, "тестовая категория", pagination
        )

        # Проверки
        assert result.total == 25
        assert result.page == 2
        assert result.size == 10

    # Тесты для duplicate_keywords_check

    @pytest.mark.asyncio
    async def test_duplicate_keywords_check_success(
        self, keyword_service, mock_db
    ):
        """Тест успешной проверки дубликатов"""
        # Настройка моков
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = (
            MagicMock()
        )  # Первое слово существует
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = (
            None  # Второе слово не существует
        )

        mock_db.execute.side_effect = [mock_result1, mock_result2]

        # Выполнение
        result = await keyword_service.duplicate_keywords_check(
            mock_db, ["существующее_слово", "новое_слово"]
        )

        # Проверки
        assert len(result) == 2
        assert result["существующее_слово"] is True
        assert result["новое_слово"] is False

    @pytest.mark.asyncio
    async def test_duplicate_keywords_check_all_new(
        self, keyword_service, mock_db
    ):
        """Тест проверки дубликатов для новых слов"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = (
            None  # Ни одно слово не существует
        )

        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await keyword_service.duplicate_keywords_check(
            mock_db, ["слово1", "слово2", "слово3"]
        )

        # Проверки
        assert len(result) == 3
        assert all(not exists for exists in result.values())

    @pytest.mark.asyncio
    async def test_duplicate_keywords_check_all_duplicates(
        self, keyword_service, mock_db
    ):
        """Тест проверки дубликатов для существующих слов"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = (
            MagicMock()
        )  # Все слова существуют

        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await keyword_service.duplicate_keywords_check(
            mock_db, ["дубликат1", "дубликат2"]
        )

        # Проверки
        assert len(result) == 2
        assert all(exists for exists in result.values())

    @pytest.mark.asyncio
    async def test_duplicate_keywords_check_empty_list(
        self, keyword_service, mock_db
    ):
        """Тест проверки дубликатов для пустого списка"""
        # Выполнение
        result = await keyword_service.duplicate_keywords_check(mock_db, [])

        # Проверки
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_duplicate_keywords_check_error(
        self, keyword_service, mock_db
    ):
        """Тест обработки ошибки при проверке дубликатов"""
        # Настройка мока для ошибки
        mock_db.execute.side_effect = Exception("Database error")

        # Выполнение
        result = await keyword_service.duplicate_keywords_check(
            mock_db, ["слово1", "слово2"]
        )

        # Проверки
        assert len(result) == 2
        assert result["слово1"] is False
        assert result["слово2"] is False

    # Тесты для _get_average_word_length

    @pytest.mark.asyncio
    async def test_get_average_word_length_success(
        self, keyword_service, mock_db
    ):
        """Тест успешного получения средней длины слова"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 7.25

        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await keyword_service._get_average_word_length(mock_db)

        # Проверки
        assert result == 7.25

    @pytest.mark.asyncio
    async def test_get_average_word_length_no_words(
        self, keyword_service, mock_db
    ):
        """Тест получения средней длины при отсутствии слов"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = None

        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await keyword_service._get_average_word_length(mock_db)

        # Проверки
        assert result == 0.0

    @pytest.mark.asyncio
    async def test_get_average_word_length_error(
        self, keyword_service, mock_db
    ):
        """Тест обработки ошибки при получении средней длины"""
        # Настройка мока для ошибки
        mock_db.execute.side_effect = Exception("Database error")

        # Выполнение
        result = await keyword_service._get_average_word_length(mock_db)

        # Проверки
        assert result == 0.0
