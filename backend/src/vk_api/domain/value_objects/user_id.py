"""
Value Object для VK User ID
"""

from typing import Union
from pydantic import Field, field_validator

from shared.domain.value_objects import ValueObject


class VKUserID(ValueObject):
    """Value Object для VK User ID"""
    
    value: int = Field(..., gt=0, description="VK User ID")
    
    @field_validator('value')
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Валидация User ID"""
        if v <= 0:
            raise ValueError("User ID must be positive")
        return v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "VKUserID":
        """Создать из строки"""
        try:
            return cls(value=int(value))
        except ValueError as e:
            raise ValueError(f"Invalid User ID format: {value}") from e
    
    @classmethod
    def from_union(cls, value: Union[int, str, "VKUserID"]) -> "VKUserID":
        """Создать из различных типов"""
        if isinstance(value, VKUserID):
            return value
        if isinstance(value, str):
            return cls.from_string(value)
        if isinstance(value, int):
            return cls(value=value)
        raise ValueError(f"Unsupported type for User ID: {type(value)}")
