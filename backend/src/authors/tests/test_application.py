"""
Unit тесты для application слоя авторов

Тестирование use cases и сервисов
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from authors.application.services import AuthorService
from authors.application.use_cases import (
    CreateAuthorUseCase,
    GetAuthorUseCase,
    UpdateAuthorUseCase,
    DeleteAuthorUseCase,
    ListAuthorsUseCase,
    UpsertAuthorUseCase,
    GetOrCreateAuthorUseCase
)
from authors.domain.entities import AuthorEntity
from authors.domain.exceptions import AuthorNotFoundError, AuthorValidationError, AuthorAlreadyExistsError


class TestCreateAuthorUseCase:
    """Тесты для CreateAuthorUseCase."""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_cache(self):
        return AsyncMock()

    @pytest.fixture
    def mock_task_queue(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository, mock_cache, mock_task_queue):
        return CreateAuthorUseCase(mock_repository, mock_cache, mock_task_queue)

    @pytest.fixture
    def sample_author_data(self):
        return {
            "vk_id": 123456789,
            "first_name": "Иван",
            "last_name": "Иванов",
            "screen_name": "ivan_ivanov",
            "photo_url": "https://example.com/photo.jpg"
        }

    @pytest.fixture
    def sample_author_entity(self):
        return AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            screen_name="ivan_ivanov",
            photo_url="https://example.com/photo.jpg",
            created_at=datetime.now()
        )

    async def test_create_author_success(self, use_case, mock_repository, mock_cache, mock_task_queue, sample_author_data, sample_author_entity):
        """Тест успешного создания автора."""
        mock_repository.exists_by_vk_id.return_value = False
        mock_repository.create.return_value = sample_author_entity

        result = await use_case.execute(sample_author_data)

        assert result == sample_author_entity
        mock_repository.exists_by_vk_id.assert_called_once_with(123456789)
        mock_repository.create.assert_called_once_with(sample_author_data)
        mock_cache.set.assert_called_once()
        mock_task_queue.send_author_created_notification.assert_called_once_with(sample_author_entity)

    async def test_create_author_missing_vk_id(self, use_case, sample_author_data):
        """Тест создания автора без VK ID."""
        sample_author_data.pop("vk_id")

        with pytest.raises(AuthorValidationError, match="VK ID обязателен"):
            await use_case.execute(sample_author_data)

    async def test_create_author_empty_vk_id(self, use_case, sample_author_data):
        """Тест создания автора с пустым VK ID."""
        sample_author_data["vk_id"] = None

        with pytest.raises(AuthorValidationError, match="VK ID обязателен"):
            await use_case.execute(sample_author_data)

    async def test_create_author_already_exists(self, use_case, mock_repository, sample_author_data):
        """Тест создания автора, который уже существует."""
        mock_repository.exists_by_vk_id.return_value = True

        with pytest.raises(AuthorAlreadyExistsError):
            await use_case.execute(sample_author_data)


class TestGetAuthorUseCase:
    """Тесты для GetAuthorUseCase."""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_cache(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository, mock_cache):
        return GetAuthorUseCase(mock_repository, mock_cache, None)

    @pytest.fixture
    def sample_author_entity(self):
        return AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            created_at=datetime.now(),
            comments_count=10
        )

    async def test_get_author_from_cache(self, use_case, mock_cache, sample_author_entity):
        """Тест получения автора из кэша."""
        mock_cache.get.return_value = sample_author_entity

        result = await use_case.execute(123456789)

        assert result == sample_author_entity
        mock_cache.get.assert_called_once_with("author:vk_id:123456789")
        # Репозиторий не должен вызываться, если данные в кэше
        use_case.repository.get_by_vk_id.assert_not_called()

    async def test_get_author_from_repository(self, use_case, mock_repository, mock_cache, sample_author_entity):
        """Тест получения автора из репозитория."""
        mock_cache.get.return_value = None
        mock_repository.get_by_vk_id.return_value = sample_author_entity

        result = await use_case.execute(123456789)

        assert result == sample_author_entity
        mock_cache.get.assert_called_once_with("author:vk_id:123456789")
        mock_repository.get_by_vk_id.assert_called_once_with(123456789)
        mock_cache.set.assert_called_once_with("author:vk_id:123456789", sample_author_entity, 3600)

    async def test_get_author_not_found(self, use_case, mock_repository, mock_cache):
        """Тест получения несуществующего автора."""
        mock_cache.get.return_value = None
        mock_repository.get_by_vk_id.return_value = None

        result = await use_case.execute(123456789)

        assert result is None
        mock_cache.get.assert_called_once_with("author:vk_id:123456789")
        mock_repository.get_by_vk_id.assert_called_once_with(123456789)


class TestUpdateAuthorUseCase:
    """Тесты для UpdateAuthorUseCase."""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_cache(self):
        return AsyncMock()

    @pytest.fixture
    def mock_task_queue(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository, mock_cache, mock_task_queue):
        return UpdateAuthorUseCase(mock_repository, mock_cache, mock_task_queue)

    @pytest.fixture
    def sample_author_entity(self):
        return AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            created_at=datetime.now(),
            comments_count=10
        )

    async def test_update_author_success(self, use_case, mock_repository, mock_cache, mock_task_queue, sample_author_entity):
        """Тест успешного обновления автора."""
        update_data = {"first_name": "Петр"}
        mock_repository.exists_by_vk_id.return_value = True
        mock_repository.update.return_value = sample_author_entity

        result = await use_case.execute(123456789, update_data)

        assert result == sample_author_entity
        mock_repository.exists_by_vk_id.assert_called_once_with(123456789)
        mock_repository.update.assert_called_once_with(123456789, update_data)
        mock_cache.delete.assert_called_once_with("author:vk_id:123456789")
        mock_cache.set.assert_called_once_with("author:vk_id:123456789", sample_author_entity, 3600)
        mock_task_queue.send_author_updated_notification.assert_called_once_with(sample_author_entity)

    async def test_update_author_not_found(self, use_case, mock_repository):
        """Тест обновления несуществующего автора."""
        mock_repository.exists_by_vk_id.return_value = False

        with pytest.raises(AuthorNotFoundError):
            await use_case.execute(123456789, {"first_name": "Петр"})


class TestAuthorService:
    """Тесты для AuthorService."""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_cache(self):
        return AsyncMock()

    @pytest.fixture
    def mock_task_queue(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository, mock_cache, mock_task_queue):
        return AuthorService(mock_repository, mock_cache, mock_task_queue)

    @pytest.fixture
    def sample_author_data(self):
        return {
            "vk_id": 123456789,
            "first_name": "Иван",
            "last_name": "Иванов"
        }

    @pytest.fixture
    def sample_author_entity(self):
        return AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            created_at=datetime.now(),
            comments_count=10
        )

    async def test_create_author_success(self, service, sample_author_data, sample_author_entity):
        """Тест успешного создания автора через сервис."""
        # Мокаем use case
        service._create_use_case.execute = AsyncMock(return_value=sample_author_entity)

        result = await service.create_author(sample_author_data)

        assert result == sample_author_entity
        service._create_use_case.execute.assert_called_once_with(sample_author_data)

    async def test_get_author_success(self, service, sample_author_entity):
        """Тест успешного получения автора через сервис."""
        service._get_use_case.execute = AsyncMock(return_value=sample_author_entity)

        result = await service.get_author(123456789)

        assert result == sample_author_entity
        service._get_use_case.execute.assert_called_once_with(123456789)

    async def test_list_authors_success(self, service):
        """Тест успешного получения списка авторов через сервис."""
        authors = [sample_author_entity]
        service._list_use_case.execute = AsyncMock(return_value=authors)

        result = await service.list_authors(limit=10, offset=0)

        assert result == authors
        service._list_use_case.execute.assert_called_once_with(10, 0)

    async def test_search_authors_success(self, service):
        """Тест успешного поиска авторов через сервис."""
        authors = [sample_author_entity]
        service.list_authors = AsyncMock(return_value=authors)

        result = await service.search_authors("Иван", limit=10)

        assert result == authors
        service.list_authors.assert_called_once_with(limit=1000)

    async def test_bulk_create_authors_success(self, service, sample_author_data, sample_author_entity):
        """Тест успешного массового создания авторов."""
        authors_data = [sample_author_data, sample_author_data]
        service.create_author = AsyncMock(return_value=sample_author_entity)

        result = await service.bulk_create_authors(authors_data)

        assert len(result) == 2
        assert all(author == sample_author_entity for author in result)
        assert service.create_author.call_count == 2

    async def test_bulk_create_authors_with_errors(self, service, sample_author_data, sample_author_entity):
        """Тест массового создания авторов с ошибками."""
        authors_data = [sample_author_data, sample_author_data]
        
        # Первый вызов успешен, второй падает с ошибкой
        service.create_author = AsyncMock(side_effect=[sample_author_entity, Exception("Test error")])

        result = await service.bulk_create_authors(authors_data)

        assert len(result) == 1
        assert result[0] == sample_author_entity
        assert service.create_author.call_count == 2
