"""
Основной файл приложения VK Comments Parser
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Импорт роутеров
from auth import auth_router
from user import user_router
from comments.presentation.router import router as comments_router
from groups.router import router as groups_router
from parser.router import router as parser_router
from morphological.router import router as morphological_router
from keywords.router import router as keywords_router
from settings.router import router as settings_router
from health.router import router as health_router
from error_reporting.router import router as error_reporting_router
from authors import router as authors_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan приложения"""
    logger.info("🚀 Запуск VK Comments Parser...")
    yield
    logger.info("🛑 Остановка VK Comments Parser...")


# Создание FastAPI приложения
app = FastAPI(
    title="VK Comments Parser API",
    version="1.7.0",
    description="API для парсинга комментариев VK",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Обработчики исключений
@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации"""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    """Обработчик непредвиденных ошибок"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Базовые endpoints
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "VK Comments Parser API", "version": "1.7.0"}


@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    return {"status": "healthy", "version": "1.7.0"}


# Подключаем роутеры модулей
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1", tags=["Users"])
app.include_router(comments_router, prefix="/api/v1", tags=["Comments"])
app.include_router(groups_router, prefix="/api/v1", tags=["Groups"])
app.include_router(parser_router, prefix="/api/v1", tags=["Parser"])
app.include_router(morphological_router, prefix="/api/v1", tags=["Morphological Analysis"])
app.include_router(keywords_router, prefix="/api/v1", tags=["Keywords Management"])
app.include_router(settings_router, prefix="/api/v1", tags=["Settings Management"])
app.include_router(health_router, prefix="/api/v1", tags=["Health Monitoring"])
app.include_router(error_reporting_router, prefix="/api/v1", tags=["Error Reports"])
app.include_router(authors_router, prefix="/api/v1", tags=["Authors"])


# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
