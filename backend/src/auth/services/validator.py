"""
Валидатор для модуля аутентификации
"""

import re
from typing import Optional

from src.common.logging import get_logger

from ..config import AuthConfig
from ..exceptions import InvalidCredentialsError


class AuthValidator:
    """Валидатор для аутентификации с улучшенной безопасностью"""

    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
        self.logger = get_logger()

        # Регулярные выражения для валидации
        self._email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self._password_pattern = re.compile(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
        )
        self._name_pattern = re.compile(r'^[a-zA-Zа-яА-Я\s\-]+$')

    async def validate_email(self, email: str) -> bool:
        """Валидировать email с дополнительными проверками"""
        if not email or not isinstance(email, str):
            return False

        email = email.strip().lower()

        # Проверка длины
        if len(email) > self.config.email_max_length:
            self.logger.warning(f"Email too long: {len(email)} characters")
            return False

        # Проверка формата
        if not self._email_pattern.match(email):
            self.logger.warning(f"Invalid email format: {email}")
            return False

        # Проверка на распространенные атаки
        if self._contains_suspicious_patterns(email):
            self.logger.warning(f"Suspicious email pattern detected: {email}")
            return False

        return True

    async def validate_password(self, password: str) -> bool:
        """Валидировать пароль с комплексными правилами"""
        if not password or not isinstance(password, str):
            return False

        # Проверка минимальной длины
        if len(password) < self.config.password_min_length:
            self.logger.warning(f"Password too short: {len(password)} characters")
            return False

        # Проверка максимальной длины (защита от DoS)
        if len(password) > 128:
            self.logger.warning(f"Password too long: {len(password)} characters")
            return False

        # Проверка сложности
        if not self._is_password_complex(password):
            self.logger.warning("Password does not meet complexity requirements")
            return False

        # Проверка на распространенные пароли
        if self._is_common_password(password):
            self.logger.warning("Password is too common")
            return False

        return True

    async def validate_full_name(self, full_name: str) -> bool:
        """Валидировать полное имя"""
        if not full_name or not isinstance(full_name, str):
            return False

        full_name = full_name.strip()

        # Проверка длины
        if len(full_name) < 2 or len(full_name) > self.config.full_name_max_length:
            self.logger.warning(f"Full name length invalid: {len(full_name)} characters")
            return False

        # Проверка формата
        if not self._name_pattern.match(full_name):
            self.logger.warning(f"Invalid full name format: {full_name}")
            return False

        return True

    async def validate_registration_data(self, email: str, password: str, full_name: str) -> None:
        """Комплексная валидация данных регистрации"""
        errors = []

        if not await self.validate_email(email):
            errors.append("Invalid email format or suspicious pattern")

        if not await self.validate_password(password):
            errors.append("Password does not meet security requirements")

        if not await self.validate_full_name(full_name):
            errors.append("Invalid full name format")

        if errors:
            error_message = "; ".join(errors)
            self.logger.warning(f"Registration validation failed: {error_message}")
            raise InvalidCredentialsError(error_message)

    async def validate_login_data(self, email: str, password: str) -> None:
        """Валидация данных входа"""
        if not await self.validate_email(email):
            self.logger.warning(f"Invalid email for login: {email}")
            raise InvalidCredentialsError("Invalid email format")

        # Для пароля при логине проверяем только базовые правила
        if not password or len(password) > 128:
            self.logger.warning("Invalid password for login")
            raise InvalidCredentialsError("Invalid password")

    def _contains_suspicious_patterns(self, email: str) -> bool:
        """Проверка на подозрительные паттерны в email"""
        suspicious_patterns = [
            r'<script',  # XSS попытки
            r'javascript:',  # JavaScript injection
            r'data:',  # Data URI
            r'vbscript:',  # VBScript
            r'on\w+\s*=',  # Event handlers
            r'\\x[0-9a-fA-F]{2}',  # Hex encoding
            r'%[0-9a-fA-F]{2}',  # URL encoding
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return True

        return False

    def _is_password_complex(self, password: str) -> bool:
        """Проверка сложности пароля"""
        # Минимум 8 символов, буквы верхнего и нижнего регистра, цифры, спецсимволы
        if len(password) < 8:
            return False

        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[@$!%*?&]', password))

        return has_lower and has_upper and has_digit and has_special

    def _is_common_password(self, password: str) -> bool:
        """Проверка на распространенные пароли"""
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', 'qwerty123', 'welcome123'
        }

        return password.lower() in common_passwords

    async def sanitize_input(self, input_str: str) -> str:
        """Санитизация входных данных"""
        if not input_str:
            return ""

        # Удаление лишних пробелов
        sanitized = input_str.strip()

        # Удаление потенциально опасных символов
        sanitized = re.sub(r'[<>]', '', sanitized)

        # Ограничение длины
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]

        return sanitized

    async def rate_limit_check(self, identifier: str, max_attempts: int, window_seconds: int) -> bool:
        """Проверка rate limiting (заглушка для интеграции с кешем)"""
        # Эта функция должна интегрироваться с кеш-сервисом
        # Пока возвращаем True (разрешено)
        return True