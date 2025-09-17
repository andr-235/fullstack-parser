"""
Рефакторенный сервис аутентификации
"""

from typing import Dict, Any, Optional

from src.common.logging import get_logger
from src.user.models import User

from .user_registration_service import UserRegistrationService
from .user_authentication_service import UserAuthenticationService
from .password_reset_service import PasswordResetService
from .token_management_service import TokenManagementService


class AuthServiceRefactored:
    """Рефакторенный сервис аутентификации с разделением ответственности"""

    def __init__(
        self,
        user_registration_service: UserRegistrationService,
        user_authentication_service: UserAuthenticationService,
        password_reset_service: PasswordResetService,
        token_management_service: TokenManagementService
    ):
        self.user_registration_service = user_registration_service
        self.user_authentication_service = user_authentication_service
        self.password_reset_service = password_reset_service
        self.token_management_service = token_management_service
        self.logger = get_logger()

    async def register(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        return await self.user_registration_service.register_user(email, password, full_name)

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Вход в систему"""
        return await self.user_authentication_service.authenticate_user(email, password)

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Обновить access токен"""
        return await self.token_management_service.refresh_access_token(refresh_token)

    async def change_password(self, user: User, current_password: str, new_password: str) -> None:
        """Сменить пароль"""
        await self.password_reset_service.change_password(user.id, current_password, new_password)

    async def reset_password(self, email: str) -> None:
        """Запросить сброс пароля"""
        await self.password_reset_service.initiate_password_reset(email)

    async def reset_password_confirm(self, token: str, new_password: str) -> None:
        """Подтвердить сброс пароля"""
        await self.password_reset_service.confirm_password_reset(token, new_password)

    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """Выход из системы"""
        await self.token_management_service.logout(refresh_token)

    async def validate_user_token(self, token: str) -> Optional[User]:
        """Валидировать токен и получить пользователя"""
        # Для обратной совместимости возвращаем User объект
        # В будущем можно изменить на Dict
        user_data = await self.token_management_service.validate_token_and_get_user(token)
        if not user_data:
            return None

        # Создаем User объект из данных
        from datetime import datetime
        return User(
            id=user_data["id"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password="",  # Не возвращаем пароль
            status=user_data["status"],
            is_superuser=False,
            last_login=user_data.get("last_login"),
            login_attempts=user_data.get("login_attempts", 0),
            locked_until=user_data.get("locked_until"),
            email_verified=user_data.get("email_verified", False),
            created_at=user_data.get("created_at") or datetime.utcnow(),
            updated_at=user_data.get("updated_at") or datetime.utcnow()
        )