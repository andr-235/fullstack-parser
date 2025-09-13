"""
JWT сервис
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt

from common.logging import get_logger

from ..exceptions import InvalidTokenError, TokenExpiredError


class JWTService:
    """JWT сервис"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        cache_service: Optional[Any] = None
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.cache_service = cache_service
        self.logger = get_logger()

    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Создать access токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            self.logger.error(f"Error creating access token: {e}")
            raise

    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Создать refresh токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            self.logger.error(f"Error creating refresh token: {e}")
            raise

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидировать токен"""
        try:
            # Проверяем blacklist
            if self.cache_service:
                is_blacklisted = await self.cache_service.get(f"blacklist:{token}")
                if is_blacklisted:
                    raise TokenExpiredError()

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            raise InvalidTokenError()

    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Декодировать токен без проверки подписи (для logout)"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            self.logger.error(f"Error decoding token: {e}")
            return None

    async def revoke_token(self, token: str) -> None:
        """Отозвать токен (добавить в blacklist)"""
        if self.cache_service:
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                exp = payload.get("exp")
                if exp:
                    # Добавляем в blacklist до истечения токена
                    ttl = exp - int(datetime.utcnow().timestamp())
                    if ttl > 0:
                        await self.cache_service.set(f"blacklist:{token}", "1", ttl=ttl)
            except Exception as e:
                self.logger.error(f"Error revoking token: {e}")
