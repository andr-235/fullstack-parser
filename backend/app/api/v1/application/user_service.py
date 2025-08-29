"""
UserService - DDD Application Service для управления пользователями

Мигрирован из app/services/user_service.py
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class UserService:
    """
    DDD Application Service для управления пользователями.

    Предоставляет высокоуровневый интерфейс для:
    - Создания и обновления пользователей
    - Аутентификации пользователей
    - Поиска пользователей
    """

    def __init__(self, user_repository=None, cache_service=None):
        """
        Инициализация UserService.

        Args:
            user_repository: Репозиторий пользователей
            cache_service: Сервис кеширования
        """
        self.user_repository = user_repository
        self.cache_service = cache_service

    # =============== МИГРАЦИЯ UserService В DDD ===============

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать нового пользователя (мигрировано из UserService)

        Args:
            user_data: Данные пользователя

        Returns:
            Созданный пользователь
        """
        from ..domain.user import User, UserContent
        from ..infrastructure.events.user_events import (
            UserCreatedEvent,
            create_user_created_event,
        )
        from ..infrastructure.events.domain_event_publisher import (
            publish_domain_event,
        )

        # Создаем контент пользователя
        content = UserContent(
            email=user_data.get("email", ""),
            full_name=user_data.get("full_name", ""),
            is_active=user_data.get("is_active", True),
            is_superuser=user_data.get("is_superuser", False),
        )

        # Создаем доменную сущность
        user = User(
            id=None,  # Будет присвоен при сохранении
            content=content,
            hashed_password=self._hash_password(user_data.get("password", "")),
        )

        # Валидируем бизнес-правила
        user.validate_business_rules()

        # Сохраняем через репозиторий
        await self.user_repository.save(user)

        # Публикуем Domain Event
        user_created_event = create_user_created_event(
            user_id=user.id,
            email=user.content.email,
            full_name=user.content.full_name,
            is_superuser=user.content.is_superuser,
        )
        await publish_domain_event(user_created_event)

        # Инвалидируем кеш
        if self.cache_service:
            await self.cache_service.invalidate_user_cache(user.content.email)

        return await self.get_user_by_id(user.id)

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить пользователя по ID (мигрировано из UserService)

        Args:
            user_id: ID пользователя

        Returns:
            Информация о пользователе или None
        """
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            return None

        return {
            "id": user.id,
            "email": user.content.email,
            "full_name": user.content.full_name,
            "is_active": user.content.is_active,
            "is_superuser": user.content.is_superuser,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Получить пользователя по email (мигрировано из UserService)

        Args:
            email: Email пользователя

        Returns:
            Информация о пользователе или None
        """
        # Получаем всех пользователей и ищем по email
        all_users = await self.user_repository.find_all()
        user = next(
            (u for u in all_users if u.content.email.lower() == email.lower()),
            None,
        )

        if not user:
            return None

        return await self.get_user_by_id(user.id)

    async def update_user(
        self, user_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить пользователя (мигрировано из UserService)

        Args:
            user_id: ID пользователя
            update_data: Данные для обновления

        Returns:
            Обновленный пользователь или None
        """
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            return None

        # Обновляем поля
        for field, value in update_data.items():
            if field == "email":
                user.content.email = value
            elif field == "full_name":
                user.content.full_name = value
            elif field == "is_active":
                user.content.is_active = value
            elif field == "is_superuser":
                user.content.is_superuser = value
            elif field == "password":
                user.hashed_password = self._hash_password(value)

        # Валидируем бизнес-правила после обновления
        user.validate_business_rules()

        # Сохраняем изменения
        await self.user_repository.save(user)

        # Публикуем Domain Event об обновлении
        from ..infrastructure.events.user_events import (
            UserUpdatedEvent,
            create_user_updated_event,
        )
        from ..infrastructure.events.domain_event_publisher import (
            publish_domain_event,
        )

        updated_fields = list(update_data.keys())
        user_updated_event = create_user_updated_event(
            user_id=user_id,
            updated_fields=updated_fields,
            updated_by=update_data.get("updated_by"),
        )
        await publish_domain_event(user_updated_event)

        # Инвалидируем кеш
        if self.cache_service:
            await self.cache_service.invalidate_user_cache(user.content.email)

        return await self.get_user_by_id(user.id)

    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        Удалить пользователя (мигрировано из UserService)

        Args:
            user_id: ID пользователя

        Returns:
            Результат операции
        """
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            return {"deleted": False, "reason": "User not found"}

        user_email = user.content.email

        # Удаляем через репозиторий
        await self.user_repository.delete(user_id)

        # Публикуем Domain Event об удалении
        from ..infrastructure.events.user_events import (
            UserDeletedEvent,
            create_user_deleted_event,
        )
        from ..infrastructure.events.domain_event_publisher import (
            publish_domain_event,
        )

        user_deleted_event = create_user_deleted_event(
            user_id=user_id,
            email=user_email,
            deleted_by=None,  # TODO: передать реального пользователя
            reason="api_request",
        )
        await publish_domain_event(user_deleted_event)

        # Инвалидируем кеш
        if self.cache_service:
            await self.cache_service.invalidate_user_cache(user_email)

        return {
            "deleted": True,
            "user_id": user_id,
            "user_email": user_email,
            "message": f"User {user_email} deleted successfully",
        }

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Аутентифицировать пользователя (мигрировано из UserService)

        Args:
            email: Email пользователя
            password: Пароль

        Returns:
            Информация о пользователе при успешной аутентификации или None
        """
        user_data = await self.get_user_by_email(email)
        if not user_data:
            return None

        # Получаем полную информацию о пользователе для проверки пароля
        user = await self.user_repository.find_by_id(user_data["id"])
        if not user:
            return None

        # Проверяем пароль
        if not self._verify_password(password, user.hashed_password):
            return None

        # Обновляем время последнего входа
        user.last_login_at = datetime.utcnow()
        await self.user_repository.save(user)

        # Публикуем Domain Event об аутентификации
        from ..infrastructure.events.user_events import (
            UserAuthenticatedEvent,
            create_user_authenticated_event,
        )
        from ..infrastructure.events.domain_event_publisher import (
            publish_domain_event,
        )

        user_authenticated_event = create_user_authenticated_event(
            user_id=user.id,
            email=email,
            login_method="password",
        )
        await publish_domain_event(user_authenticated_event)

        return user_data

    async def get_users_paginated(
        self, active_only: bool = True, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Получить пользователей с пагинацией (мигрировано из UserService)

        Args:
            active_only: Только активные пользователи
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Пагинированный результат
        """
        # Получаем всех пользователей
        all_users = await self.user_repository.find_all()

        # Применяем фильтры
        if active_only:
            all_users = [u for u in all_users if u.content.is_active]

        # Пагинация
        total = len(all_users)
        paginated_users = all_users[offset : offset + limit]

        # Преобразуем в response формат
        users_response = []
        for user in paginated_users:
            users_response.append(
                {
                    "id": user.id,
                    "email": user.content.email,
                    "full_name": user.content.full_name,
                    "is_active": user.content.is_active,
                    "is_superuser": user.content.is_superuser,
                    "created_at": user.created_at.isoformat(),
                    "last_login_at": (
                        user.last_login_at.isoformat()
                        if user.last_login_at
                        else None
                    ),
                }
            )

        return {
            "users": users_response,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": len(paginated_users) == limit,
            "has_prev": offset > 0,
        }

    def _hash_password(self, password: str) -> str:
        """
        Хешировать пароль

        Args:
            password: Пароль в открытом виде

        Returns:
            Хешированный пароль
        """
        # Импортируем здесь чтобы избежать циклических зависимостей
        from app.core.hashing import get_password_hash

        return get_password_hash(password)

    def _verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Проверить пароль

        Args:
            plain_password: Пароль в открытом виде
            hashed_password: Хешированный пароль

        Returns:
            True если пароль верный
        """
        # Импортируем здесь чтобы избежать циклических зависимостей
        from app.core.hashing import verify_password

        return verify_password(plain_password, hashed_password)
