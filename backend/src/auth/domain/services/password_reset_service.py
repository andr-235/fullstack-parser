"""
Сервис сброса паролей
"""

from typing import Dict, Any, Optional

from src.common.logging import get_logger
from src.user.exceptions import UserNotFoundError

from ..interfaces import (
    IUserRepository,
    IPasswordService,
    IJWTService,
    IEventPublisher
)
from ..exceptions import InvalidTokenError


class PasswordResetService:
    """Сервис для управления сбросом паролей"""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        jwt_service: IJWTService,
        event_publisher: IEventPublisher = None
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.event_publisher = event_publisher
        self.logger = get_logger()

    async def initiate_password_reset(self, email: str) -> None:
        """Инициирует процесс сброса пароля"""
        self.logger.info(f"Initiating password reset for email: {email}")

        user = await self.user_repository.get_by_email(email)
        if not user:
            # Не раскрываем информацию о существовании пользователя
            self.logger.info(f"Password reset requested for non-existent email: {email}")
            return

        # Создаем токен сброса пароля
        reset_token = await self.jwt_service.create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "type": "password_reset"
        })

        # Отправляем email
        if self.event_publisher:
            await self.event_publisher.send_email(
                email=user.email,
                subject="Password Reset Request",
                body=f"Your password reset token: {reset_token}"
            )

            # Логируем событие
            await self.event_publisher.publish_event(
                "password_reset_requested", str(user.id), {"email": user.email}
            )

        self.logger.info(f"Password reset initiated for user: {user.id}")

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        """Подтверждает сброс пароля"""
        self.logger.info("Confirming password reset")

        # Валидируем токен
        token_data = await self.jwt_service.validate_token(token)
        if not token_data or token_data.get("type") != "password_reset":
            raise InvalidTokenError()

        user_id = token_data.get("sub")
        if not user_id:
            raise InvalidTokenError()

        # Получаем пользователя
        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise UserNotFoundError()

        # Хешируем новый пароль
        hashed_password = await self.password_service.hash_password(new_password)
        user.hashed_password = hashed_password

        # Обновляем пользователя
        await self.user_repository.update(user)

        # Логируем событие
        if self.event_publisher:
            await self.event_publisher.publish_event(
                "password_reset_completed", str(user.id), {"email": user.email}
            )

        self.logger.info(f"Password reset completed for user: {user.id}")

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Изменяет пароль пользователя"""
        self.logger.info(f"Changing password for user: {user_id}")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        # Проверяем текущий пароль
        is_valid = await self.password_service.verify_password(current_password, user.hashed_password)
        if not is_valid:
            from ..exceptions import InvalidCredentialsError
            raise InvalidCredentialsError()

        # Хешируем новый пароль
        hashed_password = await self.password_service.hash_password(new_password)
        user.hashed_password = hashed_password

        # Обновляем пользователя
        await self.user_repository.update(user)

        # Логируем событие
        if self.event_publisher:
            await self.event_publisher.publish_event(
                "password_changed", str(user.id), {"email": user.email}
            )

        self.logger.info(f"Password changed for user: {user.id}")