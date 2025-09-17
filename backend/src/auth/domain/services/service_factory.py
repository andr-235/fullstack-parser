"""
Фабрика для создания сервисов аутентификации
"""

from typing import Dict, Any, Optional

from .user_registration_service import UserRegistrationService
from .user_authentication_service import UserAuthenticationService
from .password_reset_service import PasswordResetService
from .token_management_service import TokenManagementService
from .auth_service_refactored import AuthServiceRefactored

from ..interfaces import (
    IUserRepository,
    IPasswordService,
    IJWTService,
    ICacheService,
    IEventPublisher
)


class AuthServiceFactory:
    """Фабрика для создания сервисов аутентификации"""

    @staticmethod
    def create_user_registration_service(
        user_repository: IUserRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        cache_service: ICacheService = None,
        event_publisher: IEventPublisher = None
    ) -> UserRegistrationService:
        """Создает сервис регистрации пользователей"""
        return UserRegistrationService(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service,
            cache_service=cache_service,
            event_publisher=event_publisher
        )

    @staticmethod
    def create_user_authentication_service(
        user_repository: IUserRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        cache_service: ICacheService = None,
        event_publisher: IEventPublisher = None,
        config: Optional[Dict[str, Any]] = None
    ) -> UserAuthenticationService:
        """Создает сервис аутентификации пользователей"""
        return UserAuthenticationService(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service,
            cache_service=cache_service,
            event_publisher=event_publisher,
            config=config
        )

    @staticmethod
    def create_password_reset_service(
        user_repository: IUserRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        event_publisher: IEventPublisher = None
    ) -> PasswordResetService:
        """Создает сервис сброса паролей"""
        return PasswordResetService(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service,
            event_publisher=event_publisher
        )

    @staticmethod
    def create_token_management_service(
        jwt_service: IJWTService,
        cache_service: ICacheService = None,
        config: Optional[Dict[str, Any]] = None
    ) -> TokenManagementService:
        """Создает сервис управления токенами"""
        return TokenManagementService(
            jwt_service=jwt_service,
            cache_service=cache_service,
            config=config
        )

    @classmethod
    def create_auth_service(
        cls,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        cache_service: ICacheService = None,
        event_publisher: IEventPublisher = None,
        config: Optional[Dict[str, Any]] = None
    ) -> AuthServiceRefactored:
        """Создает основной сервис аутентификации"""
        user_registration_service = cls.create_user_registration_service(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service,
            cache_service=cache_service,
            event_publisher=event_publisher
        )

        user_authentication_service = cls.create_user_authentication_service(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service,
            cache_service=cache_service,
            event_publisher=event_publisher,
            config=config
        )

        password_reset_service = cls.create_password_reset_service(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service,
            event_publisher=event_publisher
        )

        token_management_service = cls.create_token_management_service(
            jwt_service=jwt_service,
            cache_service=cache_service,
            config=config
        )

        return AuthServiceRefactored(
            user_registration_service=user_registration_service,
            user_authentication_service=user_authentication_service,
            password_reset_service=password_reset_service,
            token_management_service=token_management_service
        )