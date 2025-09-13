"""
Общие API схемы

Содержит общие Pydantic схемы для всех модулей
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    
    error: str = Field(..., description="Тип ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительные детали ошибки")
    correlation_id: Optional[str] = Field(None, description="ID для отслеживания запроса")


class ValidationErrorResponse(BaseModel):
    """Схема ответа с ошибками валидации"""
    
    error: str = Field(default="validation_error", description="Тип ошибки")
    message: str = Field(default="Ошибка валидации данных", description="Сообщение об ошибке")
    validation_errors: List[Dict[str, Any]] = Field(..., description="Список ошибок валидации")
    correlation_id: Optional[str] = Field(None, description="ID для отслеживания запроса")


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    
    limit: int = Field(default=50, ge=1, le=100, description="Количество записей на странице")
    offset: int = Field(default=0, ge=0, description="Смещение от начала")


class PaginationResponse(BaseModel):
    """Схема ответа с пагинацией"""
    
    total: int = Field(..., description="Общее количество записей")
    limit: int = Field(..., description="Лимит записей на странице")
    offset: int = Field(..., description="Смещение от начала")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")
    pages: int = Field(..., description="Общее количество страниц")
    current_page: int = Field(..., description="Текущая страница")


class SuccessResponse(BaseModel):
    """Схема успешного ответа"""
    
    success: bool = Field(default=True, description="Статус успеха")
    message: str = Field(..., description="Сообщение")
    data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class HealthCheckResponse(BaseModel):
    """Схема ответа проверки здоровья"""
    
    status: str = Field(..., description="Статус сервиса")
    timestamp: str = Field(..., description="Время проверки")
    version: str = Field(..., description="Версия приложения")
    services: Dict[str, str] = Field(..., description="Статус зависимых сервисов")
