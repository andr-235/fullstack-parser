"""
Pydantic модель для ID пользователя

Инкапсулирует логику работы с ID пользователя
"""

from pydantic import BaseModel, Field


class UserId(BaseModel):
    """ID пользователя с валидацией"""

    value: int = Field(gt=0, description="ID пользователя")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value

    class Config:
        frozen = True
