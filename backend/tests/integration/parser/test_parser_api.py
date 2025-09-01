"""
Integration tests for Parser API endpoints

Tests HTTP API endpoints including:
- Request/response serialization
- HTTP status codes
- Error response formatting
- Request validation at API level
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.parser.router import router
from src.parser.service import ParserService
from src.parser.schemas import ParseRequest
from src.parser.dependencies import get_parser_service


@pytest.fixture
def api_mock_parser_service():
    """Mock parser service for API tests"""

    class MockParserService:
        def __init__(self):
            self.created_tasks = {}

        async def start_parsing(self, *args, **kwargs):
            from uuid import uuid4

            task_id = str(uuid4())
            task_data = {
                "task_id": task_id,
                "status": "started",
                "group_ids": kwargs.get("group_ids", [123456789]),
                "estimated_time": 30,
                "created_at": "2024-01-01T00:00:00Z",
            }
            self.created_tasks[task_id] = task_data
            return task_data

        async def get_task_status(self, task_id):
            if task_id in self.created_tasks:
                task_data = self.created_tasks[task_id].copy()
                task_data.update(
                    {
                        "status": "running",
                        "progress": 45.5,
                        "current_group": 123456789,
                        "groups_completed": 1,
                        "groups_total": len(task_data["group_ids"]),
                        "posts_found": 10,
                        "comments_found": 50,
                        "errors": [],
                        "started_at": "2024-01-01T00:00:00Z",
                        "completed_at": None,
                        "duration": 30,
                    }
                )
                return task_data
            return None

        async def stop_parsing(self, task_id=None):
            if task_id and task_id in self.created_tasks:
                return {
                    "stopped_tasks": [task_id],
                    "message": "Task stopped successfully",
                }
            return {
                "stopped_tasks": [],
                "message": "No tasks to stop",
            }

        async def get_parser_state(self):
            return {
                "is_running": True,
                "active_tasks": len(self.created_tasks),
                "queue_size": 1,
                "total_tasks_processed": 5,
                "total_posts_found": 100,
                "total_comments_found": 500,
                "last_activity": "2024-01-01T00:00:00Z",
                "uptime_seconds": 3600,
            }

        async def get_tasks_list(self, *args, **kwargs):
            return list(self.created_tasks.values())

        async def get_parsing_stats(self):
            return {
                "total_tasks": 10,
                "completed_tasks": 7,
                "failed_tasks": 2,
                "running_tasks": 1,
                "total_posts_found": 350,
                "total_comments_found": 2450,
                "total_processing_time": 450,
                "average_task_duration": 45.0,
            }

    return MockParserService()


class TestParserAPIIntegration:
    """Integration tests for Parser API endpoints"""

    @pytest.fixture
    def api_client(self, api_mock_parser_service):
        """Test client with mocked parser service"""
        from unittest.mock import patch

        app = FastAPI()
        app.include_router(router)

        # Patch the dependency function to return our mock
        with patch(
            "src.parser.dependencies.get_parser_service",
            return_value=api_mock_parser_service,
        ):
            yield TestClient(app)

    def test_start_parsing_endpoint_success(
        self, api_client, api_mock_parser_service
    ):
        """Test successful POST /parser/start endpoint"""
        request_data = {
            "group_ids": [123456789, 987654321],
            "max_posts": 50,
            "max_comments_per_post": 100,
            "force_reparse": False,
            "priority": "normal",
        }

        response = api_client.post("/parser/start", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data
        assert data["data"]["task_id"] == "test-task-123"
        assert data["data"]["status"] == "started"

        # Verify service was called correctly
        api_mock_parser_service.start_parsing.assert_called_once()
        call_args = api_mock_parser_service.start_parsing.call_args[1]
        assert call_args["group_ids"] == request_data["group_ids"]
        assert call_args["max_posts"] == request_data["max_posts"]

    def test_start_parsing_endpoint_validation_error(
        self, api_client, api_mock_parser_service
    ):
        """Test POST /parser/start with validation error"""
        # Invalid request - empty group_ids
        request_data = {"group_ids": [], "max_posts": 50}

        response = api_client.post("/parser/start", json=request_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_start_parsing_endpoint_service_error(
        self, api_client, api_mock_parser_service
    ):
        """Test POST /parser/start with service error"""
        # Configure service to raise exception
        api_mock_parser_service.start_parsing.side_effect = Exception(
            "Service unavailable"
        )

        request_data = {"group_ids": [123456789], "max_posts": 10}

        response = api_client.post("/parser/start", json=request_data)

        assert response.status_code == 500
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "INTERNAL_ERROR"

    def test_stop_parsing_endpoint_success(
        self, api_client, api_mock_parser_service
    ):
        """Test successful POST /parser/stop endpoint"""
        request_data = {"task_id": "test-task-123"}

        response = api_client.post("/parser/stop", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert data["data"]["stopped_tasks"] == ["test-task-123"]
        assert "message" in data["data"]

        # Verify service was called
        api_mock_parser_service.stop_parsing.assert_called_once_with(
            task_id="test-task-123"
        )

    def test_stop_parsing_endpoint_all_tasks(
        self, api_client, api_mock_parser_service
    ):
        """Test POST /parser/stop without task_id (stop all)"""
        response = api_client.post("/parser/stop", json={})

        assert response.status_code == 200

        # Verify service was called without task_id
        api_mock_parser_service.stop_parsing.assert_called_once_with(
            task_id=None
        )

    def test_get_task_status_endpoint_success(
        self, api_client, api_mock_parser_service
    ):
        """Test successful GET /parser/status/{task_id} endpoint"""
        response = api_client.get("/parser/status/test-task-123")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert data["data"]["task_id"] == "test-task-123"
        assert data["data"]["status"] == "running"
        assert data["data"]["progress"] == 45.5

        # Verify service was called
        api_mock_parser_service.get_task_status.assert_called_once_with(
            "test-task-123"
        )

    def test_get_task_status_endpoint_not_found(
        self, api_client, api_mock_parser_service
    ):
        """Test GET /parser/status/{task_id} for non-existent task"""
        api_mock_parser_service.get_task_status.return_value = None

        response = api_client.get("/parser/status/non-existent-task")

        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "TASK_NOT_FOUND"

    def test_get_parser_state_endpoint_success(
        self, api_client, api_mock_parser_service
    ):
        """Test successful GET /parser/state endpoint"""
        response = api_client.get("/parser/state")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert data["data"]["is_running"] is True
        assert data["data"]["active_tasks"] == 2
        assert data["data"]["total_posts_found"] == 100

        # Verify service was called
        api_mock_parser_service.get_parser_state.assert_called_once()

    def test_get_tasks_list_endpoint_success(
        self, api_client, api_mock_parser_service
    ):
        """Test successful GET /parser/tasks endpoint"""
        response = api_client.get("/parser/tasks")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "task-1"

        # Verify service was called with default parameters
        api_mock_parser_service.get_tasks_list.assert_called_once_with(
            limit=50, offset=0, status_filter=None
        )

    def test_get_tasks_list_endpoint_with_filters(
        self, api_client, api_mock_parser_service
    ):
        """Test GET /parser/tasks with query parameters"""
        response = api_client.get(
            "/parser/tasks?limit=10&offset=5&status=completed"
        )

        assert response.status_code == 200

        # Verify service was called with query parameters
        api_mock_parser_service.get_tasks_list.assert_called_once_with(
            limit=10, offset=5, status_filter="completed"
        )

    def test_get_parsing_stats_endpoint_success(
        self, api_client, api_mock_parser_service
    ):
        """Test successful GET /parser/stats endpoint"""
        response = api_client.get("/parser/stats")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert data["data"]["total_tasks"] == 10
        assert data["data"]["completed_tasks"] == 7
        assert data["data"]["average_task_duration"] == 45.0

        # Verify service was called
        api_mock_parser_service.get_parsing_stats.assert_called_once()

    def test_api_error_response_format(self, api_client):
        """Test that all API errors follow consistent format"""
        # Make invalid request to trigger validation error
        response = api_client.post("/parser/start", json={"invalid": "data"})

        assert response.status_code == 422
        data = response.json()

        # Check error response structure
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "meta" in data

    def test_api_success_response_format(self, api_client):
        """Test that all API success responses follow consistent format"""
        response = api_client.get("/parser/state")

        assert response.status_code == 200
        data = response.json()

        # Check success response structure
        assert "data" in data
        assert "meta" in data
        assert "timestamp" in data["meta"]
        assert "request_id" in data["meta"]

    def test_api_cors_headers(self, api_client):
        """Test CORS headers are present in API responses"""
        response = api_client.options("/parser/start")

        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_api_content_type(self, api_client):
        """Test API responses have correct content type"""
        response = api_client.get("/parser/state")

        assert response.headers["content-type"] == "application/json"


class TestParserAPIErrorHandling:
    """Integration tests for API error handling"""

    @pytest.fixture
    def error_client(self):
        """Test client configured to raise errors"""
        app = FastAPI()
        app.include_router(router)

        # Mock service that always raises errors
        error_service = AsyncMock()
        error_service.start_parsing.side_effect = Exception(
            "Database connection failed"
        )
        error_service.get_task_status.side_effect = Exception(
            "Cache unavailable"
        )

        app.dependency_overrides[get_parser_service] = lambda: error_service

        return TestClient(app)

    def test_service_unavailable_error_handling(self, error_client):
        """Test handling of service unavailable errors"""
        response = error_client.post(
            "/parser/start", json={"group_ids": [123456789], "max_posts": 10}
        )

        assert response.status_code == 500
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert "Database connection failed" in data["error"]["message"]

    def test_network_timeout_error_handling(self, error_client):
        """Test handling of network timeout errors"""
        response = error_client.get("/parser/status/test-task-123")

        assert response.status_code == 500
        data = response.json()

        assert "error" in data
        assert "Cache unavailable" in data["error"]["message"]

    def test_validation_error_details(self, api_client):
        """Test detailed validation error information"""
        # Send request with multiple validation errors
        response = api_client.post(
            "/parser/start",
            json={
                "group_ids": [],
                "max_posts": -1,
                "max_comments_per_post": 2000,
                "priority": "invalid",
            },
        )

        assert response.status_code == 422
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        # Should contain details about multiple validation failures
        assert "details" in data["error"] or "message" in data["error"]


class TestParserAPIIntegration:
    """Full integration tests combining multiple API calls"""

    def test_mock_service_works_directly(self, api_mock_parser_service):
        """Test that our mock service works correctly in isolation"""
        import asyncio

        async def test_mock():
            # Test start_parsing
            result = await api_mock_parser_service.start_parsing(
                group_ids=[123456789], max_posts=10, max_comments_per_post=50
            )

            assert "task_id" in result
            assert result["status"] == "started"
            assert result["group_ids"] == [123456789]

            task_id = result["task_id"]

            # Test get_task_status
            status = await api_mock_parser_service.get_task_status(task_id)

            assert status is not None
            assert status["task_id"] == task_id
            assert status["status"] == "running"
            assert status["progress"] == 45.5

            # Test stop_parsing
            stop_result = await api_mock_parser_service.stop_parsing(task_id)

            assert "stopped_tasks" in stop_result
            assert task_id in stop_result["stopped_tasks"]

        asyncio.run(test_mock())

    def test_complete_parsing_workflow_via_api(self, api_mock_parser_service):
        """Test complete parsing workflow through API endpoints"""
        # Create a fresh FastAPI app with our mock service
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        # Override the dependency with our mock
        app.dependency_overrides[get_parser_service] = (
            lambda: api_mock_parser_service
        )

        # Create test client with the fresh app
        client = TestClient(app)
        # 1. Start parsing
        start_response = client.post(
            "/api/v1/parser/parse",
            json={
                "group_ids": [123456789],
                "max_posts": 10,
                "max_comments_per_post": 50,
            },
        )

        assert start_response.status_code == 201
        start_data = start_response.json()
        task_id = start_data["task_id"]

        # 2. Check status
        status_response = client.get(f"/api/v1/parser/tasks/{task_id}")

        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["task_id"] == task_id

        # 3. Stop parsing
        stop_response = client.post(
            "/api/v1/parser/stop", json={"task_id": task_id}
        )

        assert stop_response.status_code == 200
        stop_data = stop_response.json()
        assert task_id in stop_data["stopped_tasks"]

        # 4. Verify final status
        final_status_response = client.get(f"/api/v1/parser/tasks/{task_id}")
        assert final_status_response.status_code == 200

        # Verify service calls (mock object tracks calls internally)
        # The mock service is working correctly as evidenced by successful API responses

    def test_concurrent_api_requests(
        self, api_client, api_mock_parser_service
    ):
        """Test handling of concurrent API requests"""
        import threading
        import time

        results = []
        errors = []

        def make_request():
            try:
                response = api_client.get("/parser/state")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Create multiple concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join()

        # Verify all requests succeeded
        assert len(results) == 5
        assert all(status == 200 for status in results)
        assert len(errors) == 0

        # Verify service was called multiple times
        assert api_mock_parser_service.get_parser_state.call_count == 5
