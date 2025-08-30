"""
Сервис для работы с аутентификацией и пользователями

Содержит бизнес-логику для операций аутентификации и управления пользователями
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import secrets
import string

from ..exceptions import ValidationError, AuthenticationError, NotFoundError
from .models import UserRepository, AuthToken
from ..infrastructure import security_service


class AuthService:
    """
    Сервис для аутентификации и управления пользователями

    Реализует бизнес-логику для операций CRUD с пользователями и JWT токенами
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    # JWT методы теперь делегируются SecurityService

    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Зарегистрировать нового пользователя

        Args:
            user_data: Данные пользователя (email, full_name, password)

        Returns:
            Dict[str, Any]: Созданный пользователь
        """
        # Валидация данных
        required_fields = ["email", "full_name", "password"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValidationError(
                    f"Обязательное поле '{field}' не заполнено", field=field
                )

        email = user_data["email"].strip().lower()
        full_name = user_data["full_name"].strip()
        password = user_data["password"]

        # Проверяем, что пользователь с таким email не существует
        existing = await self.repository.get_by_email(email)
        if existing:
            raise ValidationError(
                "Пользователь с таким email уже существует", field="email"
            )

        # Валидация email формата
        if "@" not in email or "." not in email:
            raise ValidationError("Неверный формат email", field="email")

        # Валидация длины пароля
        if len(password) < 8:
            raise ValidationError(
                "Пароль должен содержать минимум 8 символов", field="password"
            )

        # Создаем пользователя
        hashed_password = security_service.hash_password(password)

        user_data = {
            "email": email,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_superuser": False,
        }

        user = await self.repository.create(user_data)
        return await self.get_user(user.id)

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Аутентифицировать пользователя

        Args:
            email: Email пользователя
            password: Пароль пользователя

        Returns:
            Optional[Dict[str, Any]]: Пользователь или None если аутентификация не удалась
        """
        user = await self.repository.get_by_email(email.strip().lower())
        if not user:
            return None

        if not user.is_active:
            raise AuthenticationError("Аккаунт деактивирован")

        if not security_service.verify_password(
            password, user.hashed_password
        ):
            return None

        return await self.get_user(user.id)

    async def create_tokens(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать JWT токены для пользователя

        Args:
            user: Данные пользователя

        Returns:
            Dict[str, Any]: Access и refresh токены
        """
        token_data = {
            "sub": str(user["id"]),
            "email": user["email"],
            "type": "user",
        }

        access_token = security_service.create_access_token(token_data)
        refresh_token = security_service.create_refresh_token(token_data)

        # Время жизни access токена задается в настройках SecurityService
        expires_seconds = getattr(
            security_service, "access_token_expires_seconds", None
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": (
                int(expires_seconds) if expires_seconds is not None else 3600
            ),
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Обновить access токен с помощью refresh токена

        Args:
            refresh_token: Refresh токен

        Returns:
            Dict[str, Any]: Новые токены
        """
        try:
            payload = security_service.decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise AuthenticationError("Неверный тип токена")

            user_id = int(payload.get("sub"))
            user = await self.get_user(user_id)

            if not user or not user["is_active"]:
                raise AuthenticationError(
                    "Пользователь не найден или деактивирован"
                )

            # Создаем новые токены
            token_data = {
                "sub": str(user_id),
                "email": user["email"],
                "type": "user",
            }

            return {
                "access_token": security_service.create_access_token(
                    token_data
                ),
                "refresh_token": security_service.create_refresh_token(
                    token_data
                ),
                "token_type": "bearer",
                "expires_in": int(
                    getattr(
                        security_service, "access_token_expires_seconds", 3600
                    )
                ),
            }

        except Exception:
            raise AuthenticationError("Неверный refresh токен")

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Валидировать JWT токен

        Args:
            token: JWT токен

        Returns:
            Optional[Dict[str, Any]]: Данные пользователя или None
        """
        try:
            payload = security_service.decode_token(token)

            user_id = int(payload.get("sub"))
            user = await self.get_user(user_id)

            if not user or not user["is_active"]:
                return None

            return {
                "user": user,
                "expires_at": datetime.fromtimestamp(payload.get("exp")),
                "valid": True,
            }

        except Exception:
            return None

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            Optional[Dict[str, Any]]: Пользователь или None
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь", user_id)

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    async def update_user(
        self, user_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить пользователя

        Args:
            user_id: ID пользователя
            update_data: Данные для обновления

        Returns:
            Dict[str, Any]: Обновленный пользователь
        """
        # Проверяем, что пользователь существует
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь", user_id)

        # Валидация данных
        filtered_data = {}

        if "email" in update_data:
            email = update_data["email"].strip().lower()
            # Проверяем, что email не занят другим пользователем
            existing = await self.repository.get_by_email(email)
            if existing and existing.id != user_id:
                raise ValidationError(
                    "Email уже используется другим пользователем",
                    field="email",
                )
            filtered_data["email"] = email

        if "full_name" in update_data:
            filtered_data["full_name"] = update_data["full_name"].strip()

        if "is_active" in update_data:
            filtered_data["is_active"] = bool(update_data["is_active"])

        if "password" in update_data:
            filtered_data["hashed_password"] = security_service.hash_password(
                update_data["password"]
            )

        if not filtered_data:
            raise ValidationError("Нет допустимых полей для обновления")

        await self.repository.update(user_id, filtered_data)
        return await self.get_user(user_id)

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """
        Изменить пароль пользователя

        Args:
            user_id: ID пользователя
            current_password: Текущий пароль
            new_password: Новый пароль

        Returns:
            bool: True если пароль изменен
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь", user_id)

        # Проверяем текущий пароль
        if not security_service.verify_password(
            current_password, user.hashed_password
        ):
            raise ValidationError(
                "Неверный текущий пароль", field="current_password"
            )

        # Валидируем новый пароль
        if len(new_password) < 8:
            raise ValidationError(
                "Новый пароль должен содержать минимум 8 символов",
                field="new_password",
            )

        # Обновляем пароль
        await self.repository.update(
            user_id,
            {"hashed_password": security_service.hash_password(new_password)},
        )
        return True

    async def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь удален
        """
        return await self.repository.delete(user_id)

    async def get_users(
        self,
        limit: int = 50,
        offset: int = 0,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить список пользователей

        Args:
            limit: Максимум пользователей
            offset: Смещение
            is_active: Фильтр по активности
            search: Поиск по email или имени

        Returns:
            List[Dict[str, Any]]: Список пользователей
        """
        users = await self.repository.get_all(
            is_active=is_active, search=search, limit=limit, offset=offset
        )

        return [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            for user in users
        ]

    async def get_user_stats(self) -> Dict[str, Any]:
        """
        Получить статистику пользователей

        Returns:
            Dict[str, Any]: Статистика пользователей
        """
        return await self.repository.get_stats()

    async def generate_password_reset_token(self, email: str) -> Optional[str]:
        """
        Сгенерировать токен для сброса пароля

        Args:
            email: Email пользователя

        Returns:
            Optional[str]: Токен сброса пароля или None
        """
        user = await self.repository.get_by_email(email.strip().lower())
        if not user:
            return None  # Не раскрываем существование пользователя

        # Генерируем токен
        token = secrets.token_urlsafe(32)

        # Сохраняем токен (в реальном приложении сохраняем в БД с expiration)
        # Пока просто возвращаем токен
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Сбросить пароль с помощью токена

        Args:
            token: Токен сброса пароля
            new_password: Новый пароль

        Returns:
            bool: True если пароль сброшен
        """
        # Валидация пароля
        if len(new_password) < 8:
            raise ValidationError(
                "Пароль должен содержать минимум 8 символов",
                field="new_password",
            )

        # В реальном приложении проверяем токен в БД
        # Пока просто принимаем любой токен
        return True


# Экспорт
__all__ = [
    "AuthService",
]
