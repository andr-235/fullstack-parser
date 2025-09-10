"""
Инфраструктурный сервис безопасности

Предоставляет функциональность для JWT токенов, хеширования паролей и безопасности
"""

import secrets
import hashlib
import re
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from functools import lru_cache

from jose import jwt
from passlib.context import CryptContext

from .config import infrastructure_config
from .logging import get_loguru_logger


class SecurityService:
    """
    Инфраструктурный сервис для обеспечения безопасности

    Предоставляет функциональность для:
    - Хеширования паролей
    - Создания и проверки JWT токенов
    - Генерации секретных ключей
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = infrastructure_config.SECRET_KEY
        self.algorithm = infrastructure_config.JWT_ALGORITHM
        self.access_token_expire_minutes = (
            infrastructure_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.refresh_token_expire_days = (
            infrastructure_config.REFRESH_TOKEN_EXPIRE_DAYS
        )
        self.logger = get_loguru_logger("security")

        # Метрики
        self._password_hash_count = 0
        self._jwt_tokens_created = 0
        self._jwt_tokens_verified = 0

    def hash_password(self, password: str) -> str:
        """
        Захешировать пароль

        Args:
            password: Пароль в открытом виде

        Returns:
            Захешированный пароль
        """
        try:
            hashed = self.pwd_context.hash(password)
            self._password_hash_count += 1
            self.logger.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            self.logger.error(f"Password hashing failed: {e}")
            raise

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Проверить пароль

        Args:
            plain_password: Пароль в открытом виде
            hashed_password: Захешированный пароль

        Returns:
            True если пароль верный
        """
        try:
            result = self.pwd_context.verify(plain_password, hashed_password)
            self.logger.debug("Password verification completed")
            return result
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Создать JWT access токен

        Args:
            data: Данные для токена
            expires_delta: Время жизни токена

        Returns:
            JWT токен
        """
        try:
            to_encode = data.copy()

            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(
                    minutes=self.access_token_expire_minutes
                )

            to_encode.update({"exp": expire, "type": "access"})
            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )

            self._jwt_tokens_created += 1
            self.logger.debug("Access token created successfully")
            return encoded_jwt

        except Exception as e:
            self.logger.error(f"Access token creation failed: {e}")
            raise

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Создать JWT refresh токен

        Args:
            data: Данные для токена

        Returns:
            JWT refresh токен
        """
        try:
            to_encode = data.copy()

            expire = datetime.now(timezone.utc) + timedelta(
                days=self.refresh_token_expire_days
            )

            to_encode.update({"exp": expire, "type": "refresh"})
            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )

            self._jwt_tokens_created += 1
            self.logger.debug("Refresh token created successfully")
            return encoded_jwt

        except Exception as e:
            self.logger.error(f"Refresh token creation failed: {e}")
            raise

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Декодировать JWT токен

        Args:
            token: JWT токен

        Returns:
            Декодированные данные или None при ошибке
        """
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None

    def verify_token_type(self, token: str, expected_type: str) -> bool:
        """
        Проверить тип токена

        Args:
            token: JWT токен
            expected_type: Ожидаемый тип (access/refresh)

        Returns:
            True если тип соответствует
        """
        payload = self.decode_token(token)
        if not payload:
            return False

        return payload.get("type") == expected_type

    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Получить время истечения токена

        Args:
            token: JWT токен

        Returns:
            Время истечения или None
        """
        payload = self.decode_token(token)
        if not payload:
            return None

        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        return None

    def generate_api_key(self, length: int = 32) -> str:
        """
        Сгенерировать API ключ

        Args:
            length: Длина ключа

        Returns:
            Случайный API ключ
        """
        return secrets.token_urlsafe(length)

    def generate_secret_key(self) -> str:
        """
        Сгенерировать секретный ключ для JWT

        Returns:
            Секретный ключ
        """
        return secrets.token_hex(32)

    def validate_api_key_format(self, api_key: str) -> bool:
        """
        Проверить формат API ключа

        Args:
            api_key: API ключ

        Returns:
            True если формат корректный
        """
        # Простая валидация: должен содержать только буквы, цифры, дефисы и подчеркивания
        pattern = r"^[a-zA-Z0-9_-]+$"
        return bool(re.match(pattern, api_key)) and len(api_key) >= 16

    def hash_api_key(self, api_key: str) -> str:
        """
        Захешировать API ключ для хранения в БД

        Args:
            api_key: API ключ

        Returns:
            Захешированный API ключ
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    def get_security_config(self) -> Dict[str, Any]:
        """
        Получить конфигурацию безопасности

        Returns:
            Настройки безопасности
        """
        return {
            "secret_key_length": 64,
            "jwt_algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
            "password_min_length": 8,
            "api_key_min_length": 16,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Получить метрики использования сервиса безопасности

        Returns:
            Метрики безопасности
        """
        return {
            "passwords_hashed": self._password_hash_count,
            "jwt_tokens_created": self._jwt_tokens_created,
            "jwt_tokens_verified": self._jwt_tokens_verified,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Глобальный экземпляр сервиса безопасности
@lru_cache(maxsize=1)
def get_security_service() -> SecurityService:
    """Получить экземпляр сервиса безопасности (кешируется)"""
    return SecurityService()


# Глобальный объект для обратной совместимости
security_service = get_security_service()


# Экспорт
__all__ = [
    "SecurityService",
    "get_security_service",
    "security_service",
]
