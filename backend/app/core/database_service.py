"""
Optimized database service with connection pooling and query optimization.
Provides enhanced database operations with performance monitoring.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import delete, func, select, text, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from structlog import get_logger

from .database import AsyncSessionLocal, get_async_engine
from .exceptions import DatabaseError

logger = get_logger()

T = TypeVar("T")


class DatabaseService:
    """Optimized database service with connection pooling and monitoring."""

    def __init__(self):
        self.engine = get_async_engine()
        self._connection_pool = None
        self._pool_stats = {
            "checked_out": 0,
            "checked_in": 0,
            "overflow": 0,
            "invalid": 0,
        }

    @asynccontextmanager
    async def get_session(self):
        """Get database session with automatic cleanup."""
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise DatabaseError(f"Database operation failed: {str(e)}")
        finally:
            await session.close()

    async def execute_query(
        self,
        query,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = 30.0,
    ) -> Any:
        """
        Execute database query with timeout and error handling.

        Args:
            query: SQLAlchemy query
            params: Query parameters
            timeout: Query timeout in seconds

        Returns:
            Query result
        """
        try:
            async with asyncio.timeout(timeout):
                async with self.get_session() as session:
                    result = await session.execute(query, params or {})
                    return result
        except asyncio.TimeoutError:
            logger.error("Database query timeout", timeout=timeout)
            raise DatabaseError(f"Query timeout after {timeout} seconds")
        except SQLAlchemyError as e:
            logger.error("Database query error", error=str(e))
            raise DatabaseError(f"Database query failed: {str(e)}")

    async def get_by_id(
        self,
        model: Type[T],
        id: Any,
        load_relationships: Optional[List[str]] = None,
    ) -> Optional[T]:
        """
        Get entity by ID with optional relationship loading.

        Args:
            model: SQLAlchemy model class
            id: Entity ID
            load_relationships: List of relationship names to load

        Returns:
            Entity instance or None
        """
        query = select(model).where(model.id == id)

        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(model, rel)))

        try:
            async with self.get_session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(
                "Get by ID error", model=model.__name__, id=id, error=str(e)
            )
            raise DatabaseError(
                f"Failed to get {model.__name__} by ID: {str(e)}"
            )

    async def get_many_by_ids(
        self,
        model: Type[T],
        ids: List[Any],
        load_relationships: Optional[List[str]] = None,
    ) -> List[T]:
        """
        Get multiple entities by IDs with batch optimization.

        Args:
            model: SQLAlchemy model class
            ids: List of entity IDs
            load_relationships: List of relationship names to load

        Returns:
            List of entity instances
        """
        if not ids:
            return []

        query = select(model).where(model.id.in_(ids))

        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(model, rel)))

        try:
            async with self.get_session() as session:
                result = await session.execute(query)
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                "Get many by IDs error",
                model=model.__name__,
                ids=ids,
                error=str(e),
            )
            raise DatabaseError(
                f"Failed to get {model.__name__} by IDs: {str(e)}"
            )

    async def create(self, model: Type[T], data: Dict[str, Any]) -> T:
        """
        Create new entity with optimized insert.

        Args:
            model: SQLAlchemy model class
            data: Entity data

        Returns:
            Created entity instance
        """
        try:
            async with self.get_session() as session:
                instance = model(**data)
                session.add(instance)
                await session.flush()  # Get ID without committing
                await session.refresh(instance)
                return instance
        except SQLAlchemyError as e:
            logger.error("Create error", model=model.__name__, error=str(e))
            raise DatabaseError(f"Failed to create {model.__name__}: {str(e)}")

    async def bulk_create(
        self, model: Type[T], data_list: List[Dict[str, Any]]
    ) -> List[T]:
        """
        Bulk create entities with optimized batch insert.

        Args:
            model: SQLAlchemy model class
            data_list: List of entity data dictionaries

        Returns:
            List of created entity instances
        """
        if not data_list:
            return []

        try:
            async with self.get_session() as session:
                instances = [model(**data) for data in data_list]
                session.add_all(instances)
                await session.flush()

                # Refresh all instances to get IDs
                for instance in instances:
                    await session.refresh(instance)

                return instances
        except SQLAlchemyError as e:
            logger.error(
                "Bulk create error",
                model=model.__name__,
                count=len(data_list),
                error=str(e),
            )
            raise DatabaseError(
                f"Failed to bulk create {model.__name__}: {str(e)}"
            )

    async def update(
        self, model: Type[T], id: Any, data: Dict[str, Any]
    ) -> Optional[T]:
        """
        Update entity by ID with optimized update.

        Args:
            model: SQLAlchemy model class
            id: Entity ID
            data: Update data

        Returns:
            Updated entity instance or None
        """
        try:
            async with self.get_session() as session:
                query = update(model).where(model.id == id).values(**data)
                result = await session.execute(query)

                if result.rowcount == 0:
                    return None

                # Get updated instance
                return await self.get_by_id(model, id)
        except SQLAlchemyError as e:
            logger.error(
                "Update error", model=model.__name__, id=id, error=str(e)
            )
            raise DatabaseError(f"Failed to update {model.__name__}: {str(e)}")

    async def bulk_update(
        self, model: Type[T], updates: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk update entities with optimized batch update.

        Args:
            model: SQLAlchemy model class
            updates: List of update dictionaries with 'id' and update data

        Returns:
            Number of updated rows
        """
        if not updates:
            return 0

        try:
            async with self.get_session() as session:
                total_updated = 0
                for update_data in updates:
                    id_value = update_data.pop("id", None)
                    if id_value is not None:
                        query = (
                            update(model)
                            .where(model.id == id_value)
                            .values(**update_data)
                        )
                        result = await session.execute(query)
                        total_updated += result.rowcount

                return total_updated
        except SQLAlchemyError as e:
            logger.error(
                "Bulk update error",
                model=model.__name__,
                count=len(updates),
                error=str(e),
            )
            raise DatabaseError(
                f"Failed to bulk update {model.__name__}: {str(e)}"
            )

    async def delete(self, model: Type[T], id: Any) -> bool:
        """
        Delete entity by ID.

        Args:
            model: SQLAlchemy model class
            id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        try:
            async with self.get_session() as session:
                query = delete(model).where(model.id == id)
                result = await session.execute(query)
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(
                "Delete error", model=model.__name__, id=id, error=str(e)
            )
            raise DatabaseError(f"Failed to delete {model.__name__}: {str(e)}")

    async def count(
        self, model: Type[T], filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count entities with optional filters.

        Args:
            model: SQLAlchemy model class
            filters: Optional filter conditions

        Returns:
            Count of entities
        """
        query = select(func.count(model.id))

        if filters:
            for field, value in filters.items():
                if hasattr(model, field):
                    query = query.where(getattr(model, field) == value)

        try:
            async with self.get_session() as session:
                result = await session.execute(query)
                return result.scalar()
        except SQLAlchemyError as e:
            logger.error("Count error", model=model.__name__, error=str(e))
            raise DatabaseError(f"Failed to count {model.__name__}: {str(e)}")

    async def exists(self, model: Type[T], filters: Dict[str, Any]) -> bool:
        """
        Check if entity exists with given filters.

        Args:
            model: SQLAlchemy model class
            filters: Filter conditions

        Returns:
            True if exists, False otherwise
        """
        query = select(model.id).limit(1)

        for field, value in filters.items():
            if hasattr(model, field):
                query = query.where(getattr(model, field) == value)

        try:
            async with self.get_session() as session:
                result = await session.execute(query)
                return result.scalar() is not None
        except SQLAlchemyError as e:
            logger.error("Exists error", model=model.__name__, error=str(e))
            raise DatabaseError(
                f"Failed to check existence of {model.__name__}: {str(e)}"
            )

    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        if self.engine.pool:
            pool = self.engine.pool
            return {
                "checked_out": pool.checkedout(),
                "checked_in": pool.checkedin(),
                "overflow": pool.overflow(),
                "size": pool.size(),
                "checkedout": pool.checkedout(),
            }
        return {}

    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False


# Global database service instance
db_service = DatabaseService()
