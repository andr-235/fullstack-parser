"""
Исключения доменного слоя модуля авторов

Специфичные исключения для бизнес-логики работы с авторами
"""

from typing import Optional


class AuthorNotFoundError(Exception):
    """Исключение когда автор не найден."""

    def __init__(self, vk_id: int, message: Optional[str] = None):
        self.vk_id = vk_id
        self.message = message or f"Автор с VK ID {vk_id} не найден"
        super().__init__(self.message)


class AuthorValidationError(Exception):
    """Исключение при валидации данных автора."""

    def __init__(self, field: str, value: str, message: Optional[str] = None):
        self.field = field
        self.value = value
        self.message = message or f"Некорректное значение для поля '{field}': {value}"
        super().__init__(self.message)


class AuthorAlreadyExistsError(Exception):
    """Исключение когда автор уже существует."""

    def __init__(self, vk_id: int, message: Optional[str] = None):
        self.vk_id = vk_id
        self.message = message or f"Автор с VK ID {vk_id} уже существует"
        super().__init__(self.message)


class AuthorOperationError(Exception):
    """Общее исключение для операций с авторами."""

    def __init__(self, operation: str, vk_id: int, message: Optional[str] = None):
        self.operation = operation
        self.vk_id = vk_id
        self.message = message or f"Ошибка выполнения операции '{operation}' для автора {vk_id}"
        super().__init__(self.message)
