"""
Интеграционные тесты для API VK Comments Parser

Проверяют взаимодействие между компонентами:
- API endpoints
- Сервисы
- База данных
- Внешние API
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.group_manager import GroupManager
from app.services.comment_service import CommentService
from app.services.keyword_service import KeywordService


class TestAPIIntegration:
    """
    Интеграционные тесты для проверки взаимодействия API компонентов.
    """

    @pytest.fixture
    async def client(self):
        """Фикстура для HTTP клиента"""
        from app.main import app

        async with AsyncClient(
            app=app, base_url="http://testserver"
        ) as client:
            yield client

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

    @pytest.fixture
    def keyword_service(self):
        """Фикстура для KeywordService"""
        return KeywordService()

    async def test_api_root_endpoint(self, client):
        """Тест корневого endpoint API"""
        response = await client.get("/api/v1/")

        assert response.status_code == 200
        data = response.json()

        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert "features" in data
        assert "architecture" in data
        assert "documentation" in data

        # Проверяем версию
        assert data["version"] == "2.0.0"
        assert "SOLID" in data["status"]

    async def test_health_endpoint(self, client, db_session):
        """Тест health check endpoint"""
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data

        # Проверяем что основные сервисы загружены
        services = data["services"]
        assert "database" in services
        assert "comment_service" in services
        assert "group_manager" in services
        assert "vk_api_service" in services

        # Статус должен быть healthy или degraded (но не unhealthy)
        assert data["status"] in ["healthy", "degraded"]

    async def test_error_handling_validation(self, client):
        """Тест обработки ошибок валидации"""
        # Отправляем некорректные данные для создания группы
        response = await client.post(
            "/api/v1/groups/", json={"invalid_field": "invalid_value"}
        )

        assert response.status_code == 422  # Validation error
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

    async def test_error_handling_not_found(self, client):
        """Тест обработки ошибок 404"""
        response = await client.get("/api/v1/groups/99999")

        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

    async def test_groups_api_integration(
        self, client, db_session, group_manager
    ):
        """Интеграционный тест Groups API"""
        # Тестируем получение списка групп
        response = await client.get("/api/v1/groups/")
        assert response.status_code == 200

        # Тестируем создание группы через сервис
        group_data = {
            "vk_id_or_screen_name": "test_group",
            "is_active": True,
            "max_posts_to_check": 10,
        }

        # Создаем группу через сервис
        created_group = await group_manager.create_group(
            db_session, group_data
        )
        assert created_group is not None
        assert created_group.screen_name == "test_group"

        # Проверяем что группа доступна через API
        group_id = created_group.id
        response = await client.get(f"/api/v1/groups/{group_id}")
        assert response.status_code == 200

        group_data = response.json()
        assert group_data["screen_name"] == "test_group"
        assert group_data["is_active"] == True

    async def test_comments_api_integration(self, client, comment_service):
        """Интеграционный тест Comments API"""
        # Тестируем получение комментариев
        response = await client.get("/api/v1/comments/")
        assert response.status_code == 200

        # Тестируем поиск комментариев
        response = await client.get("/api/v1/comments/search/?q=test")
        assert response.status_code == 200

    async def test_keywords_api_integration(self, client, keyword_service):
        """Интеграционный тест Keywords API"""
        # Тестируем получение ключевых слов
        response = await client.get("/api/v1/keywords/")
        assert response.status_code == 200

        # Тестируем создание ключевого слова через сервис
        keyword_data = {
            "text": "test_keyword",
            "is_active": True,
            "category": "test",
        }

        # Проверяем что API доступен
        response = await client.post("/api/v1/keywords/", json=keyword_data)
        # Может быть 201 (создано) или 422 (валидация) или другой код в зависимости от данных
        assert response.status_code in [200, 201, 422]

    async def test_monitoring_api_integration(self, client):
        """Интеграционный тест Monitoring API"""
        # Тестируем получение статуса мониторинга
        response = await client.get("/api/v1/monitoring/status")
        assert response.status_code in [
            200,
            404,
        ]  # 404 если нет активных задач

    async def test_settings_api_integration(self, client):
        """Интеграционный тест Settings API"""
        # Тестируем получение настроек
        response = await client.get("/api/v1/settings/")
        assert response.status_code == 200

        data = response.json()
        assert "version" in data
        assert "environment" in data

    async def test_parser_api_integration(self, client):
        """Интеграционный тест Parser API"""
        # Тестируем получение статуса парсера
        response = await client.get("/api/v1/parser/status")
        assert response.status_code in [
            200,
            404,
        ]  # 404 если нет активных задач

    async def test_morphological_api_integration(self, client):
        """Интеграционный тест Morphological API"""
        # Тестируем морфологический анализ
        response = await client.get("/api/v1/morphological/analyze?word=test")
        assert response.status_code in [
            200,
            422,
        ]  # 422 если параметры некорректны

    async def test_cors_headers(self, client):
        """Тест CORS заголовков"""
        response = await client.options("/api/v1/")

        # Проверяем CORS заголовки
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    async def test_request_logging(self, client):
        """Тест логирования запросов"""
        response = await client.get("/api/v1/health")

        # Проверяем что добавлен заголовок с временем выполнения
        assert "x-process-time" in response.headers

        # Проверяем что время выполнения положительное число
        process_time = float(response.headers["x-process-time"])
        assert process_time > 0

    async def test_database_integration(self, db_session):
        """Тест интеграции с базой данных"""
        # Выполняем простой запрос
        result = await db_session.execute("SELECT 1 as test")
        row = result.fetchone()

        assert row is not None
        assert row.test == 1

    async def test_services_initialization(
        self, group_manager, comment_service, keyword_service
    ):
        """Тест инициализации сервисов"""
        # Проверяем что сервисы правильно инициализированы
        assert group_manager is not None
        assert hasattr(group_manager, "create_group")
        assert hasattr(group_manager, "get_groups_count")

        assert comment_service is not None
        assert hasattr(comment_service, "get_comments")

        assert keyword_service is not None
        assert hasattr(keyword_service, "get_keywords")
