"""
Фабрика сервисов пользователей
"""

from typing import Optional

from ...infrastructure.repositories import SQLAlchemyUserRepository
from ..interfaces import IUserRepository, IUserService, IUserValidator, IPasswordService
from .password_service import PasswordService
from .user_service import UserService
from .user_validator import UserValidator


class UserServiceFactory:
    """Фабрика для создания сервисов пользователей"""

    def __init__(self, db_session):
        """Инициализация фабрики

        Args:
            db_session: Сессия базы данных
        """
        self.db_session = db_session
        self._repository: Optional[IUserRepository] = None
        self._password_service: Optional[IPasswordService] = None
        self._validator: Optional[IUserValidator] = None
        self._user_service: Optional[IUserService] = None

    @property
    def repository(self) -> IUserRepository:
        """Получает репозиторий пользователей"""
        if self._repository is None:
            self._repository = SQLAlchemyUserRepository(self.db_session)
        return self._repository

    @property
    def password_service(self) -> IPasswordService:
        """Получает сервис паролей"""
        if self._password_service is None:
            self._password_service = PasswordService()
        return self._password_service

    @property
    def validator(self) -> IUserValidator:
        """Получает валидатор пользователей"""
        if self._validator is None:
            self._validator = UserValidator()
        return self._validator

    @property
    def user_service(self) -> IUserService:
        """Получает основной сервис пользователей"""
        if self._user_service is None:
            self._user_service = UserService(
                repository=self.repository,
                password_service=self.password_service,
                validator=self.validator
            )
        return self._user_service

    def create_user_service(self) -> IUserService:
        """Создает новый экземпляр сервиса пользователей"""
        return UserService(
            repository=SQLAlchemyUserRepository(self.db_session),
            password_service=PasswordService(),
            validator=UserValidator()
        )

    def create_password_service(self) -> IPasswordService:
        """Создает новый экземпляр сервиса паролей"""
        return PasswordService()

    def create_validator(self) -> IUserValidator:
        """Создает новый экземпляр валидатора"""
        return UserValidator()

    def create_repository(self) -> IUserRepository:
        """Создает новый экземпляр репозитория"""
        return SQLAlchemyUserRepository(self.db_session)