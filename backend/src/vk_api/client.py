"""
HTTP клиент для VK API
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from .exceptions import VKAPIError


class VKAPIClient:
    """HTTP клиент для VK API"""
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        version: str = "5.131",
        base_url: str = "https://api.vk.com/method",
        timeout: float = 30.0,
        max_requests_per_second: float = 2.0
    ):
        self.access_token = access_token
        self.version = version
        self.base_url = base_url
        self.timeout = timeout
        self.max_requests_per_second = max_requests_per_second
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time = 0.0
        self._request_count = 0
        self._rate_limit_reset_time = time.time()
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()
    
    async def _ensure_session(self):
        """Создать HTTP сессию"""
        if self._session is None or self._session.closed:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": "VK-API-Client/1.0",
                    "Accept": "application/json",
                }
            )
    
    async def _close_session(self):
        """Закрыть HTTP сессию"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _rate_limit(self):
        """Ограничение частоты запросов"""
        current_time = time.time()
        
        # Сброс счетчика каждую секунду
        if current_time - self._rate_limit_reset_time >= 1.0:
            self._request_count = 0
            self._rate_limit_reset_time = current_time
        
        # Проверка лимита
        if self._request_count >= self.max_requests_per_second:
            wait_time = 1.0 - (current_time - self._rate_limit_reset_time)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                self._request_count = 0
                self._rate_limit_reset_time = time.time()
        
        # Минимальный интервал между запросами
        min_interval = 1.0 / self.max_requests_per_second
        time_since_last = current_time - self._last_request_time
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self._request_count += 1
        self._last_request_time = time.time()
    
    def _build_url(self, method: str, params: Dict[str, Any]) -> str:
        """Построить URL запроса"""
        url = f"{self.base_url}/{method}"
        
        # Добавляем токен и версию
        params = params.copy()
        if self.access_token:
            params["access_token"] = self.access_token
        params["v"] = self.version
        
        # Кодируем параметры
        query_string = urlencode(params, doseq=True)
        return f"{url}?{query_string}"
    
    def _handle_error(self, response_data: Dict[str, Any]) -> None:
        """Обработать ошибку VK API"""
        if "error" not in response_data:
            return
        
        error = response_data["error"]
        error_code = error.get("error_code", 0)
        error_msg = error.get("error_msg", "Unknown error")
        
        raise VKAPIError(f"VK API Error {error_code}: {error_msg}", error_code)
    
    async def request(
        self, 
        method: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Выполнить запрос к VK API"""
        await self._ensure_session()
        await self._rate_limit()
        
        params = params or {}
        url = self._build_url(method, params)
        
        try:
            import aiohttp
            async with self._session.get(url) as response:
                response.raise_for_status()
                response_data = await response.json()
                
                self._handle_error(response_data)
                return response_data.get("response", {})
                
        except aiohttp.ClientTimeout:
            raise VKAPIError(f"Request timeout ({self.timeout}s)")
        except aiohttp.ClientError as e:
            raise VKAPIError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise VKAPIError(f"Invalid JSON response: {str(e)}")
    
    async def get_group(self, group_id: int) -> Dict[str, Any]:
        """Получить информацию о группе"""
        params = {"group_id": group_id, "fields": "description,members_count,is_closed,type"}
        response = await self.request("groups.getById", params)
        return response[0] if response else {}
    
    async def search_groups(
        self, 
        query: str, 
        count: int = 20, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Поиск групп"""
        params = {
            "q": query,
            "count": count,
            "offset": offset,
            "type": "group"
        }
        return await self.request("groups.search", params)
    
    async def get_group_posts(
        self, 
        group_id: int, 
        count: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Получить посты группы"""
        params = {
            "owner_id": -abs(group_id),
            "count": count,
            "offset": offset
        }
        return await self.request("wall.get", params)
    
    async def get_post_comments(
        self, 
        group_id: int, 
        post_id: int, 
        count: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Получить комментарии к посту"""
        params = {
            "owner_id": -abs(group_id),
            "post_id": post_id,
            "count": count,
            "offset": offset
        }
        return await self.request("wall.getComments", params)
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Получить информацию о пользователе"""
        params = {"user_ids": user_id, "fields": "photo_50,photo_100,photo_200"}
        response = await self.request("users.get", params)
        return response[0] if response else {}


__all__ = ["VKAPIClient"]
