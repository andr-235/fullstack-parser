"""
JWT сервис с оптимизациями производительности
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt

from common.logging import get_logger

from ..exceptions import InvalidTokenError, TokenExpiredError


class JWTService:
    """JWT сервис с оптимизациями производительности"""

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

        # Кеш для часто используемых токенов
        self._token_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_max_size = 1000
        self._cache_ttl_seconds = 300  # 5 минут

    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Создать access токен с оптимизацией"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access", "iat": datetime.utcnow()})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

            # Кешируем токен для быстрой валидации
            if self.cache_service and len(self._token_cache) < self._cache_max_size:
                cache_key = f"token:{encoded_jwt[:16]}"  # Используем первые 16 символов как ключ
                await self.cache_service.set(
                    cache_key,
                    {"payload": to_encode, "created_at": datetime.utcnow().timestamp()},
                    ttl=self._cache_ttl_seconds
                )

            return encoded_jwt
        except Exception as e:
            self.logger.error(f"Error creating access token: {e}")
            raise

    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Создать refresh токен с оптимизацией"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh", "iat": datetime.utcnow()})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

            # Кешируем refresh токен
            if self.cache_service:
                cache_key = f"refresh:{encoded_jwt[:16]}"
                await self.cache_service.set(
                    cache_key,
                    {"payload": to_encode, "created_at": datetime.utcnow().timestamp()},
                    ttl=self.refresh_token_expire_days * 24 * 3600  # В секундах
                )

            return encoded_jwt
        except Exception as e:
            self.logger.error(f"Error creating refresh token: {e}")
            raise

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидировать токен с оптимизацией через кеш"""
        try:
            # Сначала проверяем локальный кеш
            cache_key = f"token:{token[:16]}"
            if self.cache_service:
                cached_data = await self.cache_service.get(cache_key)
                if cached_data and isinstance(cached_data, dict):
                    payload = cached_data.get("payload")
                    if payload and payload.get("exp", 0) > datetime.utcnow().timestamp():
                        return payload

            # Проверяем blacklist в кеше
            blacklist_key = f"blacklist:{token}"
            if self.cache_service:
                is_blacklisted = await self.cache_service.get(blacklist_key)
                if is_blacklisted:
                    raise TokenExpiredError()

            # Декодируем токен
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Обновляем кеш
            if self.cache_service and len(self._token_cache) < self._cache_max_size:
                await self.cache_service.set(
                    cache_key,
                    {"payload": payload, "created_at": datetime.utcnow().timestamp()},
                    ttl=self._cache_ttl_seconds
                )

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
        """Отозвать токен с оптимизацией"""
        if self.cache_service:
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                exp = payload.get("exp")
                if exp:
                    # Добавляем в blacklist
                    ttl = exp - int(datetime.utcnow().timestamp())
                    if ttl > 0:
                        await self.cache_service.set(f"blacklist:{token}", "1", ttl=ttl)

                        # Удаляем из кеша валидных токенов
                        cache_key = f"token:{token[:16]}"
                        await self.cache_service.delete(cache_key)

                        # Удаляем из кеша refresh токенов
                        if payload.get("type") == "refresh":
                            refresh_cache_key = f"refresh:{token[:16]}"
                            await self.cache_service.delete(refresh_cache_key)
            except Exception as e:
                self.logger.error(f"Error revoking token: {e}")

    async def is_token_blacklisted(self, token: str) -> bool:
        """Проверить, находится ли токен в blacklist"""
        if self.cache_service:
            blacklist_key = f"blacklist:{token}"
            is_blacklisted = await self.cache_service.get(blacklist_key)
            return bool(is_blacklisted)
        return False

    async def cleanup_expired_tokens(self) -> None:
        """Очистить истекшие токены из кеша (для фоновой задачи)"""
        if self.cache_service:
            try:
                # Здесь можно реализовать очистку истекших токенов
                # Для Redis можно использовать SCAN для поиска ключей
                pass
            except Exception as e:
                self.logger.error(f"Error cleaning up expired tokens: {e}")