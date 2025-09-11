"""
DTO для регистрации пользователя

Data Transfer Object для данных регистрации
"""

from dataclasses import dataclass
from pydantic import BaseModel, EmailStr, Field


class RegisterUserDTO(BaseModel):
    """
    DTO для регистрации пользователя
    
    Валидирует данные регистрации
    """
    
    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str = Field(..., min_length=1, max_length=255, description="Полное имя")
    password: str = Field(..., min_length=8, max_length=128, description="Пароль")
    
    class Config:
        """Конфигурация Pydantic"""
        from_attributes = True
