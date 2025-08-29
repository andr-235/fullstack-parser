"""
Базовые интерфейсы репозиториев (DDD Infrastructure Layer)
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from datetime import datetime

from ...domain.base import Entity

TEntity = TypeVar("TEntity", bound=Entity)


class Specification(ABC):
    """Базовый класс для спецификаций (DDD паттерн Specification)"""

    @abstractmethod
    def is_satisfied_by(self, entity: Entity) -> bool:
        """Проверяет, удовлетворяет ли сущность спецификации"""
        pass

    def and_(self, other: "Specification") -> "Specification":
        """Логическое И"""
        return AndSpecification(self, other)

    def or_(self, other: "Specification") -> "Specification":
        """Логическое ИЛИ"""
        return OrSpecification(self, other)

    def not_(self) -> "Specification":
        """Логическое НЕ"""
        return NotSpecification(self)


class AndSpecification(Specification):
    """Спецификация И"""

    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, entity: Entity) -> bool:
        return self.left.is_satisfied_by(
            entity
        ) and self.right.is_satisfied_by(entity)


class OrSpecification(Specification):
    """Спецификация ИЛИ"""

    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, entity: Entity) -> bool:
        return self.left.is_satisfied_by(entity) or self.right.is_satisfied_by(
            entity
        )


class NotSpecification(Specification):
    """Спецификация НЕ"""

    def __init__(self, spec: Specification):
        self.spec = spec

    def is_satisfied_by(self, entity: Entity) -> bool:
        return not self.spec.is_satisfied_by(entity)


class QueryOptions:
    """Опции запроса для репозиториев"""

    def __init__(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: str = "asc",
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None,
    ):
        self.limit = limit
        self.offset = offset
        self.order_by = order_by
        self.order_direction = order_direction
        self.include_deleted = include_deleted
        self.filters = filters or {}


class Repository(ABC, Generic[TEntity]):
    """
    Базовый интерфейс репозитория (DDD Repository паттерн)

    Репозиторий предоставляет коллекцию-подобный интерфейс для работы с агрегатами,
    скрывая детали хранения и извлечения данных.
    """

    @abstractmethod
    async def save(self, entity: TEntity) -> TEntity:
        """Сохранить сущность"""
        pass

    @abstractmethod
    async def save_all(self, entities: List[TEntity]) -> List[TEntity]:
        """Сохранить несколько сущностей"""
        pass

    @abstractmethod
    async def find_by_id(
        self, entity_id: Any, include_deleted: bool = False
    ) -> Optional[TEntity]:
        """Найти сущность по ID"""
        pass

    @abstractmethod
    async def find_all(
        self, options: Optional[QueryOptions] = None
    ) -> List[TEntity]:
        """Найти все сущности"""
        pass

    @abstractmethod
    async def find_by_specification(
        self,
        specification: Specification,
        options: Optional[QueryOptions] = None,
    ) -> List[TEntity]:
        """Найти сущности по спецификации"""
        pass

    @abstractmethod
    async def count(
        self, specification: Optional[Specification] = None
    ) -> int:
        """Подсчитать количество сущностей"""
        pass

    @abstractmethod
    async def exists(self, entity_id: Any) -> bool:
        """Проверить существование сущности"""
        pass

    @abstractmethod
    async def delete(self, entity_id: Any) -> bool:
        """Удалить сущность (soft delete)"""
        pass

    @abstractmethod
    async def delete_permanently(self, entity_id: Any) -> bool:
        """Удалить сущность навсегда (hard delete)"""
        pass

    @abstractmethod
    async def update(self, entity: TEntity) -> TEntity:
        """Обновить сущность"""
        pass


class UnitOfWork(ABC):
    """
    Unit of Work паттерн (DDD)

    Гарантирует атомарность операций и отслеживает изменения в агрегатах.
    """

    @abstractmethod
    async def __aenter__(self):
        """Войти в контекст транзакции"""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выйти из контекста транзакции"""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Подтвердить изменения"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить изменения"""
        pass

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Проверить активность транзакции"""
        pass
