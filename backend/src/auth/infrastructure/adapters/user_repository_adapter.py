"""
Адаптер для репозитория пользователей
"""

from typing import Any, Optional

from ..interfaces import IUserRepository


class UserRepositoryAdapter(IUserRepository):
    """Адаптер для существующего репозитория пользователей"""

    def __init__(self, user_repository: Any):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: int) -> Optional[Any]:
        """Получить пользователя по ID"""
        return await self.user_repository.get_by_id(user_id)

    async def get_by_email(self, email: str) -> Optional[Any]:
        """Получить пользователя по email"""
        return await self.user_repository.get_by_email(email)

    async def create(self, user_data: dict) -> Any:
        """Создать нового пользователя"""
        return await self.user_repository.create(user_data)

    async def update(self, user: Any) -> None:
        """Обновить пользователя"""
        await self.user_repository.update(user)

    async def delete(self, user_id: int) -> None:
        """Удалить пользователя"""
        await self.user_repository.delete(user_id)

    async def exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        return await self.user_repository.exists_by_email(email)