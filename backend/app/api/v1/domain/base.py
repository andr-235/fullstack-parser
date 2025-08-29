"""
Базовые классы для Domain Layer (DDD)
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


class Entity:
    """Базовый класс для всех сущностей домена"""

    def __init__(self, id: Any = None):
        self._id = id or str(uuid4())
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._version = 1

    @property
    def id(self) -> Any:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def version(self) -> int:
        return self._version

    def update(self) -> None:
        """Обновить timestamp и версию"""
        self._updated_at = datetime.utcnow()
        self._version += 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class ValueObject:
    """Базовый класс для Value Objects"""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))


class DomainService(ABC):
    """Базовый класс для Domain Services"""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Основная бизнес-логика сервиса"""
        pass


class Repository(ABC):
    """Базовый интерфейс для репозиториев"""

    @abstractmethod
    async def save(self, entity: Entity) -> None:
        """Сохранить сущность"""
        pass

    @abstractmethod
    async def find_by_id(self, id: Any) -> Optional[Entity]:
        """Найти сущность по ID"""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Удалить сущность"""
        pass
