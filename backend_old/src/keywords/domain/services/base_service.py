"""
Базовый сервис для унификации работы с сервисами

Предоставляет абстрактный базовый класс с общими методами CRUD
и декораторами обработки ошибок для устранения дублирования кода
бизнес-логики в сервисах.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Dict, Any, Type

from src.keywords.shared.error_handlers import handle_service_errors
from src.keywords.shared.constants import DEFAULT_LIMIT

# Типы для обобщений
T = TypeVar("T")  # Тип доменной сущности
R = TypeVar("R")  # Тип репозитория
C = TypeVar("C")  # Тип данных для создания
U = TypeVar("U")  # Тип данных для обновления

# Настройка логгера
logger = logging.getLogger(__name__)


class BaseService(ABC, Generic[T, R, C, U]):
    """
    Абстрактный базовый сервис с общими методами CRUD.

    Предоставляет унифицированный интерфейс для работы с сервисами,
    устраняя дублирование кода и обеспечивая согласованность операций.

    Attributes:
        repository: Репозиторий для работы с данными
    """

    def __init__(self, repository: R):
        """
        Инициализация базового сервиса.

        Args:
            repository: Репозиторий для работы с данными
        """
        self.repository = repository

    @abstractmethod
    def _validate_create_data(self, data: C) -> None:
        """
        Валидация данных для создания сущности.

        Args:
            data: Данные для создания

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        pass

    @abstractmethod
    def _validate_update_data(self, data: U) -> None:
        """
        Валидация данных для обновления сущности.

        Args:
            data: Данные для обновления

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        pass

    @abstractmethod
    def _to_response(self, entity: T) -> Any:
        """
        Преобразование доменной сущности в схему ответа.

        Args:
            entity: Доменная сущность

        Returns:
            Схема ответа (DTO)
        """
        pass

    @abstractmethod
    def _get_entity_name(self) -> str:
        """
        Получение имени сущности для логирования.

        Returns:
            Имя сущности в единственном числе
        """
        pass

    @handle_service_errors
    async def create(self, data: C) -> T:
        """
        Создание новой сущности.

        Args:
            data: Данные для создания сущности

        Returns:
            Созданная доменная сущность

        Raises:
            ValueError: Если данные не проходят валидацию
            Exception: При других ошибках создания
        """
        # Валидация входных данных
        self._validate_create_data(data)

        # Создание сущности через репозиторий
        entity = await self.repository.save(data)

        entity_name = self._get_entity_name()
        logger.info(f"Created {entity_name}: ID={getattr(entity, 'id', 'unknown')}")

        return entity

    @handle_service_errors
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Получение сущности по ID.

        Args:
            entity_id: ID сущности

        Returns:
            Найденная сущность или None

        Raises:
            ValueError: Если ID некорректен
        """
        if entity_id <= 0:
            raise ValueError(f"ID {self._get_entity_name()} должен быть положительным числом")

        entity = await self.repository.find_by_id(entity_id)

        if not entity:
            entity_name = self._get_entity_name()
            logger.warning(f"{entity_name} with ID {entity_id} not found")

        return entity

    @handle_service_errors
    async def get_list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        search_fields: Optional[List[str]] = None,
        search_text: Optional[str] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Получение списка сущностей с фильтрами и поиском.

        Args:
            filters: Словарь с фильтрами {field_name: field_value}
            search_fields: Список полей для текстового поиска
            search_text: Текст для поиска
            order_by: Поле для сортировки
            order_desc: Сортировка по убыванию
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            Словарь с результатами и метаданными пагинации

        Raises:
            ValueError: Если параметры limit или offset некорректны
        """
        if limit <= 0 or limit > 100:
            raise ValueError("Limit должен быть между 1 и 100")
        if offset < 0:
            raise ValueError("Offset не может быть отрицательным")

        # Получение данных через репозиторий
        entities = await self.repository.find_all(
            filters=filters,
            search_fields=search_fields,
            search_text=search_text,
            order_by=order_by,
            order_desc=order_desc,
            limit=limit,
            offset=offset,
        )

        # Получение общего количества
        total = await self.repository.count(
            filters=filters,
            search_fields=search_fields,
            search_text=search_text,
        )

        return {
            "items": [self._to_response(entity) for entity in entities],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @handle_service_errors
    async def update(self, entity_id: int, data: U) -> Optional[T]:
        """
        Обновление сущности.

        Args:
            entity_id: ID сущности для обновления
            data: Данные для обновления

        Returns:
            Обновленная сущность или None, если не найдена

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        # Валидация входных данных
        self._validate_update_data(data)

        # Получение существующей сущности
        entity = await self.get_by_id(entity_id)
        if not entity:
            return None

        # Обновление через репозиторий
        updated_entity = await self.repository.update(entity_id, data)

        if updated_entity:
            entity_name = self._get_entity_name()
            logger.info(f"Updated {entity_name}: ID={entity_id}")

        return updated_entity

    @handle_service_errors
    async def delete(self, entity_id: int) -> bool:
        """
        Удаление сущности (мягкое удаление).

        Args:
            entity_id: ID сущности для удаления

        Returns:
            True если удаление успешно, False в противном случае

        Raises:
            ValueError: Если ID некорректен
        """
        if entity_id <= 0:
            raise ValueError(f"ID {self._get_entity_name()} должен быть положительным числом")

        # Получение сущности для проверки существования
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False

        # Удаление через репозиторий
        result = await self.repository.delete(entity_id)

        if result:
            entity_name = self._get_entity_name()
            logger.info(f"Deleted {entity_name}: ID={entity_id}")

        return result

    @handle_service_errors
    async def exists_by_field(self, field_name: str, field_value: Any) -> bool:
        """
        Проверка существования сущности по значению поля.

        Args:
            field_name: Имя поля для проверки
            field_value: Значение поля

        Returns:
            True если сущность существует, False в противном случае
        """
        return await self.repository.exists_by_field(field_name, field_value)

    @handle_service_errors
    async def get_stats(self) -> Dict[str, Any]:
        """
        Получение базовой статистики по сущностям.

        Returns:
            Словарь со статистикой
        """
        return await self.repository.get_stats()

    @handle_service_errors
    async def count(
        self,
        filters: Optional[Dict[str, Any]] = None,
        search_fields: Optional[List[str]] = None,
        search_text: Optional[str] = None,
    ) -> int:
        """
        Подсчет количества сущностей с фильтрами.

        Args:
            filters: Словарь с фильтрами {field_name: field_value}
            search_fields: Список полей для текстового поиска
            search_text: Текст для поиска

        Returns:
            Количество найденных сущностей
        """
        return await self.repository.count(
            filters=filters,
            search_fields=search_fields,
            search_text=search_text,
        )

    @handle_service_errors
    async def count_by_period(self, days: int, date_field: str = "created_at") -> int:
        """
        Подсчет количества сущностей за период.

        Args:
            days: Количество дней назад от текущего момента
            date_field: Имя поля с датой

        Returns:
            Количество сущностей за период
        """
        return await self.repository.count_by_period(days, date_field)