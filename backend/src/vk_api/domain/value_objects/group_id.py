"""
Value Object для VK Group ID
"""

from typing import Union
from pydantic import Field, field_validator

from shared.domain.value_objects import ValueObject


class VKGroupID(ValueObject):
    """Value Object для VK Group ID"""
    
    value: int = Field(..., gt=0, description="VK Group ID")
    
    @field_validator('value')
    @classmethod
    def validate_group_id(cls, v: int) -> int:
        """Валидация Group ID"""
        if v <= 0:
            raise ValueError("Group ID must be positive")
        return v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "VKGroupID":
        """Создать из строки"""
        try:
            return cls(value=int(value))
        except ValueError as e:
            raise ValueError(f"Invalid Group ID format: {value}") from e
    
    @classmethod
    def from_union(cls, value: Union[int, str, "VKGroupID"]) -> "VKGroupID":
        """Создать из различных типов"""
        if isinstance(value, VKGroupID):
            return value
        if isinstance(value, str):
            return cls.from_string(value)
        if isinstance(value, int):
            return cls(value=value)
        raise ValueError(f"Unsupported type for Group ID: {type(value)}")
