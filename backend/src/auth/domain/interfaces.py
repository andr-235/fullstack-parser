"""
Интерфейсы доменного слоя аутентификации
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

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


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[Any]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Any]:
        """Получить пользователя по email"""
        pass
    
    @abstractmethod
    async def create(self, user_data: Dict[str, Any]) -> Any:
        """Создать пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user: Any) -> Any:
        """Обновить пользователя"""
        pass


class ICacheService(ABC):
    """Интерфейс сервиса кэширования"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кэш"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удалить значение из кэша"""
        pass


class IEventService(ABC):
    """Интерфейс сервиса событий"""
    
    @abstractmethod
    async def log_security_event(
        self, 
        event_type: str, 
        user_id: str, 
        metadata: Dict[str, Any]
    ) -> None:
        """Логировать событие безопасности"""
        pass
    
    @abstractmethod
    async def send_password_reset_email(self, email: str, token: str) -> None:
        """Отправить email для сброса пароля"""
        pass


class IUnitOfWork(ABC):
    """Интерфейс Unit of Work"""
    
    @abstractmethod
    async def __aenter__(self):
        """Вход в контекст"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Подтвердить транзакцию"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Откатить транзакцию"""
        pass
    
    @property
    @abstractmethod
    def users(self) -> IUserRepository:
        """Получить репозиторий пользователей"""
        pass


class IAuthenticationService(ABC):
    """Интерфейс сервиса аутентификации"""
    
    @abstractmethod
    async def register(self, request: RegisterRequest) -> RegisterResponse:
        """Регистрация пользователя"""
        pass
    
    @abstractmethod
    async def login(self, request: LoginRequest) -> LoginResponse:
        """Вход в систему"""
        pass
    
    @abstractmethod
    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """Выход из системы"""
        pass


class IAuthorizationService(ABC):
    """Интерфейс сервиса авторизации"""
    
    @abstractmethod
    async def validate_user_token(self, token: str) -> Optional[Any]:
        """Валидировать токен пользователя"""
        pass
    
    @abstractmethod
    async def get_current_user(self, token: str) -> Optional[Any]:
        """Получить текущего пользователя"""
        pass


class ITokenService(ABC):
    """Интерфейс сервиса токенов"""
    
    @abstractmethod
    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Создать access токен"""
        pass
    
    @abstractmethod
    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Создать refresh токен"""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидировать токен"""
        pass
    
    @abstractmethod
    async def refresh_token(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        """Обновить токен"""
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> None:
        """Отозвать токен"""
        pass


class IPasswordService(ABC):
    """Интерфейс сервиса паролей"""
    
    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Захешировать пароль"""
        pass
    
    @abstractmethod
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        pass
    
    @abstractmethod
    async def change_password(
        self, 
        user: Any, 
        request: ChangePasswordRequest
    ) -> None:
        """Сменить пароль"""
        pass


class IUserManagementService(ABC):
    """Интерфейс сервиса управления пользователями"""
    
    @abstractmethod
    async def reset_password(self, request: ResetPasswordRequest) -> None:
        """Запросить сброс пароля"""
        pass
    
    @abstractmethod
    async def reset_password_confirm(
        self, 
        request: ResetPasswordConfirmRequest
    ) -> None:
        """Подтвердить сброс пароля"""
        pass
