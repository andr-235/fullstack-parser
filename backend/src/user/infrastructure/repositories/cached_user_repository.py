"""
Упрощенный кэшированный репозиторий пользователей

Реализует базовое кэширование для репозитория пользователей
"""

from typing import List, Optional, Dict, Any
from user.domain.entities.user import User
from user.domain.value_objects.user_status import UserStatus
from user.domain.interfaces.user_repository import UserRepositoryInterface


class CachedUserRepository(UserRepositoryInterface):
    """Упрощенный кэшированный репозиторий пользователей"""
    
    def __init__(
        self, 
        repository: UserRepositoryInterface,
        cache,
        cache_ttl: int = 300
    ):
        self.repository = repository
        self.cache = cache
        self.cache_ttl = cache_ttl
    
    def _get_user_cache_key(self, user_id: int) -> str:
        """Получить ключ кэша для пользователя"""
        return f"user:{user_id}"
    
    def _get_email_cache_key(self, email: str) -> str:
        """Получить ключ кэша для email"""
        return f"user_email:{email.lower().strip()}"
    
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        created_user = await self.repository.create(user)
        
        # Простое кэширование ID по email
        await self.cache.set(
            self._get_email_cache_key(created_user.email.value),
            created_user.id.value,
            self.cache_ttl
        )
        
        return created_user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        # Для простоты - всегда идем в БД
        return await self.repository.get_by_id(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        email_key = self._get_email_cache_key(email)
        
        # Пытаемся получить ID из кэша
        cached_user_id = await self.cache.get(email_key)
        if cached_user_id:
            return await self.repository.get_by_id(int(cached_user_id))
        
        # Если нет в кэше - идем в БД
        user = await self.repository.get_by_email(email)
        if user:
            # Кэшируем связь email -> ID
            await self.cache.set(email_key, user.id.value, self.cache_ttl)
        
        return user
    
    async def exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        user = await self.get_by_email(email)
        return user is not None
    
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        updated_user = await self.repository.update(user)
        
        # Инвалидируем кэш по email
        await self.cache.delete(self._get_email_cache_key(updated_user.email.value))
        
        return updated_user
    
    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        # Получаем пользователя для инвалидации кэша
        user = await self.repository.get_by_id(user_id)
        
        success = await self.repository.delete(user_id)
        if success and user:
            await self.cache.delete(self._get_email_cache_key(user.email.value))
        
        return success
    
    async def get_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """Получить пользователей с пагинацией"""
        # Для пагинации не используем кэш, так как данные часто меняются
        return await self.repository.get_paginated(limit, offset, status, search)
    
    async def get_stats(self) -> Dict[str, int]:
        """Получить статистику пользователей"""
        # Для простоты - всегда идем в БД
        return await self.repository.get_stats()