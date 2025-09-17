"""
Сервис регистрации пользователей
"""

from typing import Dict, Any

from src.common.logging import get_logger
from src.user.exceptions import UserAlreadyExistsError

from ..interfaces import (
    IUserRepository,
    IPasswordService,
    IJWTService,
    ICacheService,
    IEventPublisher
)


class UserRegistrationService:
    """Сервис для регистрации пользователей"""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        cache_service: ICacheService = None,
        event_publisher: IEventPublisher = None
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.cache_service = cache_service
        self.event_publisher = event_publisher
        self.logger = get_logger()

    async def register_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        self.logger.info(f"Starting registration for email: {email}")

        # Проверяем, существует ли пользователь
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(email)

        # Хешируем пароль
        hashed_password = await self.password_service.hash_password(password)

        # Создаем пользователя
        user_data = {
            "email": email,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "status": "active",
            "is_superuser": False,
            "email_verified": False
        }

        self.logger.info(f"Creating user for email: {email}")
        user = await self.user_repository.create(user_data)

        # Кэшируем данные пользователя
        if self.cache_service:
            cache_key = f"user:{user.id}"
            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.status == "active"
            }
            await self.cache_service.set(cache_key, user_data)

        # Создаем токены
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "is_superuser": user.is_superuser
        }

        access_token = await self.jwt_service.create_access_token(token_data)
        refresh_token = await self.jwt_service.create_refresh_token(token_data)

        # Логируем событие
        if self.event_publisher:
            await self.event_publisher.publish_event(
                "user_registered", str(user.id), {"email": user.email}
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 минут
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_superuser": user.is_superuser
            }
        }