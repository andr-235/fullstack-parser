import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_root_endpoint():
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "detail" in data


def test_api_docs():
    """Тест доступности API документации"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"] 