"""
DI контейнер для модуля User

Содержит конфигурацию и создание всех зависимостей
"""

from typing import Optional
from functools import lru_cache

from user.domain.interfaces.user_repository import UserRepositoryInterface
from auth.domain.interfaces.password_service import PasswordServiceInterface
from user.application.services import UserService
from user.application.use_cases import (
    CreateUserUseCase,
    GetUserUseCase,
    UpdateUserUseCase,
    GetUsersListUseCase,
    GetUserStatsUseCase,
)
from shared.infrastructure.logging import get_logger


class UserContainer:
    """DI контейнер для модуля User"""
    
    def __init__(
        self,
        user_repository: Optional[UserRepositoryInterface] = None,
        password_service: Optional[PasswordServiceInterface] = None
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._logger = get_logger()
        
        # Кэш для сервисов
        self._user_service: Optional[UserService] = None
        
        # Кэш для use cases
        self._create_user_use_case: Optional[CreateUserUseCase] = None
        self._get_user_use_case: Optional[GetUserUseCase] = None
        self._update_user_use_case: Optional[UpdateUserUseCase] = None
        self._get_users_list_use_case: Optional[GetUsersListUseCase] = None
        self._get_user_stats_use_case: Optional[GetUserStatsUseCase] = None
    
    def set_user_repository(self, repository: UserRepositoryInterface) -> None:
        """Установить репозиторий пользователей"""
        self._user_repository = repository
        self._clear_cache()
    
    def set_password_service(self, service: PasswordServiceInterface) -> None:
        """Установить сервис паролей"""
        self._password_service = service
        self._clear_cache()
    
    def _clear_cache(self) -> None:
        """Очистить кэш сервисов и use cases"""
        self._user_service = None
        self._create_user_use_case = None
        self._get_user_use_case = None
        self._update_user_use_case = None
        self._get_users_list_use_case = None
        self._get_user_stats_use_case = None
    
    def get_user_service(self) -> UserService:
        """Получить сервис пользователей"""
        if self._user_service is None:
            if self._user_repository is None:
                raise ValueError("User repository not set")
            if self._password_service is None:
                raise ValueError("Password service not set")
            
            self._user_service = UserService(
                user_repository=self._user_repository,
                password_service=self._password_service
            )
        
        return self._user_service
    
    def get_create_user_use_case(self) -> CreateUserUseCase:
        """Получить use case создания пользователя"""
        if self._create_user_use_case is None:
            self._create_user_use_case = CreateUserUseCase(
                user_service=self.get_user_service()
            )
        return self._create_user_use_case
    
    def get_get_user_use_case(self) -> GetUserUseCase:
        """Получить use case получения пользователя"""
        if self._get_user_use_case is None:
            self._get_user_use_case = GetUserUseCase(
                user_service=self.get_user_service()
            )
        return self._get_user_use_case
    
    def get_update_user_use_case(self) -> UpdateUserUseCase:
        """Получить use case обновления пользователя"""
        if self._update_user_use_case is None:
            self._update_user_use_case = UpdateUserUseCase(
                user_service=self.get_user_service()
            )
        return self._update_user_use_case
    
    def get_get_users_list_use_case(self) -> GetUsersListUseCase:
        """Получить use case получения списка пользователей"""
        if self._get_users_list_use_case is None:
            self._get_users_list_use_case = GetUsersListUseCase(
                user_service=self.get_user_service()
            )
        return self._get_users_list_use_case
    
    def get_get_user_stats_use_case(self) -> GetUserStatsUseCase:
        """Получить use case получения статистики пользователей"""
        if self._get_user_stats_use_case is None:
            self._get_user_stats_use_case = GetUserStatsUseCase(
                user_service=self.get_user_service()
            )
        return self._get_user_stats_use_case


# Глобальный экземпляр контейнера
_container: Optional[UserContainer] = None


def get_container() -> UserContainer:
    """Получить глобальный экземпляр контейнера"""
    global _container
    if _container is None:
        _container = UserContainer()
    return _container


def set_container(container: UserContainer) -> None:
    """Установить глобальный экземпляр контейнера"""
    global _container
    _container = container


# Функции для получения зависимостей
def get_user_service() -> UserService:
    """Получить сервис пользователей"""
    return get_container().get_user_service()


def get_create_user_use_case() -> CreateUserUseCase:
    """Получить use case создания пользователя"""
    return get_container().get_create_user_use_case()


def get_get_user_use_case() -> GetUserUseCase:
    """Получить use case получения пользователя"""
    return get_container().get_get_user_use_case()


def get_update_user_use_case() -> UpdateUserUseCase:
    """Получить use case обновления пользователя"""
    return get_container().get_update_user_use_case()


def get_get_users_list_use_case() -> GetUsersListUseCase:
    """Получить use case получения списка пользователей"""
    return get_container().get_get_users_list_use_case()


def get_get_user_stats_use_case() -> GetUserStatsUseCase:
    """Получить use case получения статистики пользователей"""
    return get_container().get_get_user_stats_use_case()