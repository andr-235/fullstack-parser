"""
Адаптер для JWT сервиса
"""

from typing import Any, Dict, Optional

from ..interfaces import IJWTService


class JWTServiceAdapter(IJWTService):
    """Адаптер для JWT сервиса"""

    def __init__(self, jwt_service):
        self.service = jwt_service

    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Создать access токен"""
        return await self.service.create_access_token(data)

    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Создать refresh токен"""
        return await self.service.create_refresh_token(data)

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидировать токен"""
        return await self.service.validate_token(token)

    async def revoke_token(self, token: str) -> None:
        """Отозвать токен"""
        await self.service.revoke_token(token)