"""
Health check эндпоинты
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/", summary="Корневой эндпоинт")
async def read_root():
    """Возвращает приветственное сообщение."""
    return {"message": "VK Comments Parser API is running"}


@router.get("/health", summary="Проверка состояния")
async def health_check():
    """Простая проверка работоспособности сервиса."""
    return {"status": "ok"}
