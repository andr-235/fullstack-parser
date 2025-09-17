"""
Сервис аутентификации с оптимизациями производительности
"""

from datetime import datetime
from typing import Any, Optional

from src.common.logging import get_logger
from src.user.exceptions import (
    UserAlreadyExistsError,
    UserInactiveError,
    UserNotFoundError,
)
from src.user.models import User

from ..config import AuthConfig
from ..exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)
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
from .validator import AuthValidator

# Константы
USER_STATUS_ACTIVE = "active"
TOKEN_TYPE_PASSWORD_RESET = "password_reset"
SECURITY_EVENT_USER_REGISTERED = "user_registered"
SECURITY_EVENT_USER_LOGIN = "user_login"
SECURITY_EVENT_PASSWORD_CHANGED = "password_changed"
SECURITY_EVENT_PASSWORD_RESET_REQUESTED = "password_reset_requested"
SECURITY_EVENT_PASSWORD_RESET_COMPLETED = "password_reset_completed"
SECURITY_EVENT_USER_LOGOUT = "user_logout"


class AuthService:
    """Сервис аутентификации с оптимизациями производительности"""

    def __init__(
        self,
        user_repository: Any,
        password_service: Any,
        jwt_service: Any,
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
        self.validator = AuthValidator(self.config)

        # Кеш для часто используемых данных
        self._user_cache_ttl = self.config.user_cache_ttl_seconds
        self._login_attempts_ttl = self.config.login_attempts_ttl_seconds

    async def _get_user_repository(self):
        """Получить репозиторий пользователей с оптимизацией"""
        if self.user_repository is None:
            from src.shared.infrastructure.database.session import get_async_session
            from src.user.infrastructure.repositories import UserRepository

            # Создаем сессию напрямую
            db_session = get_async_session()
            return UserRepository(db_session)
        return self.user_repository

    async def _get_db_session_and_repo(self):
        """Получить сессию БД и репозиторий (оптимизированный метод)"""
        from src.shared.infrastructure.database.session import get_async_session
        from src.user.infrastructure.repositories import UserRepository

        db_session = get_async_session()
        user_repository = UserRepository(db_session)
        return db_session, user_repository

    async def _cache_user_data(self, user: User) -> None:
        """Кешировать полные данные пользователя"""
        if self.cache_service:
            cache_key = f"user:{user.id}"
            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.status == USER_STATUS_ACTIVE,
                "is_superuser": user.is_superuser,
                "email_verified": user.email_verified,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "cached_at": datetime.utcnow().timestamp()
            }
            await self.cache_service.set(cache_key, user_data, ttl=self._user_cache_ttl)

    async def _get_cached_user(self, user_id: str) -> Optional[dict]:
        """Получить пользователя из кеша"""
        if self.cache_service:
            cache_key = f"user:{user_id}"
            cached_data = await self.cache_service.get(cache_key)
            if cached_data and isinstance(cached_data, dict):
                # Проверяем актуальность кеша
                cached_at = cached_data.get("cached_at", 0)
                if datetime.utcnow().timestamp() - cached_at < self._user_cache_ttl:
                    return cached_data
                else:
                    # Кеш устарел, удаляем
                    await self.cache_service.delete(cache_key)
        return None

    async def _invalidate_user_cache(self, user_id: str) -> None:
        """Инвалидировать кеш пользователя"""
        if self.cache_service:
            cache_key = f"user:{user_id}"
            await self.cache_service.delete(cache_key)

    async def register(self, request: RegisterRequest) -> RegisterResponse:
        """Регистрация нового пользователя с оптимизациями и валидацией"""
        # Валидация входных данных
        await self.validator.validate_registration_data(
            request.email, request.password, request.full_name
        )

        db_session, user_repository = await self._get_db_session_and_repo()

        async with db_session:
            try:
                self.logger.info(f"Starting registration for email: {request.email}")

                # Проверяем, существует ли пользователь (с кешем)
                existing_user = await user_repository.get_by_email(request.email)
                if existing_user:
                    raise UserAlreadyExistsError(request.email)

                # Хешируем пароль
                hashed_password = await self.password_service.hash_password(request.password)

                # Создаем пользователя
                user_data = {
                    "email": request.email,
                    "full_name": request.full_name,
                    "hashed_password": hashed_password,
                    "status": USER_STATUS_ACTIVE,
                    "is_superuser": False,
                    "email_verified": False
                }

                self.logger.info(f"Creating user for email: {request.email}")
                user = await user_repository.create(user_data)
                await db_session.commit()
                self.logger.info(f"User created successfully with ID: {user.id}")

                # Кешируем данные пользователя
                await self._cache_user_data(user)

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

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                SECURITY_EVENT_USER_REGISTERED, str(user.id), {"email": user.email}
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
        """Вход в систему с оптимизациями и валидацией"""
        # Валидация входных данных
        await self.validator.validate_login_data(request.email, request.password)

        # Защита от brute force
        if self.cache_service:
            attempts_key = f"login_attempts:{request.email}"
            attempts = await self.cache_service.get(attempts_key) or 0
            attempts = int(attempts) if attempts else 0

            if attempts >= self.config.max_login_attempts:
                self.logger.warning(f"Too many login attempts for {request.email}")
                raise InvalidCredentialsError()

        db_session, user_repository = await self._get_db_session_and_repo()

        async with db_session:
            # Получаем пользователя
            user = await user_repository.get_by_email(request.email)

            # Защита от timing attacks
            if not user:
                dummy_hash = await self.password_service.hash_password("dummy")
                await self.password_service.verify_password(request.password, dummy_hash)

                if self.cache_service:
                    await self.cache_service.set(attempts_key, attempts + 1, ttl=self._login_attempts_ttl)
                raise InvalidCredentialsError()

            # Проверяем пароль
            is_valid = await self.password_service.verify_password(
                request.password, user.hashed_password
            )
            if not is_valid:
                if self.cache_service:
                    await self.cache_service.set(attempts_key, attempts + 1, ttl=self._login_attempts_ttl)
                raise InvalidCredentialsError()

            # Проверяем активность
            if user.status != USER_STATUS_ACTIVE:
                raise UserInactiveError(user.id)

            # Сбрасываем счетчик попыток
            if self.cache_service:
                await self.cache_service.delete(attempts_key)

            # Обновляем время последнего входа
            user.last_login = datetime.utcnow()
            await user_repository.update(user)
            await db_session.commit()

            # Кешируем данные пользователя
            await self._cache_user_data(user)

        # Создаем токены
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "is_superuser": user.is_superuser
        }

        access_token = await self.jwt_service.create_access_token(token_data)
        refresh_token = await self.jwt_service.create_refresh_token(token_data)

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                SECURITY_EVENT_USER_LOGIN, str(user.id), {"email": user.email}
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
        """Обновить access токен с оптимизацией"""
        token_data = await self.jwt_service.validate_token(request.refresh_token)
        if not token_data:
            raise InvalidTokenError()

        access_token = await self.jwt_service.create_access_token(token_data)

        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=self.config.access_token_expire_minutes * 60
        )

    async def change_password(self, user: User, request: ChangePasswordRequest) -> None:
        """Сменить пароль с оптимизациями и валидацией"""
        # Валидация входных данных
        await self.validator.validate_password_change_data(
            request.current_password, request.new_password
        )

        # Проверяем текущий пароль
        is_valid = await self.password_service.verify_password(
            request.current_password, user.hashed_password
        )
        if not is_valid:
            raise InvalidCredentialsError()

        # Хешируем новый пароль
        new_hashed_password = await self.password_service.hash_password(request.new_password)
        user.hashed_password = new_hashed_password

        db_session, user_repository = await self._get_db_session_and_repo()

        async with db_session:
            await user_repository.update(user)
            await db_session.commit()

        # Инвалидируем кеш
        await self._invalidate_user_cache(str(user.id))

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                SECURITY_EVENT_PASSWORD_CHANGED, str(user.id), {"email": user.email}
            )

    async def reset_password(self, request: ResetPasswordRequest) -> None:
        """Запросить сброс пароля с оптимизациями"""
        db_session, user_repository = await self._get_db_session_and_repo()

        async with db_session:
            user = await user_repository.get_by_email(request.email)
            if not user:
                # Не раскрываем информацию о существовании пользователя
                return

            reset_token = await self.jwt_service.create_access_token({
                "sub": str(user.id),
                "email": user.email,
                "type": TOKEN_TYPE_PASSWORD_RESET
            })

            if self.task_service:
                await self.task_service.send_password_reset_email(user.email, reset_token)
                await self.task_service.log_security_event(
                    SECURITY_EVENT_PASSWORD_RESET_REQUESTED, str(user.id), {"email": user.email}
                )

    async def reset_password_confirm(self, request: ResetPasswordConfirmRequest) -> None:
        """Подтвердить сброс пароля с оптимизациями и валидацией"""
        # Валидация входных данных
        await self.validator.validate_password_reset_data(request.new_password)

        token_data = await self.jwt_service.validate_token(request.token)
        if not token_data or token_data.get("type") != TOKEN_TYPE_PASSWORD_RESET:
            raise InvalidTokenError()

        user_id = token_data.get("sub")
        if not user_id:
            raise InvalidTokenError()

        db_session, user_repository = await self._get_db_session_and_repo()

        async with db_session:
            user = await user_repository.get_by_id(int(user_id))
            if not user:
                raise UserNotFoundError()

            new_hashed_password = await self.password_service.hash_password(request.new_password)
            user.hashed_password = new_hashed_password
            await user_repository.update(user)
            await db_session.commit()

        # Инвалидируем кеш
        await self._invalidate_user_cache(user_id)

        # Логируем событие
        if self.task_service:
            await self.task_service.log_security_event(
                SECURITY_EVENT_PASSWORD_RESET_COMPLETED, user_id, {"email": token_data.get("email")}
            )

    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """Выход из системы с оптимизациями"""
        try:
            if refresh_token:
                await self.jwt_service.revoke_token(refresh_token)
                token_data = await self.jwt_service.decode_token(refresh_token)
                if token_data and self.task_service:
                    await self.task_service.log_security_event(
                        SECURITY_EVENT_USER_LOGOUT, token_data.get("sub", "unknown"),
                        {"email": token_data.get("email", "unknown")}
                    )
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")

    async def validate_user_token(self, token: str) -> Optional[User]:
        """Валидировать токен и получить пользователя с оптимизациями"""
        try:
            token_data = await self.jwt_service.validate_token(token)
            if not token_data:
                return None

            user_id = token_data.get("sub")
            if not user_id:
                return None

            # Проверяем кеш сначала
            cached_user_data = await self._get_cached_user(user_id)
            if cached_user_data:
                # Возвращаем данные из кеша без обращения к БД
                return User(
                    id=cached_user_data["id"],
                    email=cached_user_data["email"],
                    full_name=cached_user_data["full_name"],
                    hashed_password="",  # Не возвращаем пароль
                    status=cached_user_data["is_active"] and USER_STATUS_ACTIVE or "inactive",
                    is_superuser=cached_user_data.get("is_superuser", False),
                    last_login=datetime.fromisoformat(cached_user_data["last_login"]) if cached_user_data.get("last_login") else None,
                    login_attempts=0,
                    locked_until=None,
                    email_verified=cached_user_data.get("email_verified", False),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

            # Если нет в кеше, получаем из БД
            from src.common.database import get_session_factory
            from src.user.repository import UserRepository

            session_factory = get_session_factory()
            async with session_factory() as db_session:
                user_repository = UserRepository(db_session)
                user = await user_repository.get_by_id(int(user_id))

                # Кешируем для будущих запросов
                if user:
                    await self._cache_user_data(user)

                return user

        except (InvalidTokenError, TokenExpiredError, UserNotFoundError) as e:
            self.logger.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during token validation: {e}")
            return None