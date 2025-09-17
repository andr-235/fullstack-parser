"""
Сервис управления токенами
"""

from typing import Dict, Any, Optional

from src.common.logging import get_logger

from ..interfaces import IJWTService, ICacheService
from ..exceptions import InvalidTokenError, TokenExpiredError


class TokenManagementService:
    """Сервис для управления токенами"""

    def __init__(
        self,
        jwt_service: IJWTService,
        cache_service: ICacheService = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.jwt_service = jwt_service
        self.cache_service = cache_service
        self.config = config or {}
        self.logger = get_logger()

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Обновляет access токен"""
        self.logger.info("Refreshing access token")

        # Валидируем refresh токен
        token_data = await self.jwt_service.validate_token(refresh_token)
        if not token_data:
            raise InvalidTokenError()

        # Создаем новый access токен
        access_token = await self.jwt_service.create_access_token(token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.config.get("access_token_expire_minutes", 30) * 60
        }

    async def validate_token_and_get_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидирует токен и возвращает данные пользователя"""
        try:
            token_data = await self.jwt_service.validate_token(token)
            if not token_data:
                return None

            user_id = token_data.get("sub")
            if not user_id:
                return None

            # Проверяем кэш
            if self.cache_service:
                cache_key = f"user:{user_id}"
                cached_data = await self.cache_service.get(cache_key)
                if cached_data and isinstance(cached_data, dict):
                    return {
                        "id": cached_data["id"],
                        "email": cached_data["email"],
                        "full_name": cached_data["full_name"],
                        "status": cached_data["is_active"] and "active" or "inactive",
                        "is_superuser": False,
                        "last_login": None,
                        "login_attempts": 0,
                        "locked_until": None,
                        "email_verified": False,
                        "created_at": None,
                        "updated_at": None
                    }

            return None

        except (InvalidTokenError, TokenExpiredError) as e:
            self.logger.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during token validation: {e}")
            return None

    async def revoke_token(self, token: str) -> None:
        """Отзывает токен"""
        try:
            await self.jwt_service.revoke_token(token)
            self.logger.info("Token revoked successfully")
        except Exception as e:
            self.logger.error(f"Error revoking token: {e}")

    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """Выход из системы"""
        try:
            if refresh_token:
                await self.revoke_token(refresh_token)
                token_data = await self.jwt_service.decode_token(refresh_token)
                if token_data:
                    self.logger.info(f"User {token_data.get('sub')} logged out")
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")

    async def create_password_reset_token(self, user_id: int, email: str) -> str:
        """Создает токен для сброса пароля"""
        token_data = {
            "sub": str(user_id),
            "email": email,
            "type": "password_reset"
        }
        return await self.jwt_service.create_access_token(token_data)

    async def validate_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидирует токен сброса пароля"""
        token_data = await self.jwt_service.validate_token(token)
        if not token_data or token_data.get("type") != "password_reset":
            raise InvalidTokenError()
        return token_data