"""
Базовые классы для Application Layer (DDD)
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Generic
from ..domain.base import Entity, Repository

TEntity = TypeVar("TEntity", bound=Entity)


class ApplicationService(ABC):
    """Базовый класс для Application Services"""

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Основная логика сервиса"""
        pass


class CommandHandler(ABC):
    """Базовый класс для обработчиков команд"""

    def __init__(self, repository):
        self.repository = repository

    @abstractmethod
    async def handle(self, command: Any) -> Any:
        """Обработать команду"""
        pass


class QueryHandler(ABC):
    """Базовый класс для обработчиков запросов"""

    def __init__(self, repository):
        self.repository = repository

    @abstractmethod
    async def handle(self, query: Any) -> Any:
        """Обработать запрос"""
        pass


class UseCase(ABC):
    """Базовый класс для Use Cases (случаев использования)"""

    @abstractmethod
    async def execute(self, request: Any) -> Any:
        """Выполнить use case"""
        pass
