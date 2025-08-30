"""
Глобальная конфигурация базы данных VK Comments Parser

Мигрировано из app/api/v1/infrastructure/services/database_service.py
в соответствии с fastapi-best-practices
"""

from functools import lru_cache
from typing import AsyncGenerator, Dict, Any, Optional
from contextlib import asynccontextmanager

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import config_service


# Единая конвенция для именования индексов и ключей
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


# Base class для моделей
class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    metadata = metadata


class DatabaseService:
    """
    Сервис для работы с базой данных

    Предоставляет унифицированный интерфейс для работы с БД
    """

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker] = None
        self._initialized = False

    @property
    def engine(self) -> AsyncEngine:
        """Получить движок базы данных"""
        if not self._engine:
            self._init_engine()
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker:
        """Получить фабрику сессий"""
        if not self._session_maker:
            self._init_session_maker()
        return self._session_maker

    def _init_engine(self) -> None:
        """Инициализировать движок базы данных"""
        db_config = config_service.get_database_config()

        self._engine = create_async_engine(
            db_config["url"],
            echo=config_service.debug,
            pool_size=db_config.get("pool_size", 10),
            max_overflow=db_config.get("max_overflow", 20),
            pool_pre_ping=db_config.get("pool_pre_ping", True),
            pool_recycle=db_config.get("pool_recycle", 3600),
            connect_args=db_config.get(
                "connect_args",
                {"server_settings": {"application_name": "vk_parser_backend"}},
            ),
        )

    def _init_session_maker(self) -> None:
        """Инициализировать фабрику сессий"""
        if not self._engine:
            self._init_engine()

        self._session_maker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def init_database(self) -> None:
        """Инициализация базы данных с оптимизацией и повторными попытками подключения"""
        if self._initialized:
            return

        import asyncio
        import logging

        logger = logging.getLogger(__name__)
        max_retries = 10
        delay = 2  # секунд между попытками

        for attempt in range(1, max_retries + 1):
            try:
                # Проверяем подключение
                async with self.engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                break  # успех, выходим из цикла
            except Exception as e:
                logger.warning(
                    f"Database initialization attempt {attempt} failed: {e}"
                )
                if attempt == max_retries:
                    logger.error(
                        "Max retries reached. Could not connect to the database."
                    )
                    raise
                await asyncio.sleep(delay)

        self._initialized = True
        logger.info("Database initialized successfully")

    async def close_database(self) -> None:
        """Закрыть соединения с базой данных"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None
            self._initialized = False

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получить сессию базы данных (контекстный менеджер)"""
        if not self._session_maker:
            self._init_session_maker()

        async with self._session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_async_session(self) -> AsyncSession:
        """Получение асинхронной сессии для ARQ задач"""
        if not self._session_maker:
            self._init_session_maker()
        return self._session_maker()

    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья базы данных"""
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1 as test"))
                row = result.first()
                success = row is not None and row.test == 1

            return {
                "status": "healthy" if success else "unhealthy",
                "database_url": config_service.database_url,
                "connection_pool": {
                    "size": self.engine.pool.size(),
                    "checkedin": self.engine.pool.checkedin(),
                    "checkedout": self.engine.pool.checkedout(),
                    "overflow": self.engine.pool.overflow(),
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_url": config_service.database_url,
            }

    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику базы данных"""
        try:
            async with self.get_session() as session:
                # Получить количество таблиц
                tables_result = await session.execute(
                    text(
                        """
                    SELECT COUNT(*) as table_count
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """
                    )
                )
                tables_row = tables_result.first()

                # Получить размер базы данных
                size_result = await session.execute(
                    text(
                        """
                    SELECT
                        pg_size_pretty(pg_database_size(current_database())) as db_size,
                        pg_database_size(current_database()) as db_size_bytes
                """
                    )
                )
                size_row = size_result.first()

                return {
                    "database_name": config_service.database_url.split("/")[
                        -1
                    ],
                    "table_count": tables_row.table_count if tables_row else 0,
                    "database_size": (
                        size_row.db_size if size_row else "unknown"
                    ),
                    "database_size_bytes": (
                        size_row.db_size_bytes if size_row else 0
                    ),
                    "connection_pool": {
                        "size": self.engine.pool.size(),
                        "checkedin": self.engine.pool.checkedin(),
                        "checkedout": self.engine.pool.checkedout(),
                        "overflow": self.engine.pool.overflow(),
                    },
                }
        except Exception as e:
            return {
                "error": str(e),
                "database_name": "unknown",
            }

    async def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Выполнить произвольный SQL запрос"""
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result

    async def execute_read_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Выполнить SELECT запрос"""
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            return result.fetchall()


# Глобальный экземпляр сервиса базы данных
@lru_cache(maxsize=1)
def get_database_service() -> DatabaseService:
    """Получить экземпляр сервиса базы данных (кешируется)"""
    return DatabaseService()


# Глобальный объект для обратной совместимости
database_service = get_database_service()


# Функции для получения сессии (для использования в зависимостях FastAPI)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость FastAPI для получения сессии БД"""
    async with database_service.get_session() as session:
        yield session


async def get_db() -> AsyncSession:
    """Получить сессию БД для использования в сервисах"""
    return database_service.session_maker()
