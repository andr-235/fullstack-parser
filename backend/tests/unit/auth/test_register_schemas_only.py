"""
Тесты только для схем регистрации
"""

import pytest
from pydantic import ValidationError

from src.auth.schemas import RegisterRequest, RegisterResponse


class TestRegisterSchemasOnly:
    """Тесты для схем регистрации без зависимостей"""

    def test_register_request_validation(self):
        """Тест валидации RegisterRequest"""
        # Валидные данные
        valid_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
        request = RegisterRequest(**valid_data)
        
        assert request.email == "test@example.com"
        assert request.password == "password123"
        assert request.full_name == "Test User"

    def test_register_request_invalid_email(self):
        """Тест невалидного email"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="invalid-email",
                password="password123",
                full_name="Test User"
            )

    def test_register_request_short_password(self):
        """Тест короткого пароля"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="123",
                full_name="Test User"
            )

    def test_register_request_short_name(self):
        """Тест короткого имени"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="password123",
                full_name="A"
            )

    def test_register_request_long_name(self):
        """Тест длинного имени"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="password123",
                full_name="A" * 101  # Слишком длинное имя
            )

    def test_register_response_creation(self):
        """Тест создания RegisterResponse"""
        response = RegisterResponse(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            token_type="bearer",
            expires_in=3600,
            user={
                "id": 1,
                "email": "test@example.com",
                "full_name": "Test User",
                "is_superuser": False
            }
        )
        
        assert response.access_token == "access_token_123"
        assert response.refresh_token == "refresh_token_123"
        assert response.token_type == "bearer"
        assert response.expires_in == 3600
        assert response.user["id"] == 1
        assert response.user["email"] == "test@example.com"
        assert response.user["full_name"] == "Test User"
        assert response.user["is_superuser"] is False

    def test_register_request_required_fields(self):
        """Тест обязательных полей"""
        # Отсутствует email
        with pytest.raises(ValidationError):
            RegisterRequest(
                password="password123",
                full_name="Test User"
            )
        
        # Отсутствует password
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                full_name="Test User"
            )
        
        # Отсутствует full_name
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="password123"
            )
