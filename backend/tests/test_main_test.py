import fastapi.testclient

from app.core.config import settings
from app.main import app

print("FASTAPI TESTCLIENT PATH:", fastapi.testclient.__file__)

client = fastapi.testclient.TestClient(app)


def test_health_check() -> None:
    """Тест health check endpoint"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert "status" in response.json()


def test_root_endpoint() -> None:
    """Тест корневого endpoint"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data and "version" in data


def test_api_docs() -> None:
    """Тест доступности API документации"""
    if settings.debug:
        response = client.get("/docs")
        assert response.status_code == 200
        assert "Swagger UI" in response.text
