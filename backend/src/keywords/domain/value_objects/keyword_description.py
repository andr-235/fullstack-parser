"""
Value Object для описания ключевого слова
"""

from dataclasses import dataclass
from typing import Optional

from src.keywords.shared.base_value_object import BaseValueObject
from src.keywords.shared.error_handlers import handle_validation_errors
from src.keywords.shared.validation_utils import ValidationUtils


@dataclass(frozen=True)
class KeywordDescription(BaseValueObject):
    """Value Object для описания ключевого слова с валидацией"""

    value: Optional[str]

    @handle_validation_errors
    def _validate_type(self) -> None:
        """
        Валидация типа и формата значения описания.

        Использует ValidationUtils для комплексной валидации,
        включая проверку типа, длины и формата описания.
        """
        # Валидируем через ValidationUtils, который включает все проверки
        cleaned_value = ValidationUtils.validate_description(self.value)

        # Обновляем значение, если оно было изменено (очищено от пробелов или установлено None)
        if cleaned_value != self.value:
            object.__setattr__(self, "value", cleaned_value)

    def _should_strip_value(self) -> bool:
        """
        Обрезать пробелы только для непустых значений.

        Этот метод больше не нужен, так как обрезка пробелов
        выполняется в ValidationUtils.validate_description().
        """
        return False

    def _validate_length(self) -> None:
        """
        Валидация длины описания.

        Этот метод больше не нужен, так как валидация длины
        выполняется в ValidationUtils.validate_description().
        """
        pass

    def __str__(self) -> str:
        """Строковое представление"""
        return self.value or ""

    def __bool__(self) -> bool:
        """Проверка на пустоту"""
        return self.value is not None and bool(self.value.strip())

    @classmethod
    def empty(cls) -> "KeywordDescription":
        """Создать пустое описание"""
        return cls(None)