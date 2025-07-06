"""
VK Comments Parser - FastAPI Backend
"""

from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import get_logger, setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Настройка и инициализация логирования
setup_logging(log_level=settings.log_level, json_logs=not settings.debug)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager для startup/shutdown событий"""
    # Startup
    logger.info("🚀 Запуск VK Comments Parser...")
    await init_db()
    logger.info("📊 База данных инициализирована")

    yield

    # Shutdown
    logger.info("🛑 Остановка VK Comments Parser...")


# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    description="Парсер комментариев из групп ВКонтакте с фильтрацией по ключевым словам",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging middleware
app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой endpoint"""
    return {
        "message": "VK Comments Parser API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "vk-comments-parser", "version": "1.0.0"}


# Подключение API роутов
app.include_router(api_router, prefix=settings.api_v1_str)
