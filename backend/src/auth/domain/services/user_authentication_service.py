"""
Сервис аутентификации пользователей
"""

from datetime import datetime
from typing import Dict, Any, Optional

from src.common.logging import get_logger
from src.user.exceptions import UserInactiveError

from ..interfaces import (
    IUserRepository,
    IPasswordService,
    IJWTService,
    ICacheService,
    IEventPublisher
)
from ..exceptions import InvalidCredentialsError


class UserAuthenticationService:
    """Сервис для аутентификации пользователей"""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        cache_service: ICacheService = None,
        event_publisher: IEventPublisher = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.cache_service = cache_service
        self.event_publisher = event_publisher
        self.config = config or {}
        self.logger = get_logger()

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Аутентификация пользователя"""
        self.logger.info(f"Authenticating user: {email}")

        # Проверяем попытки входа
        if self.cache_service:
            await self._check_login_attempts(email)

        # Получаем пользователя
        user = await self.user_repository.get_by_email(email)
        if not user:
            await self._handle_failed_attempt(email)
            raise InvalidCredentialsError()

        # Проверяем пароль
        is_valid = await self.password_service.verify_password(password, user.hashed_password)
        if not is_valid:
            await self._handle_failed_attempt(email)
            raise InvalidCredentialsError()

        # Проверяем статус пользователя
        if user.status != "active":
            raise UserInactiveError(user.id)

        # Сбрасываем счетчик попыток
        if self.cache_service:
            await self.cache_service.delete(f"login_attempts:{email}")

        # Обновляем время последнего входа
        user.last_login = datetime.utcnow()
        await self.user_repository.update(user)

        # Создаем токены
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "is_superuser": user.is_superuser
        }

        access_token = await self.jwt_service.create_access_token(token_data)
        refresh_token = await self.jwt_service.create_refresh_token(token_data)

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

        # Логируем событие
        if self.event_publisher:
            await self.event_publisher.publish_event(
                "user_login", str(user.id), {"email": user.email}
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.config.get("access_token_expire_minutes", 30) * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_superuser": user.is_superuser
            }
        }

    async def _check_login_attempts(self, email: str) -> None:
        """Проверяет количество попыток входа"""
        attempts_key = f"login_attempts:{email}"
        attempts = await self.cache_service.get(attempts_key) or 0
        attempts = int(attempts) if attempts else 0

        max_attempts = self.config.get("max_login_attempts", 5)
        if attempts >= max_attempts:
            self.logger.warning(f"Too many login attempts for {email}")
            raise InvalidCredentialsError()

    async def _handle_failed_attempt(self, email: str) -> None:
        """Обрабатывает неудачную попытку входа"""
        if self.cache_service:
            attempts_key = f"login_attempts:{email}"
            attempts = await self.cache_service.get(attempts_key) or 0
            attempts = int(attempts) if attempts else 0
            ttl = self.config.get("login_attempts_ttl_seconds", 900)
            await self.cache_service.set(attempts_key, attempts + 1, ttl=ttl)