"""
Redis клиент для кеширования и очередей
"""

import json
import os
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from redis.asyncio import Redis


class RedisClient:
    """Асинхронный Redis клиент"""
    
    def __init__(self, url: Optional[str] = None):
        self.url = url or get_redis_url()
        self._client: Optional[Redis] = None
    
    async def get_client(self) -> Redis:
        """Получить Redis клиент"""
        if self._client is None:
            self._client = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
        return self._client
    
    async def close(self):
        """Закрыть соединение"""
        if self._client:
            try:
                await self._client.close()
            finally:
                self._client = None
    
    async def ping(self) -> bool:
        """Проверить соединение"""
        try:
            client = await self.get_client()
            return await client.ping()
        except Exception:
            return False
    
    # Базовые операции
    async def get(self, key: str) -> Optional[str]:
        """Получить значение по ключу"""
        client = await self.get_client()
        return await client.get(key)
    
    async def set(
        self, 
        key: str, 
        value: Union[str, Dict, List], 
        ttl: Optional[int] = None
    ) -> bool:
        """Установить значение"""
        client = await self.get_client()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        if ttl:
            return await client.setex(key, ttl, value)
        else:
            return await client.set(key, value)
    
    async def delete(self, key: str) -> bool:
        """Удалить ключ"""
        client = await self.get_client()
        return bool(await client.delete(key))
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        client = await self.get_client()
        return bool(await client.exists(key))
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Установить TTL для ключа"""
        client = await self.get_client()
        return await client.expire(key, ttl)
    
    # Операции с JSON
    async def get_json(self, key: str) -> Optional[Union[Dict, List]]:
        """Получить JSON значение"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(
        self, 
        key: str, 
        value: Union[Dict, List], 
        ttl: Optional[int] = None
    ) -> bool:
        """Установить JSON значение"""
        return await self.set(key, value, ttl)
    
    # Операции с хешами
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Получить значение из хеша"""
        client = await self.get_client()
        return await client.hget(name, key)
    
    async def hset(self, name: str, key: str, value: Union[str, Dict, List]) -> bool:
        """Установить значение в хеш"""
        client = await self.get_client()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        return await client.hset(name, key, value)
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Получить все значения из хеша"""
        client = await self.get_client()
        return await client.hgetall(name)
    
    async def hdel(self, name: str, key: str) -> bool:
        """Удалить ключ из хеша"""
        client = await self.get_client()
        return bool(await client.hdel(name, key))
    
    # Операции с множествами
    async def sadd(self, name: str, *values: str) -> int:
        """Добавить значения в множество"""
        client = await self.get_client()
        return await client.sadd(name, *values)
    
    async def smembers(self, name: str) -> set:
        """Получить все значения множества"""
        client = await self.get_client()
        return await client.smembers(name)
    
    async def srem(self, name: str, *values: str) -> int:
        """Удалить значения из множества"""
        client = await self.get_client()
        return await client.srem(name, *values)
    
    # Операции с списками
    async def lpush(self, name: str, *values: str) -> int:
        """Добавить значения в начало списка"""
        client = await self.get_client()
        return await client.lpush(name, *values)
    
    async def rpush(self, name: str, *values: str) -> int:
        """Добавить значения в конец списка"""
        client = await self.get_client()
        return await client.rpush(name, *values)
    
    async def lpop(self, name: str) -> Optional[str]:
        """Получить и удалить первый элемент списка"""
        client = await self.get_client()
        return await client.lpop(name)
    
    async def rpop(self, name: str) -> Optional[str]:
        """Получить и удалить последний элемент списка"""
        client = await self.get_client()
        return await client.rpop(name)
    
    async def llen(self, name: str) -> int:
        """Получить длину списка"""
        client = await self.get_client()
        return await client.llen(name)
    
    # Операции с TTL
    async def ttl(self, key: str) -> int:
        """Получить TTL ключа"""
        client = await self.get_client()
        return await client.ttl(key)
    
    # Операции с паттернами
    async def keys(self, pattern: str) -> List[str]:
        """Найти ключи по паттерну"""
        client = await self.get_client()
        return await client.keys(pattern)
    
    async def scan(self, cursor: int = 0, match: Optional[str] = None, count: int = 100) -> tuple:
        """Сканировать ключи"""
        client = await self.get_client()
        return await client.scan(cursor, match, count)
    
    # Операции с транзакциями
    async def pipeline(self):
        """Создать pipeline"""
        client = await self.get_client()
        return client.pipeline()
    
    # Операции с блокировками
    async def setnx(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Установить значение только если ключ не существует"""
        client = await self.get_client()
        
        if ttl:
            return await client.set(key, value, nx=True, ex=ttl)
        else:
            return await client.set(key, value, nx=True)
    
    async def lock(self, key: str, timeout: int = 10) -> bool:
        """Получить блокировку"""
        return await self.setnx(f"lock:{key}", "1", ttl=timeout)
    
    async def unlock(self, key: str) -> bool:
        """Освободить блокировку"""
        return await self.delete(f"lock:{key}")


def get_redis_url() -> str:
    """Получить URL Redis"""
    return os.getenv(
        "REDIS_URL",
        "redis://redis:6379/0"
    )


# Глобальный экземпляр Redis клиента
redis_client = RedisClient()
