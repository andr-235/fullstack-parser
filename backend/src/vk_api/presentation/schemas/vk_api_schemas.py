"""
Pydantic схемы для VK API модуля
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from vk_api.shared.presentation.schemas.pagination import PaginatedResponse


class VKAPIHealthCheckResponse(BaseModel):
    """Ответ проверки здоровья VK API"""
    
    model_config = ConfigDict(from_attributes=True)
    
    status: str = Field(..., description="Статус здоровья")
    timestamp: str = Field(..., description="Время проверки")
    vk_api: Optional[Dict[str, Any]] = Field(None, description="Статус VK API")
    cache: Optional[Dict[str, Any]] = Field(None, description="Статус кеша")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")


class VKAPIStatsResponse(BaseModel):
    """Ответ со статистикой VK API"""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_requests: int = Field(..., description="Общее количество запросов")
    successful_requests: int = Field(..., description="Успешные запросы")
    failed_requests: int = Field(..., description="Неудачные запросы")
    cache_hits: int = Field(..., description="Попадания в кеш")
    cache_misses: int = Field(..., description="Промахи кеша")
    avg_response_time: float = Field(..., description="Среднее время ответа")
    last_updated: datetime = Field(..., description="Время последнего обновления")


class VKAPIErrorResponse(BaseModel):
    """Ответ об ошибке VK API"""
    
    model_config = ConfigDict(from_attributes=True)
    
    error: str = Field(..., description="Тип ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки")
    timestamp: datetime = Field(..., description="Время ошибки")


class VKAPIConfigResponse(BaseModel):
    """Ответ с конфигурацией VK API"""
    
    model_config = ConfigDict(from_attributes=True)
    
    version: str = Field(..., description="Версия VK API")
    base_url: str = Field(..., description="Базовый URL")
    timeout: float = Field(..., description="Таймаут запросов")
    max_requests_per_second: int = Field(..., description="Максимум запросов в секунду")
    cache_enabled: bool = Field(..., description="Включено ли кеширование")
    cache_ttl: int = Field(..., description="TTL кеша в секундах")
