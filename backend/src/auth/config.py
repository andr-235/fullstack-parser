"""
Конфигурация модуля Auth

Содержит настройки специфичные для модуля аутентификации
"""

from typing import Optional

from ..config import settings


class AuthConfig:
    """Конфигурация для модуля аутентификации"""

    # Настройки JWT
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    # Настройки паролей
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128

    # Настройки безопасности
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    REQUIRE_EMAIL_VERIFICATION = False

    # Настройки сброса пароля
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 24
    PASSWORD_RESET_RATE_LIMIT = 3  # попыток в час

    # Настройки регистрации
    ALLOW_PUBLIC_REGISTRATION = True
    REQUIRE_EMAIL_CONFIRMATION = False

    # Настройки кеширования
    CACHE_USER_TTL = 300  # 5 минут
    CACHE_TOKEN_TTL = 3600  # 1 час

    # Настройки rate limiting
    LOGIN_RATE_LIMIT = 5  # попыток в минуту
    REGISTER_RATE_LIMIT = 3  # попыток в час

    @classmethod
    def get_jwt_config(cls) -> dict:
        """Получить конфигурацию JWT"""
        return {
            "algorithm": settings.jwt_algorithm or cls.JWT_ALGORITHM,
            "access_token_expire_minutes": cls.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": cls.REFRESH_TOKEN_EXPIRE_DAYS,
            "secret_key": settings.secret_key,
        }

    @classmethod
    def get_password_config(cls) -> dict:
        """Получить конфигурацию паролей"""
        return {
            "min_length": cls.PASSWORD_MIN_LENGTH,
            "max_length": cls.PASSWORD_MAX_LENGTH,
        }

    @classmethod
    def get_security_config(cls) -> dict:
        """Получить конфигурацию безопасности"""
        return {
            "max_login_attempts": cls.MAX_LOGIN_ATTEMPTS,
            "lockout_duration_minutes": cls.LOCKOUT_DURATION_MINUTES,
            "require_email_verification": cls.REQUIRE_EMAIL_VERIFICATION,
        }

    @classmethod
    def get_registration_config(cls) -> dict:
        """Получить конфигурацию регистрации"""
        return {
            "allow_public_registration": cls.ALLOW_PUBLIC_REGISTRATION,
            "require_email_confirmation": cls.REQUIRE_EMAIL_CONFIRMATION,
        }

    @classmethod
    def get_cache_config(cls) -> dict:
        """Получить конфигурацию кеширования"""
        return {
            "enabled": settings.cache_enabled,
            "user_ttl": cls.CACHE_USER_TTL,
            "token_ttl": cls.CACHE_TOKEN_TTL,
        }


# Экземпляр конфигурации
auth_config = AuthConfig()


# Экспорт
__all__ = [
    "AuthConfig",
    "auth_config",
]
