"""
Unit тесты для доменного слоя авторов

Тестирование сущностей, исключений и бизнес-логики
"""

import pytest
from datetime import datetime
from authors.domain.entities import AuthorEntity
from authors.domain.exceptions import AuthorNotFoundError, AuthorValidationError


class TestAuthorEntity:
    """Тесты для сущности AuthorEntity."""

    def test_author_entity_creation(self):
        """Тест создания сущности автора."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            screen_name="ivan_ivanov",
            photo_url="https://example.com/photo.jpg",
            created_at=datetime.now(),
            comments_count=15
        )
        
        assert author.id == 1
        assert author.vk_id == 123456789
        assert author.first_name == "Иван"
        assert author.last_name == "Иванов"
        assert author.screen_name == "ivan_ivanov"
        assert author.photo_url == "https://example.com/photo.jpg"
        assert author.comments_count == 15

    def test_author_entity_validation_vk_id_positive(self):
        """Тест валидации положительного VK ID."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            created_at=datetime.now()
        )
        assert author.vk_id == 123456789

    def test_author_entity_validation_vk_id_negative(self):
        """Тест валидации отрицательного VK ID."""
        with pytest.raises(ValueError, match="VK ID должен быть положительным числом"):
            AuthorEntity(
                id=1,
                vk_id=-1,
                created_at=datetime.now()
            )

    def test_author_entity_validation_photo_url_valid(self):
        """Тест валидации корректного URL фото."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            photo_url="https://example.com/photo.jpg",
            created_at=datetime.now()
        )
        assert author.photo_url == "https://example.com/photo.jpg"

    def test_author_entity_validation_photo_url_invalid(self):
        """Тест валидации некорректного URL фото."""
        with pytest.raises(ValueError, match="URL фото должен начинаться с http:// или https://"):
            AuthorEntity(
                id=1,
                vk_id=123456789,
                photo_url="invalid_url",
                created_at=datetime.now()
            )

    def test_author_entity_full_name(self):
        """Тест получения полного имени."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            created_at=datetime.now()
        )
        assert author.full_name == "Иван Иванов"

    def test_author_entity_full_name_partial(self):
        """Тест получения полного имени с частичными данными."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            created_at=datetime.now()
        )
        assert author.full_name == "Иван"

    def test_author_entity_full_name_empty(self):
        """Тест получения полного имени без данных."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            created_at=datetime.now()
        )
        assert author.full_name == "123456789"

    def test_author_entity_display_name_with_screen_name(self):
        """Тест отображаемого имени с screen_name."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            screen_name="ivan_ivanov",
            created_at=datetime.now()
        )
        assert author.display_name == "ivan_ivanov"

    def test_author_entity_display_name_without_screen_name(self):
        """Тест отображаемого имени без screen_name."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            created_at=datetime.now()
        )
        assert author.display_name == "Иван Иванов"

    def test_author_entity_is_updated(self):
        """Тест проверки обновления автора."""
        now = datetime.now()
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            created_at=now,
            updated_at=now
        )
        assert author.is_updated() is True

    def test_author_entity_is_not_updated(self):
        """Тест проверки отсутствия обновления автора."""
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            created_at=datetime.now()
        )
        assert author.is_updated() is False

    def test_author_entity_to_dict(self):
        """Тест преобразования в словарь."""
        now = datetime.now()
        author = AuthorEntity(
            id=1,
            vk_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            screen_name="ivan_ivanov",
            photo_url="https://example.com/photo.jpg",
            created_at=now,
            updated_at=now,
            comments_count=25
        )
        
        result = author.to_dict()
        
        assert result["id"] == 1
        assert result["vk_id"] == 123456789
        assert result["first_name"] == "Иван"
        assert result["last_name"] == "Иванов"
        assert result["screen_name"] == "ivan_ivanov"
        assert result["photo_url"] == "https://example.com/photo.jpg"
        assert result["created_at"] == now.isoformat()
        assert result["updated_at"] == now.isoformat()
        assert result["comments_count"] == 25


class TestAuthorExceptions:
    """Тесты для исключений авторов."""

    def test_author_not_found_error(self):
        """Тест исключения AuthorNotFoundError."""
        error = AuthorNotFoundError(123456789)
        assert error.vk_id == 123456789
        assert str(error) == "Автор с VK ID 123456789 не найден"

    def test_author_not_found_error_custom_message(self):
        """Тест исключения AuthorNotFoundError с кастомным сообщением."""
        error = AuthorNotFoundError(123456789, "Custom message")
        assert error.vk_id == 123456789
        assert str(error) == "Custom message"

    def test_author_validation_error(self):
        """Тест исключения AuthorValidationError."""
        error = AuthorValidationError("email", "invalid@")
        assert error.field == "email"
        assert error.value == "invalid@"
        assert str(error) == "Некорректное значение для поля 'email': invalid@"

    def test_author_validation_error_custom_message(self):
        """Тест исключения AuthorValidationError с кастомным сообщением."""
        error = AuthorValidationError("email", "invalid@", "Custom validation error")
        assert error.field == "email"
        assert error.value == "invalid@"
        assert str(error) == "Custom validation error"
