"""
Инициализация модуля Auth в приложении
"""

import os
import asyncio
from typing import Optional

from common.logging import get_logger
from common.redis_client import redis_client
from .setup import setup_auth

logger = get_logger(__name__)


async def wait_for_redis(max_retries: int = 30, delay: float = 1.0) -> bool:
    """Ждать доступности Redis с retry"""
    for attempt in range(max_retries):
        try:
            if await redis_client.ping():
                return True
        except Exception as e:
            logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
        
        await asyncio.sleep(delay)
    
    return False


async def init_auth_module():
    """Инициализировать модуль аутентификации"""
    try:
        # Получаем конфигурацию из переменных окружения
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        
        # Проверяем Redis подключение
        if await wait_for_redis():
            logger.info("✅ Redis connection established")
            setup_auth(
                user_repository=None,  # Будет создаваться в dependencies
                redis_client=redis_client,  # Используем общий Redis клиент
                secret_key=secret_key,
                algorithm="HS256",
                access_token_expire_minutes=30,
                refresh_token_expire_days=7,
                password_rounds=12
            )
            logger.info("✅ Auth module initialized with Redis cache")
        else:
            logger.warning("⚠️ Redis unavailable, initializing without cache")
            setup_auth(
                user_repository=None,
                redis_client=None,  # Без кеширования
                secret_key=secret_key,
                algorithm="HS256",
                access_token_expire_minutes=30,
                refresh_token_expire_days=7,
                password_rounds=12
            )
            logger.info("✅ Auth module initialized without Redis cache")
            
    except Exception as e:
        logger.error(f"❌ Auth module initialization failed: {e}")
        raise
