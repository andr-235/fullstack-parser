"""
Сервис аутентификации
"""

from typing import Any, Optional

from common.logging import get_logger
from common.exceptions import ValidationError, NotFoundError

from .config import AuthConfig
from .exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)
from .schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordConfirmRequest,
    ResetPasswordRequest,
)


class AuthService:
    """Сервис аутентификации"""

    def __init__(
        self,
        user_repository,
        password_service,
        jwt_service,
        cache_service: Optional[Any] = None,
        task_service: Optional[Any] = None,
        config: Optional[AuthConfig] = None
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.cache_service = cache_service
        self.task_service = task_service
        self.config = config or AuthConfig()
        self.logger = get_logger()

    async def login(self, request: LoginRequest) -> LoginResponse:
        """Вход в систему"""
        # Защита от brute force
        if self.cache_service:
            attempts_key = f"login_attempts:{request.email}"
            attempts = await self.cache_service.get(attempts_key) or 0

            if attempts >= self.config.max_login_attempts:
                self.logger.warning(f"Too many login attempts for {request.email}")
                raise InvalidCredentialsError()

        # Получаем пользователя
        user = await self.user_repository.get_by_email(request.email)

        # Защита от timing attacks
        if not user:
            dummy_hash = await self.password_service.hash_password("dummy")
            await self.password_service.verify_password(request.password, dummy_hash)

            if self.cache_service:
                await self.cache_service.set(attempts_key, attempts + 1, ttl=self.config.login_attempts_ttl_seconds)
            raise InvalidCredentialsError()

        # Проверяем пароль
        is_valid = await self.password_service.verify_password(
            request.password, user.hashed_password.value
        )
        if not is_valid:
            if self.cache_service:
                await self.cache_service.set(attempts_key, attempts + 1, ttl=self.config.login_attempts_ttl_seconds)
            raise InvalidCredentialsError()

        # Проверяем активность
        if not user.can_login():
            raise UserInactiveError(user.id.value)

        # Сбрасываем счетчик попыток
        if self.cache_service:
            await self.cache_service.delete(attempts_key)

        # Создаем токены
        token_data = {
            "sub": str(user.id.value),
            "email": user.email.value,
            "is_superuser": user.is_superuser
        }

        access_token = await self.jwt_service.create_access_token(token_data)
        refresh_token = await self.jwt_service.create_refresh_token(token_data)

        # Кэшируем данные пользователя
        if self.cache_service:
            cache_key = f"user:{user.id.value}"
            user_data = {
                "id": user.id.value,
                "email": user.email.value,
                "full_name": user.full_name,
                "is_active": user.is_active
            }
            await self.cache_service.set(cache_key, user_data, ttl=self.config.user_cache_ttl_seconds)

        # Обновляем время последнего входа
        updated_user = user.update_login_time()
        await self.user_repository.update(updated_user)

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                "user_login", str(user.id.value), {"email": user.email.value}
            )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.access_token_expire_minutes * 60,
            user={
                "id": user.id.value,
                "email": user.email.value,
                "full_name": user.full_name,
                "is_superuser": user.is_superuser
            }
        )

    async def refresh_token(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        """Обновить access токен"""
        token_data = await self.jwt_service.validate_token(request.refresh_token)
        if not token_data:
            raise InvalidTokenError()

        access_token = await self.jwt_service.create_access_token(token_data)

        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=self.config.access_token_expire_minutes * 60
        )

    async def change_password(self, user: User, request: ChangePasswordRequest) -> None:
        """Сменить пароль"""
        is_valid = await self.password_service.verify_password(
            request.current_password, user.hashed_password.value
        )
        if not is_valid:
            raise InvalidCredentialsError()

        new_hashed_password = await self.password_service.hash_password(request.new_password)
        updated_user = user.change_password(new_hashed_password)
        await self.user_repository.update(updated_user)

        # Инвалидируем кэш
        if self.cache_service:
            cache_key = f"user:{user.id.value}"
            await self.cache_service.delete(cache_key)

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                "password_changed", str(user.id.value), {"email": user.email.value}
            )

    async def reset_password(self, request: ResetPasswordRequest) -> None:
        """Запросить сброс пароля"""
        user = await self.user_repository.get_by_email(request.email)
        if not user:
            # Не раскрываем информацию о существовании пользователя
            return

        reset_token = await self.jwt_service.create_access_token({
            "sub": str(user.id.value),
            "email": user.email.value,
            "type": "password_reset"
        })

        if self.task_service:
            await self.task_service.send_password_reset_email(user.email.value, reset_token)
            await self.task_service.log_security_event(
                "password_reset_requested", str(user.id.value), {"email": user.email.value}
            )

    async def reset_password_confirm(self, request: ResetPasswordConfirmRequest) -> None:
        """Подтвердить сброс пароля"""
        token_data = await self.jwt_service.validate_token(request.token)
        if not token_data or token_data.get("type") != "password_reset":
            raise InvalidTokenError()

        user_id = token_data.get("sub")
        if not user_id:
            raise InvalidTokenError()

        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise UserNotFoundError()

        new_hashed_password = await self.password_service.hash_password(request.new_password)
        updated_user = user.change_password(new_hashed_password)
        await self.user_repository.update(updated_user)

        # Инвалидируем кэш
        if self.cache_service:
            cache_key = f"user:{user.id.value}"
            await self.cache_service.delete(cache_key)

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                "password_reset_completed", str(user.id.value), {"email": user.email.value}
            )

    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """Выход из системы"""
        try:
            if refresh_token:
                await self.jwt_service.revoke_token(refresh_token)
                token_data = await self.jwt_service.decode_token(refresh_token)
                if token_data and self.task_service:
                    await self.task_service.log_security_event(
                        "user_logout", token_data.get("sub", "unknown"),
                        {"email": token_data.get("email", "unknown")}
                    )
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")

    async def validate_user_token(self, token: str) -> Optional[User]:
        """Валидировать токен и получить пользователя"""
        try:
            token_data = await self.jwt_service.validate_token(token)
            if not token_data:
                return None

            user_id = token_data.get("sub")
            if not user_id:
                return None

            # Проверяем кэш
            if self.cache_service:
                cache_key = f"user:{user_id}"
                cached_data = await self.cache_service.get(cache_key)
                if cached_data:
                    user = await self.user_repository.get_by_id(int(user_id))
                    return user

            user = await self.user_repository.get_by_id(int(user_id))

            # Кэшируем
            if self.cache_service and user:
                cache_key = f"user:{user_id}"
                user_data = {
                    "id": user.id.value,
                    "email": user.email.value,
                    "full_name": user.full_name,
                    "is_active": user.is_active
                }
                await self.cache_service.set(cache_key, user_data, ttl=self.config.user_cache_ttl_seconds)

            return user

        except (InvalidTokenError, TokenExpiredError, UserNotFoundError) as e:
            self.logger.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during token validation: {e}")
            return None
