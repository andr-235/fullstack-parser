"""
Провайдеры зависимостей для FastAPI

Содержит функции для внедрения зависимостей в FastAPI эндпоинты
"""

from functools import lru_cache
from fastapi import Depends

from .container import get_container
from auth.application.services import AuthService, UserService
from auth.application.use_cases import (
    LoginUseCase,
    RefreshTokenUseCase,
    ChangePasswordUseCase,
    ResetPasswordUseCase,
    LogoutUseCase,
    ValidateTokenUseCase,
    CreateUserUseCase,
    GetUserUseCase,
    GetCurrentUserUseCase,
    UpdateUserUseCase,
    GetUsersListUseCase,
    GetUserStatsUseCase,
)


@lru_cache()
def get_auth_service() -> AuthService:
    """Получить сервис аутентификации"""
    container = get_container()
    return container.get_auth_service()


@lru_cache()
def get_user_service() -> UserService:
    """Получить сервис пользователей"""
    container = get_container()
    return container.get_user_service()


@lru_cache()
def get_login_use_case() -> LoginUseCase:
    """Получить use case для входа"""
    container = get_container()
    return container.get_login_use_case()


@lru_cache()
def get_refresh_token_use_case() -> RefreshTokenUseCase:
    """Получить use case для обновления токена"""
    container = get_container()
    return container.get_refresh_token_use_case()


@lru_cache()
def get_change_password_use_case() -> ChangePasswordUseCase:
    """Получить use case для смены пароля"""
    container = get_container()
    return container.get_change_password_use_case()


@lru_cache()
def get_reset_password_use_case() -> ResetPasswordUseCase:
    """Получить use case для сброса пароля"""
    container = get_container()
    return container.get_reset_password_use_case()


@lru_cache()
def get_logout_use_case() -> LogoutUseCase:
    """Получить use case для выхода"""
    container = get_container()
    return container.get_logout_use_case()


@lru_cache()
def get_validate_token_use_case() -> ValidateTokenUseCase:
    """Получить use case для валидации токена"""
    container = get_container()
    return container.get_validate_token_use_case()


@lru_cache()
def get_create_user_use_case() -> CreateUserUseCase:
    """Получить use case для создания пользователя"""
    container = get_container()
    return container.get_create_user_use_case()


@lru_cache()
def get_get_user_use_case() -> GetUserUseCase:
    """Получить use case для получения пользователя"""
    container = get_container()
    return container.get_get_user_use_case()


@lru_cache()
def get_get_current_user_use_case() -> GetCurrentUserUseCase:
    """Получить use case для получения текущего пользователя"""
    container = get_container()
    return container.get_get_current_user_use_case()


@lru_cache()
def get_update_user_use_case() -> UpdateUserUseCase:
    """Получить use case для обновления пользователя"""
    container = get_container()
    return container.get_update_user_use_case()


@lru_cache()
def get_get_users_list_use_case() -> GetUsersListUseCase:
    """Получить use case для получения списка пользователей"""
    container = get_container()
    return container.get_get_users_list_use_case()


@lru_cache()
def get_get_user_stats_use_case() -> GetUserStatsUseCase:
    """Получить use case для получения статистики пользователей"""
    container = get_container()
    return container.get_get_user_stats_use_case()


# FastAPI зависимости для использования в Depends()
def auth_service_dependency() -> AuthService:
    """Зависимость для получения сервиса аутентификации"""
    return get_auth_service()


def user_service_dependency() -> UserService:
    """Зависимость для получения сервиса пользователей"""
    return get_user_service()


def login_use_case_dependency() -> LoginUseCase:
    """Зависимость для получения use case входа"""
    return get_login_use_case()


def refresh_token_use_case_dependency() -> RefreshTokenUseCase:
    """Зависимость для получения use case обновления токена"""
    return get_refresh_token_use_case()


def change_password_use_case_dependency() -> ChangePasswordUseCase:
    """Зависимость для получения use case смены пароля"""
    return get_change_password_use_case()


def reset_password_use_case_dependency() -> ResetPasswordUseCase:
    """Зависимость для получения use case сброса пароля"""
    return get_reset_password_use_case()


def logout_use_case_dependency() -> LogoutUseCase:
    """Зависимость для получения use case выхода"""
    return get_logout_use_case()


def create_user_use_case_dependency() -> CreateUserUseCase:
    """Зависимость для получения use case создания пользователя"""
    return get_create_user_use_case()


def get_user_use_case_dependency() -> GetUserUseCase:
    """Зависимость для получения use case получения пользователя"""
    return get_get_user_use_case()


def get_current_user_use_case_dependency() -> GetCurrentUserUseCase:
    """Зависимость для получения use case получения текущего пользователя"""
    return get_get_current_user_use_case()


def update_user_use_case_dependency() -> UpdateUserUseCase:
    """Зависимость для получения use case обновления пользователя"""
    return get_update_user_use_case()


def get_users_list_use_case_dependency() -> GetUsersListUseCase:
    """Зависимость для получения use case списка пользователей"""
    return get_get_users_list_use_case()


def get_user_stats_use_case_dependency() -> GetUserStatsUseCase:
    """Зависимость для получения use case статистики пользователей"""
    return get_get_user_stats_use_case()
