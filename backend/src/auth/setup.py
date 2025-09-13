"""
Настройка модуля Auth
"""

from typing import Optional, Any
import redis.asyncio as redis
from .services import AuthService, PasswordService, JWTService
from .config import AuthConfig
from shared.infrastructure.logging import get_logger


class AuthSetup:
    """Настройка модуля Auth"""
    
    def __init__(self):
        self._auth_service: Optional[AuthService] = None
        self._password_service: Optional[PasswordService] = None
        self._jwt_service: Optional[JWTService] = None
        self._cache_service: Optional[Any] = None
        self._config: Optional[AuthConfig] = None
        self.logger = get_logger()
    
    def setup(
        self,
        user_repository,
        redis_url: str = "redis://localhost:6379/0",
        secret_key: str = "your-secret-key",
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        password_rounds: int = 12,
        config: Optional[AuthConfig] = None
    ):
        """Настроить все сервисы"""
        self._config = config or AuthConfig(
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
            password_rounds=password_rounds
        )
        
        # Создаем сервисы
        self._password_service = PasswordService(rounds=password_rounds)
        
        self._jwt_service = JWTService(
            secret_key=secret_key,
            algorithm=algorithm,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
            cache_service=self._cache_service
        )
        
        # Настраиваем Redis если нужно
        if redis_url:
            self._cache_service = redis.from_url(redis_url)
        
        # Создаем основной сервис
        self._auth_service = AuthService(
            user_repository=user_repository,
            password_service=self._password_service,
            jwt_service=self._jwt_service,
            cache_service=self._cache_service,
            config=self._config
        )
        
        self.logger.info("Auth module setup completed")
    
    def get_auth_service(self) -> AuthService:
        """Получить сервис аутентификации"""
        if not self._auth_service:
            raise RuntimeError("Auth service not initialized. Call setup() first.")
        return self._auth_service
    
    def get_password_service(self) -> PasswordService:
        """Получить сервис паролей"""
        if not self._password_service:
            raise RuntimeError("Password service not initialized. Call setup() first.")
        return self._password_service
    
    def get_jwt_service(self) -> JWTService:
        """Получить JWT сервис"""
        if not self._jwt_service:
            raise RuntimeError("JWT service not initialized. Call setup() first.")
        return self._jwt_service
    
    def get_cache_service(self):
        """Получить сервис кэширования"""
        return self._cache_service
    
    def get_config(self) -> AuthConfig:
        """Получить конфигурацию"""
        if not self._config:
            raise RuntimeError("Config not initialized. Call setup() first.")
        return self._config


# Глобальный экземпляр
_auth_setup = AuthSetup()


def setup_auth(
    user_repository,
    redis_url: str = "redis://localhost:6379/0",
    secret_key: str = "your-secret-key",
    algorithm: str = "HS256",
    access_token_expire_minutes: int = 30,
    refresh_token_expire_days: int = 7,
    password_rounds: int = 12,
    config: Optional[AuthConfig] = None
):
    """Настроить модуль Auth"""
    _auth_setup.setup(
        user_repository=user_repository,
        redis_url=redis_url,
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=access_token_expire_minutes,
        refresh_token_expire_days=refresh_token_expire_days,
        password_rounds=password_rounds,
        config=config
    )


def get_auth_service() -> AuthService:
    """Получить сервис аутентификации"""
    return _auth_setup.get_auth_service()


def get_password_service() -> PasswordService:
    """Получить сервис паролей"""
    return _auth_setup.get_password_service()


def get_jwt_service() -> JWTService:
    """Получить JWT сервис"""
    return _auth_setup.get_jwt_service()


def get_cache_service():
    """Получить сервис кэширования"""
    return _auth_setup.get_cache_service()


def get_auth_config() -> AuthConfig:
    """Получить конфигурацию"""
    return _auth_setup.get_config()
