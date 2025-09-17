"""
Адаптер для сервиса паролей
"""

from typing import Any

from ..interfaces import IPasswordService


class PasswordServiceAdapter(IPasswordService):
    """Адаптер для существующего сервиса паролей"""

    def __init__(self, password_service: Any):
        self.password_service = password_service

    async def hash_password(self, password: str) -> str:
        """Хешировать пароль"""
        return await self.password_service.hash_password(password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return await self.password_service.verify_password(password, hashed_password)