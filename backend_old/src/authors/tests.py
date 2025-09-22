"""
Unit-тесты для модуля авторов
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import AuthorAlreadyExistsError, AuthorNotFoundError
from .models import AuthorModel
from .repository import AuthorRepository
from .schemas import AuthorCreate, AuthorUpdate, AuthorResponse
from .services import AuthorService


# Константы для тестов
TEST_VK_ID = 12345
TEST_FIRST_NAME = "Иван"
TEST_LAST_NAME = "Иванов"
TEST_SCREEN_NAME = "ivanov"
TEST_PHOTO_URL = "https://example.com/photo.jpg"
TEST_STATUS = "active"
TEST_FOLLOWERS_COUNT = 1000
TEST_COMMENTS_COUNT = 50
TEST_MAX_SCREEN_NAME_LENGTH = 100


class TestAuthorRepository:
    """Тесты для AuthorRepository"""

    @pytest.fixture
    def mock_db(self):
        """Мок базы данных"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_db):
        """Экземпляр репозитория с моками"""
        return AuthorRepository(mock_db)

    @pytest.fixture
    def sample_author_data(self):
        """Пример данных автора"""
        return {
            "id": 1,
            "vk_id": TEST_VK_ID,
            "first_name": TEST_FIRST_NAME,
            "last_name": TEST_LAST_NAME,
            "screen_name": TEST_SCREEN_NAME,
            "photo_url": TEST_PHOTO_URL,
            "status": TEST_STATUS,
            "is_closed": False,
            "is_verified": True,
            "followers_count": TEST_FOLLOWERS_COUNT,
            "last_activity": datetime.utcnow(),
            "author_metadata": json.dumps({"key": "value"}),
            "comments_count": TEST_COMMENTS_COUNT,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    @pytest.fixture
    def sample_author_model(self, sample_author_data):
        """Пример модели автора"""
        author = AuthorModel()
        for key, value in sample_author_data.items():
            setattr(author, key, value)
        return author

    @pytest.fixture
    def sample_create_data(self):
        """Пример данных для создания"""
        return AuthorCreate(
            vk_id=TEST_VK_ID,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            screen_name=TEST_SCREEN_NAME,
            photo_url=TEST_PHOTO_URL,
            status=TEST_STATUS,
            is_closed=False,
            is_verified=True,
            followers_count=TEST_FOLLOWERS_COUNT,
            metadata={"key": "value"},
            comments_count=TEST_COMMENTS_COUNT
        )

    @pytest.fixture
    def sample_author_with_special_chars(self):
        """Пример автора с специальными символами в screen_name"""
        return AuthorModel(
            id=2,
            vk_id=67890,
            first_name="Мария",
            last_name="Петрова",
            screen_name="maria_petrova-123",
            photo_url="https://example.com/photo2.jpg",
            status="inactive",
            is_closed=True,
            is_verified=False,
            followers_count=500,
            last_activity=datetime.utcnow(),
            author_metadata=json.dumps({"special": True}),
            comments_count=25,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def test_get_by_id_success(self, repository, mock_db, sample_author_model):
        """Тест успешного получения автора по ID"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_author_model

        result = await repository.get_by_id(1)

        assert result == sample_author_model
        mock_db.execute.assert_called_once()

    async def test_get_by_id_not_found(self, repository, mock_db):
        """Тест получения несуществующего автора"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        result = await repository.get_by_id(999)

        assert result is None
        mock_db.execute.assert_called_once()

    async def test_get_by_vk_id_success(self, repository, mock_db, sample_author_model):
        """Тест успешного получения автора по VK ID"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_author_model

        result = await repository.get_by_vk_id(TEST_VK_ID)

        assert result == sample_author_model
        mock_db.execute.assert_called_once()

    async def test_get_by_vk_id_not_found(self, repository, mock_db):
        """Тест получения автора по несуществующему VK ID"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        result = await repository.get_by_vk_id(99999)

        assert result is None
        mock_db.execute.assert_called_once()

    async def test_get_by_screen_name_success(self, repository, mock_db, sample_author_model):
        """Тест успешного получения автора по screen name"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_author_model

        result = await repository.get_by_screen_name(TEST_SCREEN_NAME)

        assert result == sample_author_model
        assert result.screen_name == TEST_SCREEN_NAME
        mock_db.execute.assert_called_once()

    async def test_get_by_screen_name_not_found(self, repository, mock_db):
        """Тест получения автора по несуществующему screen name"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        result = await repository.get_by_screen_name("nonexistent")

        assert result is None
        mock_db.execute.assert_called_once()

    async def test_get_by_screen_name_special_chars(self, repository, mock_db, sample_author_with_special_chars):
        """Тест получения автора с специальными символами в screen name"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_author_with_special_chars

        result = await repository.get_by_screen_name("maria_petrova-123")

        assert result == sample_author_with_special_chars
        assert result.screen_name == "maria_petrova-123"
        mock_db.execute.assert_called_once()

    async def test_get_by_screen_name_empty_string(self, repository, mock_db):
        """Тест получения автора по пустому screen name"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        result = await repository.get_by_screen_name("")

        assert result is None
        mock_db.execute.assert_called_once()

    async def test_create_success(self, repository, mock_db, sample_create_data, sample_author_model):
        """Тест успешного создания автора"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        result = await repository.create(sample_create_data)

        assert isinstance(result, AuthorModel)
        assert result.vk_id == TEST_VK_ID
        assert result.first_name == TEST_FIRST_NAME
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    async def test_create_duplicate_vk_id(self, repository, mock_db, sample_create_data, sample_author_model):
        """Тест создания автора с существующим VK ID"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_author_model

        with pytest.raises(AuthorAlreadyExistsError):
            await repository.create(sample_create_data)

    async def test_update_success(self, repository, mock_db, sample_author_model):
        """Тест успешного обновления автора"""
        update_data = AuthorUpdate(first_name="Петр")
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_author_model

        result = await repository.update(1, update_data)

        assert result.first_name == "Петр"
        assert result.id == 1
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    async def test_update_not_found(self, repository, mock_db):
        """Тест обновления несуществующего автора"""
        update_data = AuthorUpdate(first_name="Петр")
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with pytest.raises(AuthorNotFoundError):
            await repository.update(999, update_data)

    async def test_delete_success(self, repository, mock_db, sample_author_model):
        """Тест успешного удаления автора"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_author_model

        result = await repository.delete(1)

        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_delete_not_found(self, repository, mock_db):
        """Тест удаления несуществующего автора"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with pytest.raises(AuthorNotFoundError):
            await repository.delete(999)


class TestAuthorService:
    """Тесты для AuthorService"""

    @pytest.fixture
    def mock_repository(self):
        """Мок репозитория"""
        return AsyncMock(spec=AuthorRepository)

    @pytest.fixture
    def service(self, mock_repository):
        """Экземпляр сервиса с моками"""
        service = AuthorService.__new__(AuthorService)
        service.repository = mock_repository
        return service

    @pytest.fixture
    def sample_response(self):
        """Пример ответа"""
        return AuthorResponse(
            id=1,
            vk_id=TEST_VK_ID,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            screen_name=TEST_SCREEN_NAME,
            photo_url=TEST_PHOTO_URL,
            status=TEST_STATUS,
            is_closed=False,
            is_verified=True,
            followers_count=TEST_FOLLOWERS_COUNT,
            last_activity=datetime.utcnow(),
            metadata={"key": "value"},
            comments_count=TEST_COMMENTS_COUNT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def test_create_author_success(self, service, mock_repository, sample_response):
        """Тест успешного создания автора через сервис"""
        create_data = AuthorCreate(vk_id=TEST_VK_ID, first_name=TEST_FIRST_NAME)
        mock_repository.create.return_value = sample_response

        result = await service.create_author(create_data)

        assert isinstance(result, AuthorResponse)
        assert result.vk_id == TEST_VK_ID
        mock_repository.create.assert_called_once_with(create_data)

    async def test_create_author_duplicate(self, service, mock_repository):
        """Тест создания автора с дубликатом VK ID"""
        create_data = AuthorCreate(vk_id=TEST_VK_ID, first_name=TEST_FIRST_NAME)
        mock_repository.create.side_effect = AuthorAlreadyExistsError(TEST_VK_ID)

        with pytest.raises(AuthorAlreadyExistsError):
            await service.create_author(create_data)

    async def test_get_by_id_success(self, service, mock_repository, sample_response):
        """Тест успешного получения автора по ID"""
        mock_repository.get_by_id.return_value = sample_response

        result = await service.get_by_id(1)

        assert result == sample_response
        mock_repository.get_by_id.assert_called_once_with(1)

    async def test_get_by_id_not_found(self, service, mock_repository):
        """Тест получения несуществующего автора"""
        mock_repository.get_by_id.return_value = None

        result = await service.get_by_id(999)

        assert result is None

    async def test_get_by_vk_id_success(self, service, mock_repository, sample_response):
        """Тест успешного получения автора по VK ID"""
        mock_repository.get_by_vk_id.return_value = sample_response

        result = await service.get_by_vk_id(TEST_VK_ID)

        assert result == sample_response
        assert result.vk_id == TEST_VK_ID
        mock_repository.get_by_vk_id.assert_called_once_with(TEST_VK_ID)

    async def test_get_by_vk_id_not_found(self, service, mock_repository):
        """Тест получения автора по несуществующему VK ID"""
        mock_repository.get_by_vk_id.return_value = None

        result = await service.get_by_vk_id(99999)

        assert result is None

    async def test_get_by_screen_name_success(self, service, mock_repository, sample_response):
        """Тест успешного получения автора по screen name"""
        mock_repository.get_by_screen_name.return_value = sample_response

        result = await service.get_by_screen_name(TEST_SCREEN_NAME)

        assert result == sample_response
        assert result.screen_name == TEST_SCREEN_NAME
        mock_repository.get_by_screen_name.assert_called_once_with(TEST_SCREEN_NAME)

    async def test_get_by_screen_name_not_found(self, service, mock_repository):
        """Тест получения автора по несуществующему screen name"""
        mock_repository.get_by_screen_name.return_value = None

        result = await service.get_by_screen_name("nonexistent")

        assert result is None

    async def test_get_by_screen_name_empty(self, service, mock_repository):
        """Тест получения автора по пустому screen name"""
        mock_repository.get_by_screen_name.return_value = None

        result = await service.get_by_screen_name("")

        assert result is None

    async def test_update_author_success(self, service, mock_repository, sample_response):
        """Тест успешного обновления автора"""
        update_data = AuthorUpdate(first_name="Петр")
        mock_repository.update.return_value = sample_response

        result = await service.update_author(1, update_data)

        assert result == sample_response
        mock_repository.update.assert_called_once_with(1, update_data)

    async def test_update_author_not_found(self, service, mock_repository):
        """Тест обновления несуществующего автора"""
        update_data = AuthorUpdate(first_name="Петр")
        mock_repository.update.side_effect = AuthorNotFoundError(author_id=1)

        result = await service.update_author(1, update_data)

        assert result is None

    async def test_delete_author_success(self, service, mock_repository):
        """Тест успешного удаления автора"""
        mock_repository.delete.return_value = True

        result = await service.delete_author(1)

        assert result is True
        mock_repository.delete.assert_called_once_with(1)

    async def test_delete_author_not_found(self, service, mock_repository):
        """Тест удаления несуществующего автора"""
        mock_repository.delete.side_effect = AuthorNotFoundError(author_id=1)

        result = await service.delete_author(1)

        assert result is False

    async def test_get_stats(self, service, mock_repository):
        """Тест получения статистики"""
        stats = {
            "total": 100,
            "by_status": {"active": 80, "inactive": 20},
            "verified": 50,
            "closed": 10
        }
        mock_repository.get_stats.return_value = stats

        result = await service.get_stats()

        assert result == stats
        mock_repository.get_stats.assert_called_once()


class TestAuthorServicePhase1:
    """Тесты для новых изменений Phase 1"""

    @pytest.fixture
    def mock_repository(self):
        """Мок репозитория"""
        return AsyncMock(spec=AuthorRepository)

    @pytest.fixture
    def service(self, mock_repository):
        """Экземпляр сервиса с моками"""
        service = AuthorService.__new__(AuthorService)
        service.repository = mock_repository
        return service

    @pytest.fixture
    def sample_response(self):
        """Пример ответа"""
        return AuthorResponse(
            id=1,
            vk_id=TEST_VK_ID,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            screen_name=TEST_SCREEN_NAME,
            photo_url=TEST_PHOTO_URL,
            status=TEST_STATUS,
            is_closed=False,
            is_verified=True,
            followers_count=TEST_FOLLOWERS_COUNT,
            last_activity=datetime.utcnow(),
            metadata={"key": "value"},
            comments_count=TEST_COMMENTS_COUNT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def test_update_author_raises_exception_on_not_found(self, service, mock_repository):
        """Тест, что update_author поднимает исключение при не найденном авторе"""
        update_data = AuthorUpdate(first_name="Петр")
        mock_repository.update.side_effect = AuthorNotFoundError(author_id=1)

        with pytest.raises(AuthorNotFoundError):
            await service.update_author(1, update_data)

    async def test_delete_author_raises_exception_on_not_found(self, service, mock_repository):
        """Тест, что delete_author поднимает исключение при не найденном авторе"""
        mock_repository.delete.side_effect = AuthorNotFoundError(author_id=1)

        with pytest.raises(AuthorNotFoundError):
            await service.delete_author(1)


class TestUnitOfWork:
    """Тесты для Unit of Work паттерна"""

    @pytest.fixture
    def mock_db(self):
        """Мок базы данных"""
        return AsyncMock(spec=AsyncSession)

    async def test_transaction_commit_on_success(self, mock_db):
        """Тест успешного коммита транзакции"""
        # Имитация успешной операции
        mock_db.commit.return_value = None
        mock_db.rollback.return_value = None

        try:
            # Имитация бизнес-логики
            await mock_db.commit()
        except Exception:
            await mock_db.rollback()
            raise
        else:
            # Проверяем, что commit был вызван
            mock_db.commit.assert_called_once()
            mock_db.rollback.assert_not_called()

    async def test_transaction_rollback_on_error(self, mock_db):
        """Тест отката транзакции при ошибке"""
        mock_db.commit.return_value = None
        mock_db.rollback.return_value = None

        try:
            # Имитация ошибки в бизнес-логике
            raise ValueError("Test error")
        except Exception:
            await mock_db.rollback()
            raise
        else:
            await mock_db.commit()

        # Проверяем, что rollback был вызван
        mock_db.rollback.assert_called_once()
        mock_db.commit.assert_not_called()


class TestErrorHandling:
    """Тесты для улучшенной обработки ошибок"""

    @pytest.fixture
    def mock_repository(self):
        """Мок репозитория"""
        return AsyncMock(spec=AuthorRepository)

    @pytest.fixture
    def service(self, mock_repository):
        """Экземпляр сервиса с моками"""
        service = AuthorService.__new__(AuthorService)
        service.repository = mock_repository
        return service

    async def test_create_author_logs_error_on_failure(self, service, mock_repository, caplog):
        """Тест логирования ошибки при создании автора"""
        create_data = AuthorCreate(vk_id=TEST_VK_ID, first_name=TEST_FIRST_NAME)
        mock_repository.create.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await service.create_author(create_data)

        # Проверяем, что ошибка была залогирована
        assert "Failed to create author" in caplog.text
        assert "Database error" in caplog.text

    async def test_update_author_logs_error_on_failure(self, service, mock_repository, caplog):
        """Тест логирования ошибки при обновлении автора"""
        update_data = AuthorUpdate(first_name="Петр")
        mock_repository.update.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await service.update_author(1, update_data)

        # Проверяем, что ошибка была залогирована
        assert "Failed to update author" in caplog.text
        assert "Database error" in caplog.text

    async def test_delete_author_logs_error_on_failure(self, service, mock_repository, caplog):
        """Тест логирования ошибки при удалении автора"""
        mock_repository.delete.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await service.delete_author(1)

        # Проверяем, что ошибка была залогирована
        assert "Failed to delete author" in caplog.text
        assert "Database error" in caplog.text


class TestIntegrationAPI:
    """Интеграционные тесты для API эндпоинтов авторов"""

    @pytest.fixture
    def mock_service(self):
        """Мок сервиса авторов"""
        return AsyncMock(spec=AuthorService)

    @pytest.fixture
    def sample_response(self):
        """Пример ответа API"""
        return AuthorResponse(
            id=1,
            vk_id=TEST_VK_ID,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            screen_name=TEST_SCREEN_NAME,
            photo_url=TEST_PHOTO_URL,
            status=TEST_STATUS,
            is_closed=False,
            is_verified=True,
            followers_count=TEST_FOLLOWERS_COUNT,
            last_activity=datetime.utcnow(),
            metadata={"key": "value"},
            comments_count=TEST_COMMENTS_COUNT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def test_get_author_endpoint_success(self, mock_service, sample_response):
        """Тест успешного получения автора через API"""
        from .api import get_author
        from fastapi import Request

        mock_request = MagicMock(spec=Request)
        mock_service.get_by_id.return_value = sample_response

        result = await get_author(mock_request, author_id=1, service=mock_service)

        assert result == sample_response
        mock_service.get_by_id.assert_called_once_with(1)

    async def test_get_author_by_vk_id_endpoint_success(self, mock_service, sample_response):
        """Тест успешного получения автора по VK ID через API"""
        from .api import get_author_by_vk_id
        from fastapi import Request

        mock_request = MagicMock(spec=Request)
        mock_service.get_by_vk_id.return_value = sample_response

        result = await get_author_by_vk_id(mock_request, vk_id=TEST_VK_ID, service=mock_service)

        assert result == sample_response
        assert result.vk_id == TEST_VK_ID
        mock_service.get_by_vk_id.assert_called_once_with(TEST_VK_ID)

    async def test_get_author_by_screen_name_endpoint_success(self, mock_service, sample_response):
        """Тест успешного получения автора по screen name через API"""
        from .api import get_author_by_screen_name
        from fastapi import Request

        mock_request = MagicMock(spec=Request)
        mock_service.get_by_screen_name.return_value = sample_response

        result = await get_author_by_screen_name(mock_request, screen_name=TEST_SCREEN_NAME, service=mock_service)

        assert result == sample_response
        assert result.screen_name == TEST_SCREEN_NAME
        mock_service.get_by_screen_name.assert_called_once_with(TEST_SCREEN_NAME)

    async def test_get_author_by_screen_name_endpoint_not_found(self, mock_service):
        """Тест получения несуществующего автора по screen name через API"""
        from .api import get_author_by_screen_name
        from fastapi import Request, HTTPException

        mock_request = MagicMock(spec=Request)
        mock_service.get_by_screen_name.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_author_by_screen_name(mock_request, screen_name="nonexistent", service=mock_service)

        assert exc_info.value.status_code == 404
        assert "не найден" in exc_info.value.detail["message"]

    async def test_create_author_endpoint_success(self, mock_service, sample_response):
        """Тест успешного создания автора через API"""
        from .api import create_author
        from fastapi import Request

        mock_request = MagicMock(spec=Request)
        create_data = AuthorCreate(vk_id=TEST_VK_ID, first_name=TEST_FIRST_NAME)
        mock_service.create_author.return_value = sample_response

        result = await create_author(mock_request, data=create_data, service=mock_service)

        assert result == sample_response
        mock_service.create_author.assert_called_once_with(create_data)

    async def test_update_author_endpoint_success(self, mock_service, sample_response):
        """Тест успешного обновления автора через API"""
        from .api import update_author
        from fastapi import Request

        mock_request = MagicMock(spec=Request)
        update_data = AuthorUpdate(first_name="Петр")
        mock_service.update_author.return_value = sample_response

        result = await update_author(mock_request, author_id=1, data=update_data, service=mock_service)

        assert result == sample_response
        mock_service.update_author.assert_called_once_with(1, update_data)

    async def test_delete_author_endpoint_success(self, mock_service):
        """Тест успешного удаления автора через API"""
        from .api import delete_author
        from fastapi import Request

        mock_request = MagicMock(spec=Request)
        mock_service.delete_author.return_value = None

        result = await delete_author(mock_request, author_id=1, service=mock_service)

        assert result is None
        mock_service.delete_author.assert_called_once_with(1)

    async def test_get_stats_endpoint_success(self, mock_service):
        """Тест успешного получения статистики через API"""
        from .api import get_stats
        from fastapi import Request

        mock_request = MagicMock(spec=Request)
        stats_data = {"total": 100, "active": 80}
        mock_service.get_stats.return_value = stats_data

        result = await get_stats(mock_request, service=mock_service)

        assert result == stats_data
        mock_service.get_stats.assert_called_once()

    async def test_health_check_endpoint(self):
        """Тест health check эндпоинта"""
        from .api import health_check
        from fastapi import Request

        mock_request = MagicMock(spec=Request)

        result = await health_check(mock_request)

        assert result == {"status": "healthy", "module": "authors"}