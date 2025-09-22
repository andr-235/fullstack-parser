"""
Конфигурация модуля Auth
"""

from pydantic import BaseModel, Field


class AuthConfig(BaseModel):
    """Конфигурация модуля аутентификации"""

    # JWT настройки
    secret_key: str = Field(default="your-secret-key-here")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

    # Кэширование
    user_cache_ttl_seconds: int = Field(default=3600)
    login_attempts_ttl_seconds: int = Field(default=900)

    # Безопасность
    max_login_attempts: int = Field(default=5)
    password_min_length: int = Field(default=8)
    password_rounds: int = Field(default=12)

    # Rate limiting
    login_rate_limit: str = Field(default="5/minute")

    # Email
    password_reset_token_expire_hours: int = Field(default=24)
    email_verification_token_expire_hours: int = Field(default=24)

    # Константы (из constants.py)
    # Статусы пользователей
    USER_STATUS_ACTIVE: str = Field(default="active")
    USER_STATUS_INACTIVE: str = Field(default="inactive")
    USER_STATUS_LOCKED: str = Field(default="locked")

    # Типы токенов
    TOKEN_TYPE_ACCESS: str = Field(default="access")
    TOKEN_TYPE_REFRESH: str = Field(default="refresh")
    TOKEN_TYPE_PASSWORD_RESET: str = Field(default="password_reset")

    # Типы событий безопасности
    SECURITY_EVENT_USER_REGISTERED: str = Field(default="user_registered")
    SECURITY_EVENT_USER_LOGIN: str = Field(default="user_login")
    SECURITY_EVENT_USER_LOGOUT: str = Field(default="user_logout")
    SECURITY_EVENT_PASSWORD_CHANGED: str = Field(default="password_changed")
    SECURITY_EVENT_PASSWORD_RESET_REQUESTED: str = Field(default="password_reset_requested")
    SECURITY_EVENT_PASSWORD_RESET_COMPLETED: str = Field(default="password_reset_completed")

    # Кеш ключи
    CACHE_KEY_USER_PREFIX: str = Field(default="user:")
    CACHE_KEY_LOGIN_ATTEMPTS_PREFIX: str = Field(default="login_attempts:")
    CACHE_KEY_TOKEN_PREFIX: str = Field(default="token:")

    # Ограничения
    LIMIT_MAX_LOGIN_ATTEMPTS: int = Field(default=5)
    LIMIT_LOGIN_ATTEMPTS_TTL_SECONDS: int = Field(default=900)
    LIMIT_PASSWORD_MIN_LENGTH: int = Field(default=8)
    LIMIT_EMAIL_MAX_LENGTH: int = Field(default=255)
    LIMIT_FULL_NAME_MAX_LENGTH: int = Field(default=100)
