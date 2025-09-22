"""
Базовый класс для Value Objects с общей логикой валидации
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass(frozen=True)
class BaseValueObject(ABC):
    """
    Базовый класс для Value Objects с унифицированной логикой валидации.

    Предоставляет общую функциональность для:
    - Валидации типа значения
    - Обрезки пробелов для строковых значений
    - Валидации длины/диапазона
    - Строкового представления
    - Сравнения и хэширования

    Наследники должны определить параметры валидации через свойства класса.
    """

    value: Any

    def __post_init__(self):
        """
        Валидация после инициализации объекта.

        Выполняет последовательность валидаций:
        1. Валидация типа значения
        2. Обрезка пробелов (для строк)
        3. Валидация длины/диапазона
        """
        # Валидация типа
        self._validate_type()

        # Обрезка пробелов для строковых значений
        if self._should_strip_value():
            self._strip_value()

        # Валидация длины/диапазона
        self._validate_length()

    @abstractmethod
    def _validate_type(self) -> None:
        """
        Валидация типа значения.

        Должен быть реализован в наследниках для проверки
        корректности типа переданного значения.
        """
        pass

    def _should_strip_value(self) -> bool:
        """
        Определяет, нужно ли обрезать пробелы у значения.

        По умолчанию возвращает True для строковых значений.
        Может быть переопределен в наследниках.

        Returns:
            bool: True если нужно обрезать пробелы
        """
        return isinstance(self.value, str)

    def _strip_value(self) -> None:
        """
        Обрезает пробелы у строкового значения.

        Использует object.__setattr__ для изменения значения
        в frozen dataclass.
        """
        if isinstance(self.value, str):
            object.__setattr__(self, "value", self.value.strip())

    def _validate_length(self) -> None:
        """
        Валидация длины или диапазона значения.

        Базовая реализация не выполняет проверок.
        Наследники могут переопределить для специфической валидации.
        """
        pass

    def __str__(self) -> str:
        """
        Строковое представление Value Object.

        Returns:
            str: Строковое представление значения
        """
        return str(self.value) if self.value is not None else ""

    def __eq__(self, other) -> bool:
        """
        Сравнение с другим Value Object.

        Для строковых значений сравнение регистронезависимое.
        Для других типов - стандартное сравнение.

        Args:
            other: Объект для сравнения

        Returns:
            bool: True если объекты равны
        """
        if not isinstance(other, self.__class__):
            return False

        if isinstance(self.value, str) and isinstance(other.value, str):
            return self.value.lower() == other.value.lower()

        return self.value == other.value

    def __hash__(self) -> int:
        """
        Хэш для использования в множествах и словарях.

        Для строковых значений хэш вычисляется от нижнего регистра.
        Для других типов - стандартный хэш.

        Returns:
            int: Хэш-значение объекта
        """
        if isinstance(self.value, str):
            return hash(self.value.lower())

        return hash(self.value)

    @classmethod
    def _get_expected_type(cls) -> type:
        """
        Возвращает ожидаемый тип значения.

        Используется для сообщений об ошибках валидации.
        По умолчанию возвращает тип первого поля dataclass.

        Returns:
            type: Ожидаемый тип значения
        """
        # Получаем аннотацию типа из поля value
        annotations = cls.__annotations__
        if "value" in annotations:
            return annotations["value"]
        return type(None)

    def _get_type_error_message(self, actual_type: type) -> str:
        """
        Формирует сообщение об ошибке типа.

        Args:
            actual_type: Фактический тип значения

        Returns:
            str: Сообщение об ошибке
        """
        expected_type = self._get_expected_type()
        return f"Значение должно быть типа {expected_type.__name__}, получен {actual_type.__name__}"