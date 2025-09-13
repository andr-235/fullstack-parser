"""
Конфигурация модуля Auth
"""

from pydantic import BaseModel, Field


class AuthConfig(BaseModel):
    """Конфигурация модуля аутентификации"""
    
    # JWT настройки
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
