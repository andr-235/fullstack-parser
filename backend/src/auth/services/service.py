"""
Сервис аутентификации
"""

from typing import Any, Optional

from user.models import User
from common.logging import get_logger
from user.exceptions import UserNotFoundError

from ..config import AuthConfig
from ..exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)
from user.exceptions import UserInactiveError
from ..schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
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

    async def _get_user_repository(self):
        """Получить репозиторий пользователей"""
        if self.user_repository is None:
            from common.database import get_session_factory
            from user.repository import UserRepository
            
            # Создаем сессию напрямую
            session_factory = get_session_factory()
            db_session = session_factory()
            return UserRepository(db_session)вс
        return self.user_repository

    async def register(self, request: RegisterRequest) -> RegisterResponse:
        """Регистрация нового пользователя"""
        from common.database import get_session_factory
        from user.repository import UserRepository
        
        session_factory = get_session_factory()
        async with session_factory() as db_session:
            try:
                self.logger.info(f"Starting registration for email: {request.email}")
                user_repository = UserRepository(db_session)
                
                # Проверяем, существует ли пользователь
                existing_user = await user_repository.get_by_email(request.email)
                if existing_user:
                    from user.exceptions import UserAlreadyExistsError
                    raise UserAlreadyExistsError(request.email)

                # Хешируем пароль
                hashed_password = await self.password_service.hash_password(request.password)

                # Создаем пользователя
                user_data = {
                    "email": request.email,
                    "full_name": request.full_name,
                    "hashed_password": hashed_password,
                    "status": "active",
                    "is_superuser": False,
                    "email_verified": False
                }

                self.logger.info(f"Creating user with data: {user_data}")
                # Сохраняем в БД
                user = await user_repository.create(user_data)
                await db_session.commit()
                self.logger.info(f"User created successfully with ID: {user.id}")
            except Exception as e:
                await db_session.rollback()
                self.logger.error(f"Error in register method: {e}")
                raise

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
            if self.task_service:
                await self.task_service.log_security_event(
                    "user_registered", str(user.id), {"email": user.email}
                )

            return RegisterResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.config.access_token_expire_minutes * 60,
                user={
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_superuser": user.is_superuser
                }
            )

    async def login(self, request: LoginRequest) -> LoginResponse:
        """Вход в систему"""
        from common.database import get_session_factory
        from user.repository import UserRepository
        
        # Защита от brute force
        if self.cache_service:
            attempts_key = f"login_attempts:{request.email}"
            attempts = await self.cache_service.get(attempts_key) or 0

            if attempts >= self.config.max_login_attempts:
                self.logger.warning(f"Too many login attempts for {request.email}")
                raise InvalidCredentialsError()

        session_factory = get_session_factory()
        async with session_factory() as db_session:
            # Получаем пользователя
            user_repository = UserRepository(db_session)
            user = await user_repository.get_by_email(request.email)

            # Защита от timing attacks
            if not user:
                dummy_hash = await self.password_service.hash_password("dummy")
                await self.password_service.verify_password(request.password, dummy_hash)

                if self.cache_service:
                    await self.cache_service.set(attempts_key, attempts + 1, ttl=self.config.login_attempts_ttl_seconds)
                raise InvalidCredentialsError()

            # Проверяем пароль
            is_valid = await self.password_service.verify_password(
                request.password, user.hashed_password
            )
            if not is_valid:
                if self.cache_service:
                    await self.cache_service.set(attempts_key, attempts + 1, ttl=self.config.login_attempts_ttl_seconds)
                raise InvalidCredentialsError()

            # Проверяем активность
            if user.status != "active":
                raise UserInactiveError(user.id)

            # Сбрасываем счетчик попыток
            if self.cache_service:
                await self.cache_service.delete(attempts_key)

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

            # Обновляем время последнего входа
            from datetime import datetime
            user.last_login = datetime.utcnow()
            await user_repository.update(user)
            await db_session.commit()

            # Логируем событие
            if self.task_service:
                await self.task_service.log_security_event(
                    "user_login", str(user.id), {"email": user.email}
                )

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.config.access_token_expire_minutes * 60,
                user={
                    "id": user.id,
                    "email": user.email,
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
        from common.database import get_session_factory
        from user.repository import UserRepository
        
        is_valid = await self.password_service.verify_password(
            request.current_password, user.hashed_password
        )
        if not is_valid:
            raise InvalidCredentialsError()

        new_hashed_password = await self.password_service.hash_password(request.new_password)
        user.hashed_password = new_hashed_password
        
        session_factory = get_session_factory()
        async with session_factory() as db_session:
            user_repository = UserRepository(db_session)
            await user_repository.update(user)
            await db_session.commit()

        # Инвалидируем кэш
        if self.cache_service:
            cache_key = f"user:{user.id}"
            await self.cache_service.delete(cache_key)

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                "password_changed", str(user.id), {"email": user.email}
            )

    async def reset_password(self, request: ResetPasswordRequest) -> None:
        """Запросить сброс пароля"""
        from common.database import get_session_factory
        from user.repository import UserRepository
        
        session_factory = get_session_factory()
        async with session_factory() as db_session:
            user_repository = UserRepository(db_session)
            user = await user_repository.get_by_email(request.email)
            if not user:
                # Не раскрываем информацию о существовании пользователя
                return

            reset_token = await self.jwt_service.create_access_token({
                "sub": str(user.id),
                "email": user.email,
                "type": "password_reset"
            })

            if self.task_service:
                await self.task_service.send_password_reset_email(user.email, reset_token)
                await self.task_service.log_security_event(
                    "password_reset_requested", str(user.id), {"email": user.email}
                )

    async def reset_password_confirm(self, request: ResetPasswordConfirmRequest) -> None:
        """Подтвердить сброс пароля"""
        from common.database import get_session_factory
        from user.repository import UserRepository
        
        token_data = await self.jwt_service.validate_token(request.token)
        if not token_data or token_data.get("type") != "password_reset":
            raise InvalidTokenError()

        user_id = token_data.get("sub")
        if not user_id:
            raise InvalidTokenError()

        session_factory = get_session_factory()
        async with session_factory() as db_session:
            user_repository = UserRepository(db_session)
            user = await user_repository.get_by_id(int(user_id))
            if not user:
                raise UserNotFoundError()

            new_hashed_password = await self.password_service.hash_password(request.new_password)
            user.hashed_password = new_hashed_password
            await user_repository.update(user)
            await db_session.commit()

        # Инвалидируем кэш
        if self.cache_service:
            cache_key = f"user:{user.id}"
            await self.cache_service.delete(cache_key)

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                "password_reset_completed", str(user.id), {"email": user.email}
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
        from common.database import get_session_factory
        from user.repository import UserRepository
        
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
                    session_factory = get_session_factory()
                    async with session_factory() as db_session:
                        user_repository = UserRepository(db_session)
                        user = await user_repository.get_by_id(int(user_id))
                        return user

            session_factory = get_session_factory()
            async with session_factory() as db_session:
                user_repository = UserRepository(db_session)
                user = await user_repository.get_by_id(int(user_id))

                # Кэшируем
                if self.cache_service and user:
                    cache_key = f"user:{user_id}"
                    user_data = {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "is_active": user.status == "active"
                    }
                    await self.cache_service.set(cache_key, user_data)

                return user

        except (InvalidTokenError, TokenExpiredError, UserNotFoundError) as e:
            self.logger.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during token validation: {e}")
            return None
