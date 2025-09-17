"""
Сервис паролей с оптимизациями производительности
"""

import asyncio
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
    """Сервис паролей с использованием bcrypt и оптимизациями"""

    DEFAULT_ROUNDS = 12
    MAX_WORKERS = 4  # Максимальное количество воркеров для асинхронных операций

    def __init__(self, rounds: int = DEFAULT_ROUNDS):
        self.rounds = rounds
        self.logger = get_logger()

        # Создаем thread pool для CPU-bound операций
        self._executor = None
        try:
            from concurrent.futures import ThreadPoolExecutor
            self._executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        except ImportError:
            self.logger.warning("ThreadPoolExecutor not available, using synchronous operations")

    async def hash_password(self, password: str) -> str:
        """Захешировать пароль с оптимизацией

        Args:
            password: Пароль для хеширования

        Returns:
            str: Захешированный пароль

        Raises:
            Exception: При ошибке хеширования
        """
        try:
            if self._executor:
                # Выполняем CPU-bound операцию в thread pool
                loop = asyncio.get_event_loop()
                salt = await loop.run_in_executor(self._executor, bcrypt.gensalt, self.rounds)
                hashed = await loop.run_in_executor(self._executor, bcrypt.hashpw, password.encode('utf-8'), salt)
            else:
                # Fallback для синхронного выполнения
                salt = bcrypt.gensalt(rounds=self.rounds)
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

            return hashed.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error hashing password: {e}")
            raise

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль с оптимизацией

        Args:
            password: Пароль для проверки
            hashed_password: Захешированный пароль

        Returns:
            bool: True если пароль верный, False иначе
        """
        try:
            if self._executor:
                # Выполняем CPU-bound операцию в thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    bcrypt.checkpw,
                    password.encode('utf-8'),
                    hashed_password.encode('utf-8')
                )
            else:
                # Fallback для синхронного выполнения
                result = bcrypt.checkpw(
                    password.encode('utf-8'),
                    hashed_password.encode('utf-8')
                )

            return result
        except Exception as e:
            self.logger.error(f"Error verifying password: {e}")
            return False

    async def hash_multiple_passwords(self, passwords: list[str]) -> list[str]:
        """Захешировать несколько паролей параллельно

        Args:
            passwords: Список паролей для хеширования

        Returns:
            list[str]: Список захешированных паролей
        """
        if not self._executor:
            # Fallback для последовательного выполнения
            return [await self.hash_password(pwd) for pwd in passwords]

        try:
            loop = asyncio.get_event_loop()
            tasks = []

            for password in passwords:
                task = loop.run_in_executor(
                    self._executor,
                    self._hash_password_sync,
                    password
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Обрабатываем результаты и исключения
            hashed_passwords = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error hashing password {i}: {result}")
                    hashed_passwords.append("")  # Или можно поднять исключение
                else:
                    hashed_passwords.append(result)

            return hashed_passwords
        except Exception as e:
            self.logger.error(f"Error in batch password hashing: {e}")
            raise

    def _hash_password_sync(self, password: str) -> str:
        """Синхронная версия хеширования для использования в thread pool"""
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    async def close(self) -> None:
        """Закрыть ресурсы сервиса"""
        if self._executor:
            self._executor.shutdown(wait=True)
            self.logger.info("Password service executor shut down")

    def __del__(self):
        """Деструктор для очистки ресурсов"""
        if hasattr(self, '_executor') and self._executor:
            try:
                self._executor.shutdown(wait=False)
            except Exception:
                pass  # Игнорируем ошибки в деструкторе