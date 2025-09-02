"""
Зависимости для ARQ модуля

Содержит функции зависимостей для FastAPI роутеров ARQ.
"""

from typing import Optional
from fastapi import Depends, HTTPException

from ..infrastructure.arq_service import arq_service
from ..config import config_service


async def get_arq_service():
    """
    Зависимость для получения ARQ сервиса

    Проверяет, что ARQ сервис инициализирован и доступен.
    """
    if not arq_service._is_initialized:
        raise HTTPException(
            status_code=503, detail="ARQ сервис не инициализирован"
        )

    return arq_service


async def check_arq_enabled():
    """
    Зависимость для проверки, что ARQ включен в конфигурации

    Вызывает ошибку 503, если ARQ отключен.
    """
    if not config_service.arq_enabled:
        raise HTTPException(
            status_code=503, detail="ARQ отключен в конфигурации"
        )

    return True


def get_arq_config():
    """
    Зависимость для получения конфигурации ARQ
    """
    return config_service.get_arq_config()
