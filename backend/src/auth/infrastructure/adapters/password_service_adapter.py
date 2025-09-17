"""
Адаптер для сервиса паролей
"""

from ..interfaces import IPasswordService


class PasswordServiceAdapter(IPasswordService):
    """Адаптер для сервиса паролей"""

    def __init__(self, password_service):
        self.service = password_service

    async def hash_password(self, password: str) -> str:
        """Захешировать пароль"""
        return await self.service.hash_password(password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return await self.service.verify_password(password, hashed_password)