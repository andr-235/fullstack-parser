"""
Unit tests for Settings router endpoints

Tests cover all router endpoints including:
- GET /settings - get current settings
- PUT /settings - update settings
- POST /settings/reset - reset to defaults
- GET /settings/section/{section_name} - get section
- PUT /settings/section/{section_name} - update section
- GET /settings/value/{section_name}/{key} - get setting value
- PUT /settings/value/{section_name}/{key} - set setting value
- GET /settings/health - health check
- POST /settings/validate - validate settings
"""

import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import Request
from fastapi.testclient import TestClient

from src.settings.router import router
from src.handlers import create_success_response, create_error_response


class TestSettingsRouter:
    """Test suite for Settings router"""

    @pytest.fixture
    def client(self, mock_settings_service):
        """Create test client with mocked service"""
        from fastapi import FastAPI
        from src.settings.router import get_settings_service

        app = FastAPI()
        app.include_router(router)

        # Mock the dependency function directly
        app.dependency_overrides[get_settings_service] = (
            lambda: mock_settings_service
        )

        return TestClient(app)

    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/settings"
        request.headers = {}
        request.query_params = {}
        return request

    @pytest.fixture
    def sample_settings(self, sample_settings_data):
        """Sample settings data"""
        return sample_settings_data

    @pytest.fixture
    def sample_updates(self, sample_section_data):
        """Sample settings updates"""
        return sample_section_data

    def test_get_settings_success(
        self, client, mock_settings_service, sample_settings
    ):
        """Test successful GET /settings"""
        # Arrange
        mock_settings_service.get_current_settings = AsyncMock(
            return_value=sample_settings
        )

        # Act
        response = client.get("/settings")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == sample_settings

    def test_get_settings_failure(self, client, mock_settings_service):
        """Test GET /settings failure"""
        # Arrange
        mock_settings_service.get_current_settings = AsyncMock(
            side_effect=Exception("Service error")
        )

        # Act
        response = client.get("/settings")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "meta" in data
        assert data["error"]["code"] == "SETTINGS_LOAD_FAILED"

    def test_update_settings_success(
        self, client, mock_settings_service, sample_settings, sample_updates
    ):
        """Test successful PUT /settings"""
        # Arrange
        mock_settings_service.update_settings = AsyncMock(
            return_value=sample_settings
        )

        # Act
        response = client.put("/settings", json=sample_updates)

        # Debug: print response body if error
        if response.status_code != 200:
            print(f"Response body: {response.json()}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert "message" in data["meta"]
        assert "Настройки успешно обновлены" in data["meta"]["message"]

    def test_update_settings_failure(
        self, client, mock_settings_service, sample_updates
    ):
        """Test PUT /settings failure"""
        # Arrange
        mock_settings_service.update_settings = AsyncMock(
            side_effect=Exception("Update failed")
        )

        # Act
        response = client.put("/settings", json=sample_updates)

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "SETTINGS_UPDATE_FAILED" in data["error"]["code"]

    def test_reset_settings_success(
        self, client, mock_settings_service, sample_settings
    ):
        """Test successful POST /settings/reset"""
        # Arrange
        mock_settings_service.reset_to_defaults = AsyncMock(
            return_value=sample_settings
        )

        # Act
        response = client.post("/settings/reset")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "message" in data
        assert (
            "Настройки сброшены к значениям по умолчанию"
            in data["meta"]["message"]
        )

    def test_reset_settings_failure(self, client, mock_settings_service):
        """Test POST /settings/reset failure"""
        # Arrange
        mock_settings_service.reset_to_defaults = AsyncMock(
            side_effect=Exception("Reset failed")
        )

        # Act
        response = client.post("/settings/reset")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "SETTINGS_RESET_FAILED" in data["error"]["code"]

    def test_get_settings_section_success(
        self, client, mock_settings_service, sample_settings
    ):
        """Test successful GET /settings/section/{section_name}"""
        # Arrange
        section_name = "vk_api"
        section_data = sample_settings[section_name]
        mock_settings_service.get_section = AsyncMock(
            return_value={
                "name": section_name,
                "values": section_data,
                "description": f"Settings for {section_name}",
            }
        )

        # Act
        response = client.get(f"/settings/section/{section_name}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["name"] == section_name
        assert data["data"]["values"] == section_data

    def test_get_settings_section_not_found(
        self, client, mock_settings_service
    ):
        """Test GET /settings/section/{section_name} when section not found"""
        # Arrange
        section_name = "nonexistent"
        mock_settings_service.get_section = AsyncMock(return_value=None)

        # Act
        response = client.get(f"/settings/section/{section_name}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "SECTION_NOT_FOUND"

    def test_get_settings_section_failure(self, client, mock_settings_service):
        """Test GET /settings/section/{section_name} failure"""
        # Arrange
        section_name = "vk_api"
        mock_settings_service.get_section = AsyncMock(
            side_effect=Exception("Section error")
        )

        # Act
        response = client.get(f"/settings/section/{section_name}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "SECTION_LOAD_FAILED"

    def test_update_settings_section_success(
        self, client, mock_settings_service, sample_settings
    ):
        """Test successful PUT /settings/section/{section_name}"""
        # Arrange
        section_name = "vk_api"
        section_data = {"api_version": "5.200", "requests_per_second": 5}
        mock_settings_service.update_section = AsyncMock(
            return_value=sample_settings
        )

        # Act
        response = client.put(
            f"/settings/section/{section_name}", json=section_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "message" in data
        assert (
            f"Секция '{section_name}' успешно обновлена"
            in data["meta"]["message"]
        )

    def test_update_settings_section_failure(
        self, client, mock_settings_service
    ):
        """Test PUT /settings/section/{section_name} failure"""
        # Arrange
        section_name = "vk_api"
        section_data = {"key": "value"}
        mock_settings_service.update_section = AsyncMock(
            side_effect=Exception("Section update failed")
        )

        # Act
        response = client.put(
            f"/settings/section/{section_name}", json=section_data
        )

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "SECTION_UPDATE_FAILED" in data["error"]["code"]

    def test_get_setting_value_success(self, client, mock_settings_service):
        """Test successful GET /settings/value/{section_name}/{key}"""
        # Arrange
        section_name = "vk_api"
        key = "api_version"
        value = "5.199"
        mock_settings_service.get_setting_value = AsyncMock(return_value=value)

        # Act
        response = client.get(f"/settings/value/{section_name}/{key}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["section"] == section_name
        assert data["data"]["key"] == key
        assert data["data"]["value"] == value

    def test_get_setting_value_not_found(self, client, mock_settings_service):
        """Test GET /settings/value/{section_name}/{key} when value not found"""
        # Arrange
        section_name = "vk_api"
        key = "nonexistent_key"
        mock_settings_service.get_setting_value = AsyncMock(return_value=None)

        # Act
        response = client.get(f"/settings/value/{section_name}/{key}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "SETTING_NOT_FOUND" in data["error"]["code"]

    def test_get_setting_value_failure(self, client, mock_settings_service):
        """Test GET /settings/value/{section_name}/{key} failure"""
        # Arrange
        section_name = "vk_api"
        key = "api_version"
        mock_settings_service.get_setting_value = AsyncMock(
            side_effect=Exception("Value error")
        )

        # Act
        response = client.get(f"/settings/value/{section_name}/{key}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "SETTING_LOAD_FAILED" in data["error"]["code"]

    def test_set_setting_value_success(
        self, client, mock_settings_service, sample_settings
    ):
        """Test successful PUT /settings/value/{section_name}/{key}"""
        # Arrange
        section_name = "vk_api"
        key = "api_version"
        value = "5.200"
        mock_settings_service.set_setting_value = AsyncMock(
            return_value=sample_settings
        )

        # Act
        response = client.put(
            f"/settings/value/{section_name}/{key}?value={value}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "message" in data
        assert (
            f"Настройка '{section_name}.{key}' успешно установлена"
            in data["meta"]["message"]
        )

    def test_set_setting_value_failure(self, client, mock_settings_service):
        """Test PUT /settings/value/{section_name}/{key} failure"""
        # Arrange
        section_name = "vk_api"
        key = "api_version"
        value = "5.200"
        mock_settings_service.set_setting_value = AsyncMock(
            side_effect=Exception("Value update failed")
        )

        # Act
        response = client.put(
            f"/settings/value/{section_name}/{key}?value={value}"
        )

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "SETTING_UPDATE_FAILED" in data["error"]["code"]

    def test_get_settings_health_success(
        self, client, mock_settings_service, health_check_response
    ):
        """Test successful GET /settings/health"""
        # Arrange
        mock_settings_service.get_health_status = AsyncMock(
            return_value=health_check_response
        )

        # Act
        response = client.get("/settings/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "healthy"

    def test_get_settings_health_failure(self, client, mock_settings_service):
        """Test GET /settings/health failure"""
        # Arrange
        mock_settings_service.get_health_status = AsyncMock(
            side_effect=Exception("Health check failed")
        )

        # Act
        response = client.get("/settings/health")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "HEALTH_CHECK_FAILED" in data["error"]["code"]

    def test_validate_settings_success(
        self, client, mock_settings_service, validation_result
    ):
        """Test successful POST /settings/validate"""
        # Arrange
        mock_settings_service.validate_settings = AsyncMock(
            return_value=validation_result
        )

        # Act
        response = client.post("/settings/validate")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["valid"] is True

    def test_validate_settings_failure(self, client, mock_settings_service):
        """Test POST /settings/validate failure"""
        # Arrange
        mock_settings_service.validate_settings = AsyncMock(
            side_effect=Exception("Validation failed")
        )

        # Act
        response = client.post("/settings/validate")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "VALIDATION_FAILED" in data["error"]["code"]

    def test_validate_settings_with_data(
        self, client, mock_settings_service, sample_settings, validation_result
    ):
        """Test POST /settings/validate with request data"""
        # Arrange
        mock_settings_service.validate_settings = AsyncMock(
            return_value=validation_result
        )

        # Act
        response = client.post("/settings/validate", json=sample_settings)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        mock_settings_service.validate_settings.assert_called_once()

    # Test dependency injection
    def test_get_settings_service_dependency(self):
        """Test that get_settings_service dependency works"""
        from src.settings.router import get_settings_service

        # Act
        service = get_settings_service()

        # Assert
        assert service is not None
        # This will create a real service instance

    # Test router configuration
    def test_router_configuration(self):
        """Test router configuration"""
        assert router.prefix == "/settings"
        assert "Settings" in router.tags
        assert len(router.routes) > 0  # Should have routes

    # Test individual route configurations
    def test_get_settings_route_config(self):
        """Test GET /settings route configuration"""
        route = None
        for r in router.routes:
            if (
                hasattr(r, "methods")
                and "GET" in r.methods
                and r.path == "/settings"
            ):
                route = r
                break

        assert route is not None
        assert route.summary == "Get Current Settings"
        assert "current settings" in route.description.lower()

    def test_put_settings_route_config(self):
        """Test PUT /settings route configuration"""
        route = None
        for r in router.routes:
            if (
                hasattr(r, "methods")
                and "PUT" in r.methods
                and r.path == "/settings"
            ):
                route = r
                break

        assert route is not None
        assert route.summary == "Update Settings"
        assert "update" in route.description.lower()

    def test_reset_route_config(self):
        """Test POST /settings/reset route configuration"""
        route = None
        for r in router.routes:
            if (
                hasattr(r, "methods")
                and "POST" in r.methods
                and r.path == "/reset"
            ):
                route = r
                break

        assert route is not None
        assert route.summary == "Reset Settings to Defaults"
        assert "default" in route.description.lower()

    def test_section_routes_config(self):
        """Test section-related routes configuration"""
        section_routes = [r for r in router.routes if "section" in str(r.path)]

        assert len(section_routes) >= 2  # Should have GET and PUT for sections

        get_section = next(
            (
                r
                for r in section_routes
                if hasattr(r, "methods") and "GET" in r.methods
            ),
            None,
        )
        put_section = next(
            (
                r
                for r in section_routes
                if hasattr(r, "methods") and "PUT" in r.methods
            ),
            None,
        )

        assert get_section is not None
        assert put_section is not None
        assert "section" in get_section.summary.lower()
        assert "section" in put_section.summary.lower()

    def test_value_routes_config(self):
        """Test value-related routes configuration"""
        value_routes = [r for r in router.routes if "value" in str(r.path)]

        assert len(value_routes) >= 2  # Should have GET and PUT for values

        get_value = next(
            (
                r
                for r in value_routes
                if hasattr(r, "methods") and "GET" in r.methods
            ),
            None,
        )
        put_value = next(
            (
                r
                for r in value_routes
                if hasattr(r, "methods") and "PUT" in r.methods
            ),
            None,
        )

        assert get_value is not None
        assert put_value is not None
        assert "value" in get_value.summary.lower()
        assert "value" in put_value.summary.lower()

    def test_health_route_config(self):
        """Test health route configuration"""
        health_route = next(
            (r for r in router.routes if "health" in str(r.path)), None
        )

        assert health_route is not None
        assert (
            hasattr(health_route, "methods") and "GET" in health_route.methods
        )
        assert "health" in health_route.summary.lower()

    def test_validate_route_config(self):
        """Test validate route configuration"""
        validate_route = next(
            (r for r in router.routes if "validate" in str(r.path)), None
        )

        assert validate_route is not None
        assert (
            hasattr(validate_route, "methods")
            and "POST" in validate_route.methods
        )
        assert "validate" in validate_route.summary.lower()
