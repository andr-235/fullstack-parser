"""
Настройка модуля Auth
"""

from typing import Any, Optional

from common.logging import get_logger

from .config import AuthConfig
from .domain.services.service_factory import AuthServiceFactory
from .infrastructure.adapters.cache_adapter import RedisCacheAdapter, InMemoryCacheAdapter
from .infrastructure.adapters.event_publisher_adapter import EventPublisherAdapter, NoOpEventPublisher
from .infrastructure.adapters.jwt_adapter import JWTServiceAdapter
from .infrastructure.adapters.password_adapter import PasswordServiceAdapter
from .infrastructure.adapters.user_repository_adapter import UserRepositoryAdapter
from .services import JWTService, PasswordService


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
        user_repository=None,
        redis_client=None,
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
            password_rounds=password_rounds,
            max_login_attempts=5
        )

        # Создаем базовые сервисы
        self._password_service = PasswordService(rounds=password_rounds)
        self._jwt_service = JWTService(
            secret_key=secret_key,
            algorithm=algorithm,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
            cache_service=self._cache_service
        )

        # Настраиваем кеширование
        if redis_client:
            self._cache_service = RedisCacheAdapter(redis_client)
        else:
            self._cache_service = InMemoryCacheAdapter()

        # Создаем адаптеры
        user_repo_adapter = UserRepositoryAdapter(user_repository) if user_repository else None
        password_adapter = PasswordServiceAdapter(self._password_service)
        jwt_adapter = JWTServiceAdapter(self._jwt_service)
        cache_adapter = self._cache_service
        event_publisher = NoOpEventPublisher()  # Можно заменить на реальный адаптер

        # Создаем сервис через фабрику
        factory = AuthServiceFactory()
        self._auth_service = factory.create_auth_service(
            user_repository=user_repo_adapter,
            password_service=password_adapter,
            jwt_service=jwt_adapter,
            cache_service=cache_adapter,
            event_publisher=event_publisher,
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
    user_repository=None,
    redis_client=None,
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
        redis_client=redis_client,
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=access_token_expire_minutes,
        refresh_token_expire_days=refresh_token_expire_days,
        password_rounds=password_rounds,
        config=config
    )


def get_auth_service() -> AuthServiceInterface:
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
