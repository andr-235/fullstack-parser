"""
Основной файл приложения VK Comments Parser
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan приложения"""
    logger.info("🚀 Запуск VK Comments Parser...")
    yield
    logger.info("🛑 Остановка VK Comments Parser...")


app = FastAPI(
    title="VK Comments Parser API",
    version="1.7.0",
    description="API для парсинга комментариев VK",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации"""
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений"""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    """Обработчик непредвиденных ошибок"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "VK Comments Parser API", "version": "1.7.0"}


@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    return {"status": "healthy", "version": "1.7.0"}


# Подключаем роутеры модулей
try:
    # from auth.router import router as auth_router
    from authors.api import router as authors_router
    from comments.router import router as comments_router
    from groups.router import router as groups_router
    from keywords.router import router as keywords_router
    from user.routers import user_router
    from tasks.router import router as tasks_router

    # app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
    app.include_router(user_router, prefix="/api/v1", tags=["Users"])
    app.include_router(comments_router, prefix="/api/v1", tags=["Comments"])
    app.include_router(groups_router, prefix="/api/v1", tags=["Groups"])
    app.include_router(keywords_router, prefix="/api/v1", tags=["Keywords Management"])
    app.include_router(authors_router, prefix="/api/v1", tags=["Authors"])
    app.include_router(tasks_router, prefix="/api/v1", tags=["Tasks Management"])
except ImportError as e:
    logger.warning(f"Some modules not available: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
