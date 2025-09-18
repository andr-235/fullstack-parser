"""
Сервис валидации пользователей
"""

import re
from typing import Optional

from ...exceptions import ValidationError
from ...schemas import UserCreateRequest, UserUpdateRequest
from ..interfaces import IUserValidator


class UserValidator(IUserValidator):
    """Валидатор данных пользователей"""

    # Константы валидации
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    EMAIL_PATTERN = re.compile(r'^[^@]+@[^@]+\.[^@]+$')

    async def validate_create_data(self, data: UserCreateRequest) -> None:
        """Валидирует данные для создания пользователя

        Args:
            data: Данные для создания пользователя

        Raises:
            ValidationError: Если данные невалидны
        """
        errors = []

        # Валидация имени
        if not data.full_name or not data.full_name.strip():
            errors.append("Имя пользователя обязательно")
        elif len(data.full_name.strip()) < self.MIN_NAME_LENGTH:
            errors.append(f"Имя должно содержать минимум {self.MIN_NAME_LENGTH} символа")
        elif len(data.full_name.strip()) > self.MAX_NAME_LENGTH:
            errors.append(f"Имя не должно превышать {self.MAX_NAME_LENGTH} символов")

        # Валидация email
        if not data.email or not data.email.strip():
            errors.append("Email обязателен")
        elif not self.EMAIL_PATTERN.match(data.email.strip()):
            errors.append("Некорректный формат email")
        elif len(data.email.strip()) > 255:
            errors.append("Email не должен превышать 255 символов")

        # Валидация пароля
        if not data.password:
            errors.append("Пароль обязателен")
        elif len(data.password) < self.MIN_PASSWORD_LENGTH:
            errors.append(f"Пароль должен содержать минимум {self.MIN_PASSWORD_LENGTH} символов")
        elif len(data.password) > self.MAX_PASSWORD_LENGTH:
            errors.append(f"Пароль не должен превышать {self.MAX_PASSWORD_LENGTH} символов")

        # Проверка сложности пароля
        password_errors = self._validate_password_complexity(data.password)
        errors.extend(password_errors)

        if errors:
            raise ValidationError("; ".join(errors))

    async def validate_update_data(self, data: UserUpdateRequest) -> None:
        """Валидирует данные для обновления пользователя

        Args:
            data: Данные для обновления пользователя

        Raises:
            ValidationError: Если данные невалидны
        """
        errors = []

        # Валидация имени (если указано)
        if data.full_name is not None:
            if not data.full_name.strip():
                errors.append("Имя пользователя не может быть пустым")
            elif len(data.full_name.strip()) < self.MIN_NAME_LENGTH:
                errors.append(f"Имя должно содержать минимум {self.MIN_NAME_LENGTH} символа")
            elif len(data.full_name.strip()) > self.MAX_NAME_LENGTH:
                errors.append(f"Имя не должно превышать {self.MAX_NAME_LENGTH} символов")

        # Валидация email (если указан)
        if data.email is not None:
            if not data.email.strip():
                errors.append("Email не может быть пустым")
            elif not self.EMAIL_PATTERN.match(data.email.strip()):
                errors.append("Некорректный формат email")
            elif len(data.email.strip()) > 255:
                errors.append("Email не должен превышать 255 символов")

        if errors:
            raise ValidationError("; ".join(errors))

    def _validate_password_complexity(self, password: str) -> list[str]:
        """Проверяет сложность пароля

        Args:
            password: Пароль для проверки

        Returns:
            Список ошибок валидации
        """
        errors = []

        if not re.search(r'[A-Z]', password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву")

        if not re.search(r'[a-z]', password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву")

        if not re.search(r'\d', password):
            errors.append("Пароль должен содержать хотя бы одну цифру")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Пароль должен содержать хотя бы один специальный символ")

        return errors