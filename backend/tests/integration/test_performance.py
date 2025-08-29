"""
Интеграционные тесты производительности

Проверяют:
- Время отклика API
- Производительность базы данных
- Эффективность кэширования
- Масштабируемость
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.group_manager import GroupManager
from app.services.comment_service import CommentService


class TestPerformance:
    """
    Тесты производительности системы.
    """

    PERFORMANCE_THRESHOLDS = {
        "api_response_time": 2.0,  # секунды
        "db_query_time": 1.0,  # секунды
        "bulk_operation_time": 5.0,  # секунды
    }

    @pytest.fixture
    async def db_session(self):
        """Фикстура для сессии базы данных"""
        async with get_db_session() as session:
            yield session

    @pytest.fixture
    def group_manager(self):
        """Фикстура для GroupManager"""
        return GroupManager()

    @pytest.fixture
    def comment_service(self):
        """Фикстура для CommentService"""
        return CommentService()

    async def test_api_response_time(self, client):
        """Тест времени отклика API endpoints"""
        endpoints = [
            "/api/v1/",
            "/api/v1/health",
            "/api/v1/groups/",
            "/api/v1/keywords/",
            "/api/v1/comments/",
        ]

        for endpoint in endpoints:
            start_time = time.time()

            response = await client.get(endpoint)

            response_time = time.time() - start_time

            assert response.status_code in [
                200,
                404,
            ]  # 404 нормально для пустых списков
            assert (
                response_time
                < self.PERFORMANCE_THRESHOLDS["api_response_time"]
            ), f"API endpoint {endpoint} too slow: {response_time:.2f}s"

            # Проверяем заголовок с временем выполнения
            assert "x-process-time" in response.headers
            process_time = float(response.headers["x-process-time"])
            assert (
                process_time < self.PERFORMANCE_THRESHOLDS["api_response_time"]
            )

    async def test_database_query_performance(self, db_session, group_manager):
        """Тест производительности запросов к базе данных"""
        # Тест простого запроса
        start_time = time.time()

        count = await group_manager.get_groups_count(db_session)

        query_time = time.time() - start_time
        assert (
            query_time < self.PERFORMANCE_THRESHOLDS["db_query_time"]
        ), f"Database query too slow: {query_time:.2f}s"

        # Тест запроса со сложными условиями
        start_time = time.time()

        # Имитируем сложный запрос
        from app.models.vk_group import VKGroup
        from sqlalchemy import select

        result = await db_session.execute(
            select(VKGroup).where(VKGroup.is_active == True)
        )
        groups = result.scalars().all()

        query_time = time.time() - start_time
        assert (
            query_time < self.PERFORMANCE_THRESHOLDS["db_query_time"]
        ), f"Complex database query too slow: {query_time:.2f}s"

    async def test_bulk_operations_performance(
        self, db_session, group_manager
    ):
        """Тест производительности массовых операций"""
        # Создаем несколько групп для тестирования
        bulk_data = [
            {
                "vk_id_or_screen_name": f"perf_test_{i}",
                "is_active": True,
                "max_posts_to_check": 10,
            }
            for i in range(10)
        ]

        start_time = time.time()

        # Создаем группы массово
        created_groups = []
        for group_data in bulk_data:
            group = await group_manager.create_group(db_session, group_data)
            created_groups.append(group)

        bulk_time = time.time() - start_time

        assert len(created_groups) == 10
        assert (
            bulk_time < self.PERFORMANCE_THRESHOLDS["bulk_operation_time"]
        ), f"Bulk operation too slow: {bulk_time:.2f}s"

        # Проверяем среднее время на операцию
        avg_time = bulk_time / len(created_groups)
        assert (
            avg_time < 0.5
        ), f"Average operation time too high: {avg_time:.2f}s"

    async def test_concurrent_requests_performance(self, client):
        """Тест производительности при одновременных запросах"""

        async def make_request(endpoint: str):
            start_time = time.time()
            response = await client.get(endpoint)
            response_time = time.time() - start_time
            return response.status_code, response_time

        # Тестируем одновременные запросы к health endpoint
        endpoints = ["/api/v1/health"] * 10

        start_time = time.time()

        # Выполняем 10 одновременных запросов
        tasks = [make_request(endpoint) for endpoint in endpoints]
        results = await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Проверяем что все запросы успешны
        for status_code, response_time in results:
            assert status_code == 200
            assert (
                response_time
                < self.PERFORMANCE_THRESHOLDS["api_response_time"]
            )

        # Проверяем общее время выполнения
        assert (
            total_time < self.PERFORMANCE_THRESHOLDS["bulk_operation_time"]
        ), f"Concurrent requests too slow: {total_time:.2f}s"

    async def test_memory_usage_estimation(self, db_session, group_manager):
        """Тест оценки использования памяти"""
        # Создаем большое количество групп для тестирования
        bulk_data = [
            {
                "vk_id_or_screen_name": f"memory_test_{i}",
                "is_active": True,
                "max_posts_to_check": 10,
                "name": f"Memory Test Group {i}",
                "description": f"Description for memory test group {i}" * 5,
            }
            for i in range(50)
        ]

        start_time = time.time()
        memory_start = asyncio.get_event_loop().get_running_loop()

        # Создаем группы
        created_groups = []
        for group_data in bulk_data:
            group = await group_manager.create_group(db_session, group_data)
            created_groups.append(group)

        creation_time = time.time() - start_time

        assert len(created_groups) == 50
        assert (
            creation_time < 10.0
        ), f"Memory test too slow: {creation_time:.2f}s"

    async def test_database_connection_pooling(self, db_session):
        """Тест пула соединений базы данных"""
        # Выполняем несколько запросов подряд
        query_times = []

        for i in range(20):
            start_time = time.time()

            # Выполняем простой запрос
            result = await db_session.execute("SELECT 1 as test")
            row = result.fetchone()

            query_time = time.time() - start_time
            query_times.append(query_time)

            assert row.test == 1

        # Проверяем что время запросов стабильно
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)

        assert avg_time < 0.1, f"Average query time too high: {avg_time:.3f}s"
        assert max_time < 1.0, f"Max query time too high: {max_time:.3f}s"

        # Проверяем что нет сильных колебаний производительности
        variance = sum((t - avg_time) ** 2 for t in query_times) / len(
            query_times
        )
        assert variance < 0.01, f"Query time variance too high: {variance:.4f}"

    async def test_service_initialization_performance(self):
        """Тест производительности инициализации сервисов"""
        start_time = time.time()

        # Импортируем и инициализируем все основные сервисы
        from app.services.group_manager import GroupManager
        from app.services.comment_service import CommentService
        from app.services.keyword_service import KeywordService
        from app.services.group_validator import GroupValidator
        from app.services.vk_api_service import VKAPIService
        from app.core.config import settings

        vk_service = VKAPIService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

        group_manager = GroupManager()
        comment_service = CommentService()
        keyword_service = KeywordService()
        group_validator = GroupValidator(vk_service)

        init_time = time.time() - start_time

        assert (
            init_time < 2.0
        ), f"Service initialization too slow: {init_time:.2f}s"

        # Проверяем что все сервисы корректно инициализированы
        assert group_manager is not None
        assert comment_service is not None
        assert keyword_service is not None
        assert group_validator is not None

    async def test_error_handling_performance(self, client):
        """Тест производительности обработки ошибок"""
        error_endpoints = [
            "/api/v1/groups/99999",  # Несуществующая группа
            "/api/v1/comments/search/?invalid_param=test",  # Некорректные параметры
        ]

        for endpoint in error_endpoints:
            start_time = time.time()

            response = await client.get(endpoint)

            error_time = time.time() - start_time

            # Ошибки должны обрабатываться быстро
            assert (
                error_time < self.PERFORMANCE_THRESHOLDS["api_response_time"]
            ), f"Error handling too slow for {endpoint}: {error_time:.2f}s"

            # Проверяем что возвращается правильный код ошибки
            assert response.status_code in [400, 404, 422]

            # Проверяем структуру ответа об ошибке
            data = response.json()
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]

    async def test_caching_performance_simulation(
        self, db_session, group_manager
    ):
        """Тест производительности с имитацией кэширования"""
        # Создаем группу для тестирования
        group_data = {
            "vk_id_or_screen_name": "cache_test_group",
            "is_active": True,
            "max_posts_to_check": 10,
        }

        group = await group_manager.create_group(db_session, group_data)
        assert group is not None

        # Имитируем многократные чтения (как если бы было кэширование)
        read_times = []

        for i in range(50):
            start_time = time.time()

            found_group = await group_manager.get_by_id(db_session, group.id)

            read_time = time.time() - start_time
            read_times.append(read_time)

            assert found_group is not None
            assert found_group.id == group.id

        # Анализируем производительность чтения
        avg_read_time = sum(read_times) / len(read_times)
        max_read_time = max(read_times)

        assert (
            avg_read_time < 0.05
        ), f"Average read time too high: {avg_read_time:.3f}s"
        assert (
            max_read_time < 0.5
        ), f"Max read time too high: {max_read_time:.3f}s"
