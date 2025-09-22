"""
Сервис для работы с паролями
"""

import bcrypt
from typing import Optional

from ..interfaces import IPasswordService


class PasswordService(IPasswordService):
    """Сервис для безопасной работы с паролями"""

    # Константы для bcrypt
    SALT_ROUNDS = 12

    async def hash_password(self, password: str) -> str:
        """Хеширует пароль с использованием bcrypt

        Args:
            password: Пароль в открытом виде

        Returns:
            Хешированный пароль
        """
        # Преобразуем пароль в байты
        password_bytes = password.encode('utf-8')

        # Генерируем соль и хешируем пароль
        salt = bcrypt.gensalt(rounds=self.SALT_ROUNDS)
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        # Возвращаем хеш как строку
        return hashed_password.decode('utf-8')

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверяет пароль против хеша

        Args:
            password: Пароль в открытом виде
            hashed_password: Хешированный пароль

        Returns:
            True если пароль верный, False в противном случае
        """
        try:
            # Преобразуем в байты
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')

            # Проверяем пароль
            return bcrypt.checkpw(password_bytes, hashed_bytes)

        except (ValueError, TypeError):
            # Если хеш поврежден или неправильный формат
            return False

    def _validate_password_strength(self, password: str) -> bool:
        """Проверяет минимальную сложность пароля

        Args:
            password: Пароль для проверки

        Returns:
            True если пароль достаточно сложный
        """
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*(),.?\":{}|<>" for c in password)

        return has_upper and has_lower and has_digit and has_special