"""
Сервис аутентификации - упрощенная версия для маленького проекта
"""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.logging import get_logger
from src.user.exceptions import UserAlreadyExistsError, UserInactiveError, UserNotFoundError
from src.user.models import User
from src.user.repository import UserRepository

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
    RegisterRequest,
    RegisterResponse,
    ResetPasswordConfirmRequest,
    ResetPasswordRequest,
)


class AuthService:
    """Сервис аутентификации с упрощенной архитектурой"""

    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
        self.logger = get_logger(__name__)

    async def register(self, request: RegisterRequest) -> RegisterResponse:
        """Регистрация нового пользователя"""
        from src.shared.infrastructure.database.session import get_async_session

        async with get_async_session() as session:
            user_repo = UserRepository(session)

            # Проверяем, существует ли пользователь
            existing_user = await user_repo.get_by_email(request.email)
            if existing_user:
                raise UserAlreadyExistsError(request.email)

            # Хешируем пароль
            hashed_password = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()

            # Создаем пользователя
            user_data = {
                "email": request.email,
                "full_name": request.full_name,
                "hashed_password": hashed_password,
                "status": "active",
                "is_superuser": False,
                "email_verified": False
            }

            user = await user_repo.create(user_data)
            await session.commit()

            # Создаем токены
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "is_superuser": user.is_superuser
            }

            access_token = self._create_access_token(token_data)
            refresh_token = self._create_refresh_token(token_data)

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
        from src.shared.infrastructure.database.session import get_async_session

        async with get_async_session() as session:
            user_repo = UserRepository(session)

            # Получаем пользователя
            user = await user_repo.get_by_email(request.email)
            if not user:
                raise InvalidCredentialsError()

            # Проверяем пароль
            if not bcrypt.checkpw(request.password.encode(), user.hashed_password.encode()):
                raise InvalidCredentialsError()

            # Проверяем активность
            if user.status != "active":
                raise UserInactiveError(user.id)

            # Обновляем время последнего входа
            user.last_login = datetime.utcnow()
            await user_repo.update(user)
            await session.commit()

            # Создаем токены
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "is_superuser": user.is_superuser
            }

            access_token = self._create_access_token(token_data)
            refresh_token = self._create_refresh_token(token_data)

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
        try:
            token_data = jwt.decode(
                request.refresh_token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )

            access_token = self._create_access_token(token_data)

            return RefreshTokenResponse(
                access_token=access_token,
                expires_in=self.config.access_token_expire_minutes * 60
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

    async def change_password(self, user: User, request: ChangePasswordRequest) -> None:
        """Сменить пароль"""
        # Проверяем текущий пароль
        if not bcrypt.checkpw(request.current_password.encode(), user.hashed_password.encode()):
            raise InvalidCredentialsError()

        # Хешируем новый пароль
        new_hashed_password = bcrypt.hashpw(request.new_password.encode(), bcrypt.gensalt()).decode()
        user.hashed_password = new_hashed_password

        from src.shared.infrastructure.database.session import get_async_session

        async with get_async_session() as session:
            user_repo = UserRepository(session)
            await user_repo.update(user)
            await session.commit()

    async def reset_password(self, request: ResetPasswordRequest) -> None:
        """Запросить сброс пароля"""
        from src.shared.infrastructure.database.session import get_async_session

        async with get_async_session() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_email(request.email)
            if not user:
                return  # Не раскрываем информацию

            # Создаем токен сброса пароля
            reset_token = jwt.encode(
                {
                    "sub": str(user.id),
                    "email": user.email,
                    "type": "password_reset",
                    "exp": datetime.utcnow() + timedelta(hours=self.config.password_reset_token_expire_hours)
                },
                self.config.secret_key,
                algorithm=self.config.algorithm
            )

            # Здесь можно отправить email
            self.logger.info(f"Password reset token for {user.email}: {reset_token}")

    async def reset_password_confirm(self, request: ResetPasswordConfirmRequest) -> None:
        """Подтвердить сброс пароля"""
        try:
            token_data = jwt.decode(
                request.token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )

            if token_data.get("type") != "password_reset":
                raise InvalidTokenError()

            user_id = token_data.get("sub")
            if not user_id:
                raise InvalidTokenError()

            from src.shared.infrastructure.database.session import get_async_session

            async with get_async_session() as session:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_id(int(user_id))
                if not user:
                    raise UserNotFoundError()

                # Хешируем новый пароль
                new_hashed_password = bcrypt.hashpw(request.new_password.encode(), bcrypt.gensalt()).decode()
                user.hashed_password = new_hashed_password
                await user_repo.update(user)
                await session.commit()

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """Выход из системы"""
        # В упрощенной версии просто логируем
        if refresh_token:
            self.logger.info("User logged out")

    async def validate_user_token(self, token: str) -> Optional[User]:
        """Валидировать токен и получить пользователя"""
        try:
            token_data = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )

            user_id = token_data.get("sub")
            if not user_id:
                return None

            from src.shared.infrastructure.database.session import get_async_session

            async with get_async_session() as session:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_id(int(user_id))
                return user

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def _create_access_token(self, data: dict) -> str:
        """Создать access токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)

    def _create_refresh_token(self, data: dict) -> str:
        """Создать refresh токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)