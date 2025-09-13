"""
Value Object для VK Post ID
"""

from typing import Union
from pydantic import Field, field_validator

from shared.domain.value_objects import ValueObject


class VKPostID(ValueObject):
    """Value Object для VK Post ID"""
    
    value: int = Field(..., gt=0, description="VK Post ID")
    
    @field_validator('value')
    @classmethod
    def validate_post_id(cls, v: int) -> int:
        """Валидация Post ID"""
        if v <= 0:
            raise ValueError("Post ID must be positive")
        return v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "VKPostID":
        """Создать из строки"""
        try:
            return cls(value=int(value))
        except ValueError as e:
            raise ValueError(f"Invalid Post ID format: {value}") from e
    
    @classmethod
    def from_union(cls, value: Union[int, str, "VKPostID"]) -> "VKPostID":
        """Создать из различных типов"""
        if isinstance(value, VKPostID):
            return value
        if isinstance(value, str):
            return cls.from_string(value)
        if isinstance(value, int):
            return cls(value=value)
        raise ValueError(f"Unsupported type for Post ID: {type(value)}")
