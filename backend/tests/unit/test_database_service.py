"""
Unit tests for database service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError

from app.core.database_service import DatabaseService
from app.core.exceptions import DatabaseError


class TestDatabaseService:
    """Test database service functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        mock = AsyncMock()
        mock.execute = AsyncMock()
        mock.commit = AsyncMock()
        mock.rollback = AsyncMock()
        mock.close = AsyncMock()
        return mock

    @pytest.fixture
    def mock_engine(self):
        """Create mock database engine."""
        mock = MagicMock()
        mock.pool = MagicMock()
        mock.pool.checkedout = MagicMock(return_value=5)
        mock.pool.checkedin = MagicMock(return_value=10)
        mock.pool.overflow = MagicMock(return_value=2)
        mock.pool.size = MagicMock(return_value=15)
        return mock

    @pytest.fixture
    def db_service(self, mock_engine):
        """Create database service with mock engine."""
        with patch(
            "app.core.database_service.get_async_engine",
            return_value=mock_engine,
        ):
            return DatabaseService()

    @pytest.fixture
    def mock_model(self):
        """Create mock SQLAlchemy model."""
        mock = MagicMock()
        mock.__name__ = "TestModel"
        mock.id = MagicMock()
        return mock

    @pytest.mark.asyncio
    async def test_get_session_success(self, db_service, mock_session):
        """Test successful session creation and cleanup."""
        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            async with db_service.get_session() as session:
                assert session == mock_session

            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_error(self, db_service, mock_session):
        """Test session error handling."""
        mock_session.execute.side_effect = Exception("Database error")

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            with pytest.raises(
                DatabaseError, match="Database operation failed"
            ):
                async with db_service.get_session() as session:
                    await session.execute("SELECT 1")

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_success(self, db_service, mock_session):
        """Test successful query execution."""
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.execute_query("SELECT 1")

            assert result == mock_result
            mock_session.execute.assert_called_once_with("SELECT 1", {})

    @pytest.mark.asyncio
    async def test_execute_query_timeout(self, db_service, mock_session):
        """Test query timeout handling."""
        mock_session.execute.side_effect = Exception("Timeout")

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            with pytest.raises(DatabaseError, match="Query timeout"):
                await db_service.execute_query("SELECT 1", timeout=0.1)

    @pytest.mark.asyncio
    async def test_execute_query_error(self, db_service, mock_session):
        """Test query error handling."""
        mock_session.execute.side_effect = SQLAlchemyError("Database error")

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            with pytest.raises(DatabaseError, match="Database query failed"):
                await db_service.execute_query("SELECT 1")

    @pytest.mark.asyncio
    async def test_get_by_id_success(
        self, db_service, mock_session, mock_model
    ):
        """Test getting entity by ID successfully."""
        mock_instance = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            mock_instance
        )

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.get_by_id(mock_model, 123)

            assert result == mock_instance
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_with_relationships(
        self, db_service, mock_session, mock_model
    ):
        """Test getting entity by ID with relationship loading."""
        mock_instance = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            mock_instance
        )

        # Mock relationship attribute
        mock_model.relationship = MagicMock()

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.get_by_id(
                mock_model, 123, load_relationships=["relationship"]
            )

            assert result == mock_instance
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_error(self, db_service, mock_session, mock_model):
        """Test getting entity by ID with error."""
        mock_session.execute.side_effect = SQLAlchemyError("Database error")

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            with pytest.raises(
                DatabaseError, match="Failed to get TestModel by ID"
            ):
                await db_service.get_by_id(mock_model, 123)

    @pytest.mark.asyncio
    async def test_get_many_by_ids_success(
        self, db_service, mock_session, mock_model
    ):
        """Test getting multiple entities by IDs successfully."""
        mock_instances = [MagicMock(), MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_instances
        )

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.get_many_by_ids(mock_model, [123, 456])

            assert result == mock_instances
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_many_by_ids_empty(self, db_service, mock_model):
        """Test getting multiple entities with empty ID list."""
        result = await db_service.get_many_by_ids(mock_model, [])

        assert result == []

    @pytest.mark.asyncio
    async def test_create_success(self, db_service, mock_session, mock_model):
        """Test creating entity successfully."""
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.create(mock_model, {"name": "test"})

            assert result == mock_instance
            mock_session.add.assert_called_once_with(mock_instance)
            mock_session.flush.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_instance)

    @pytest.mark.asyncio
    async def test_create_error(self, db_service, mock_session, mock_model):
        """Test creating entity with error."""
        mock_session.flush.side_effect = SQLAlchemyError("Database error")
        mock_model.return_value = MagicMock()

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            with pytest.raises(
                DatabaseError, match="Failed to create TestModel"
            ):
                await db_service.create(mock_model, {"name": "test"})

    @pytest.mark.asyncio
    async def test_bulk_create_success(
        self, db_service, mock_session, mock_model
    ):
        """Test bulk creating entities successfully."""
        mock_instances = [MagicMock(), MagicMock()]
        mock_model.side_effect = mock_instances

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.bulk_create(
                mock_model, [{"name": "test1"}, {"name": "test2"}]
            )

            assert result == mock_instances
            mock_session.add_all.assert_called_once_with(mock_instances)
            mock_session.flush.assert_called_once()
            assert mock_session.refresh.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_create_empty(self, db_service, mock_model):
        """Test bulk creating entities with empty data list."""
        result = await db_service.bulk_create(mock_model, [])

        assert result == []

    @pytest.mark.asyncio
    async def test_update_success(self, db_service, mock_session, mock_model):
        """Test updating entity successfully."""
        mock_session.execute.return_value.rowcount = 1

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            with patch.object(
                db_service, "get_by_id", return_value=MagicMock()
            ):
                result = await db_service.update(
                    mock_model, 123, {"name": "updated"}
                )

                assert result is not None
                mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(
        self, db_service, mock_session, mock_model
    ):
        """Test updating entity that doesn't exist."""
        mock_session.execute.return_value.rowcount = 0

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.update(
                mock_model, 123, {"name": "updated"}
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_bulk_update_success(
        self, db_service, mock_session, mock_model
    ):
        """Test bulk updating entities successfully."""
        mock_session.execute.return_value.rowcount = 1

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.bulk_update(
                mock_model,
                [
                    {"id": 123, "name": "updated1"},
                    {"id": 456, "name": "updated2"},
                ],
            )

            assert result == 2
            assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_success(self, db_service, mock_session, mock_model):
        """Test deleting entity successfully."""
        mock_session.execute.return_value.rowcount = 1

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.delete(mock_model, 123)

            assert result is True
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(
        self, db_service, mock_session, mock_model
    ):
        """Test deleting entity that doesn't exist."""
        mock_session.execute.return_value.rowcount = 0

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.delete(mock_model, 123)

            assert result is False

    @pytest.mark.asyncio
    async def test_count_success(self, db_service, mock_session, mock_model):
        """Test counting entities successfully."""
        mock_session.execute.return_value.scalar.return_value = 10

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.count(mock_model)

            assert result == 10
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_with_filters(
        self, db_service, mock_session, mock_model
    ):
        """Test counting entities with filters."""
        mock_session.execute.return_value.scalar.return_value = 5

        # Mock filter attribute
        mock_model.status = MagicMock()

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.count(
                mock_model, filters={"status": "active"}
            )

            assert result == 5
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_success(self, db_service, mock_session, mock_model):
        """Test checking entity existence successfully."""
        mock_session.execute.return_value.scalar.return_value = 123

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.exists(mock_model, {"id": 123})

            assert result is True
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_not_found(
        self, db_service, mock_session, mock_model
    ):
        """Test checking entity existence when not found."""
        mock_session.execute.return_value.scalar.return_value = None

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.exists(mock_model, {"id": 123})

            assert result is False

    @pytest.mark.asyncio
    async def test_get_pool_stats(self, db_service, mock_engine):
        """Test getting connection pool statistics."""
        db_service.engine = mock_engine

        stats = await db_service.get_pool_stats()

        assert "checked_out" in stats
        assert "checked_in" in stats
        assert "overflow" in stats
        assert "size" in stats

    @pytest.mark.asyncio
    async def test_health_check_success(self, db_service, mock_session):
        """Test database health check success."""
        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.health_check()

            assert result is True
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, db_service, mock_session):
        """Test database health check failure."""
        mock_session.execute.side_effect = Exception("Connection failed")

        with patch(
            "app.core.database_service.AsyncSessionLocal",
            return_value=mock_session,
        ):
            result = await db_service.health_check()

            assert result is False
