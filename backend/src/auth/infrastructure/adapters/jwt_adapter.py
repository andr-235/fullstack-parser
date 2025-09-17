"""
Адаптер для JWT сервиса
"""

from typing import Dict, Any, Optional

from ..interfaces import IJWTService


class JWTServiceAdapter(IJWTService):
    """Адаптер для существующего JWT сервиса"""

    def __init__(self, jwt_service: Any):
        self.jwt_service = jwt_service

    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Создать access токен"""
        return await self.jwt_service.create_access_token(data)

    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Создать refresh токен"""
        return await self.jwt_service.create_refresh_token(data)

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидировать токен"""
        return await self.jwt_service.validate_token(token)

    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Декодировать токен без валидации"""
        return await self.jwt_service.decode_token(token)

    async def revoke_token(self, token: str) -> None:
        """Отозвать токен"""
        await self.jwt_service.revoke_token(token)