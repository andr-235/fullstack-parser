"""
Реализация VK API клиента
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import aiohttp

from shared.infrastructure.external_apis.base_client import BaseHTTPClient
from shared.presentation.exceptions import InternalServerException as ServiceUnavailableError, ValidationException as ValidationError
from shared.config import settings


logger = logging.getLogger(__name__)


class VKAPIClientImpl(BaseHTTPClient):
    """Реализация VK API клиента"""
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        version: str = "5.199",
        base_url: str = "https://api.vk.com/method",
        timeout: float = 30.0,
        max_requests_per_second: int = 2
    ):
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            max_requests_per_second=max_requests_per_second
        )
        
        self.access_token = access_token or settings.VK_API_ACCESS_TOKEN
        self.version = version
        self._last_request_time = 0.0
        self._request_interval = 1.0 / max_requests_per_second
    
    async def call_method(
        self, 
        method: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Вызвать метод VK API
        
        Args:
            method: Название метода VK API
            params: Параметры метода
            
        Returns:
            Ответ от VK API
            
        Raises:
            ServiceUnavailableError: При ошибке API
            ValidationError: При невалидных параметрах
        """
        if not method:
            raise ValidationError("Method name is required")
        
        # Rate limiting
        await self._rate_limit()
        
        # Подготавливаем параметры
        request_params = {
            "access_token": self.access_token,
            "v": self.version,
            **(params or {})
        }
        
        # Удаляем None значения
        request_params = {k: v for k, v in request_params.items() if v is not None}
        
        try:
            # Выполняем запрос
            response = await self._make_request(
                method="GET",
                url=f"/{method}",
                params=request_params
            )
            
            # Обрабатываем ответ
            return await self._handle_response(response, method)
            
        except Exception as e:
            logger.error(f"VK API call failed for method {method}: {e}")
            raise ServiceUnavailableError(f"VK API call failed: {e}")
    
    async def _handle_response(
        self, 
        response: aiohttp.ClientResponse, 
        method: str
    ) -> Dict[str, Any]:
        """Обработка ответа VK API"""
        try:
            data = await response.json()
        except Exception as e:
            logger.error(f"Failed to parse VK API response: {e}")
            raise ServiceUnavailableError("Invalid response format from VK API")
        
        # Проверяем статус HTTP
        if response.status != 200:
            error_msg = data.get("error", {}).get("error_msg", "Unknown error")
            logger.error(f"VK API HTTP error {response.status}: {error_msg}")
            raise ServiceUnavailableError(f"VK API HTTP error: {error_msg}")
        
        # Проверяем наличие ошибки в ответе
        if "error" in data:
            error = data["error"]
            error_code = error.get("error_code", 0)
            error_msg = error.get("error_msg", "Unknown error")
            
            logger.error(f"VK API error {error_code}: {error_msg}")
            
            # Обрабатываем специфичные ошибки
            if error_code == 5:  # Invalid access token
                raise ServiceUnavailableError("Invalid VK API access token")
            elif error_code == 6:  # Too many requests
                raise ServiceUnavailableError("VK API rate limit exceeded")
            elif error_code == 15:  # Access denied
                raise ServiceUnavailableError("Access denied to VK API")
            elif error_code == 18:  # Page blocked
                raise ServiceUnavailableError("VK page is blocked")
            else:
                raise ServiceUnavailableError(f"VK API error: {error_msg}")
        
        return data
    
    async def _rate_limit(self) -> None:
        """Ограничение частоты запросов"""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self._request_interval:
            sleep_time = self._request_interval - time_since_last_request
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья VK API клиента"""
        try:
            # Простой запрос для проверки доступности
            response = await self.call_method("users.get", {"user_ids": "1"})
            
            return {
                "status": "healthy",
                "version": self.version,
                "base_url": self.base_url,
                "has_token": bool(self.access_token),
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"VK API health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "version": self.version,
                "base_url": self.base_url,
                "has_token": bool(self.access_token),
                "timestamp": time.time()
            }
    
    async def get_access_token_info(self) -> Optional[Dict[str, Any]]:
        """Получить информацию о токене доступа"""
        try:
            response = await self.call_method("users.get", {"fields": "id"})
            return response.get("response", [{}])[0] if response.get("response") else None
        except Exception as e:
            logger.error(f"Failed to get access token info: {e}")
            return None
    
    async def validate_token(self) -> bool:
        """Проверить валидность токена"""
        try:
            await self.call_method("users.get", {"user_ids": "1"})
            return True
        except Exception:
            return False
