"""
VK Comments Parser - FastAPI Backend
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db

# Логирование
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    description="Парсер комментариев из групп ВКонтакте с фильтрацией по ключевым словам",
    version="1.0.0",
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("🚀 Запуск VK Comments Parser...")
    await init_db()
    logger.info("📊 База данных инициализирована")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    logger.info("🛑 Остановка VK Comments Parser...")


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "VK Comments Parser API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vk-comments-parser", "version": "1.0.0"}


# Подключение API роутов
app.include_router(api_router, prefix=settings.api_v1_str)
