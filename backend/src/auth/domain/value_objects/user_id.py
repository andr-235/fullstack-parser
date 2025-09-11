"""
Value Object для UserId

Инкапсулирует логику работы с идентификаторами пользователей
"""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class UserId:
    """
    Value Object для идентификатора пользователя
    
    Обеспечивает типобезопасность для ID пользователей
    """
    
    value: int
    
    def __post_init__(self):
        """Валидация ID после инициализации"""
        if not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("User ID must be a positive integer")
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, UserId):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    @classmethod
    def from_int(cls, value: int) -> 'UserId':
        """Создать UserId из int"""
        return cls(value=value)
    
    @classmethod
    def from_string(cls, value: str) -> 'UserId':
        """Создать UserId из строки"""
        try:
            return cls(value=int(value))
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to UserId")
