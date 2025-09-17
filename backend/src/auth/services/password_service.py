"""
Сервис паролей
"""

from abc import ABC, abstractmethod
from typing import Protocol

import bcrypt

from src.common.logging import get_logger


class PasswordServiceProtocol(Protocol):
    """Протокол для сервиса паролей"""

    async def hash_password(self, password: str) -> str:
        """Захешировать пароль"""
        ...

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        ...


class PasswordService(PasswordServiceProtocol):
    """Сервис паролей с использованием bcrypt"""

    DEFAULT_ROUNDS = 12

    def __init__(self, rounds: int = DEFAULT_ROUNDS):
        self.rounds = rounds
        self.logger = get_logger()

    async def hash_password(self, password: str) -> str:
        """Захешировать пароль

        Args:
            password: Пароль для хеширования

        Returns:
            str: Захешированный пароль

        Raises:
            Exception: При ошибке хеширования
        """
        try:
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error hashing password: {e}")
            raise

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль

        Args:
            password: Пароль для проверки
            hashed_password: Захешированный пароль

        Returns:
            bool: True если пароль верный, False иначе
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f"Error verifying password: {e}")
            return False
