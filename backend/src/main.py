"""
Основной файл приложения VK Comments Parser
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.common.logging import get_logger, setup_logging

# Настраиваем логирование
setup_logging()

# Импортируем все модели для правильной инициализации SQLAlchemy relationships
from src.models import *  # noqa: F401, F403

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan приложения"""
    logger.info("🚀 Запуск VK Comments Parser...")
    
    # Инициализируем auth модуль
    try:
        from auth.init_app import init_auth_module
        await init_auth_module()
        logger.info("✅ Auth module initialized")
    except Exception as e:
        logger.warning(f"⚠️ Auth module initialization failed: {e}")
    
    yield
    logger.info("🛑 Остановка VK Comments Parser...")


# Инициализация rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="VK Comments Parser API",
    version="1.7.0",
    description="API для парсинга комментариев VK",
    lifespan=lifespan,
)

# Добавляем rate limiter в приложение
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "VK Comments Parser API", "version": "1.7.0"}


@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    return {"status": "healthy", "version": "1.7.0"}


@app.get("/api/v1/metrics/dashboard")
async def get_dashboard_metrics():
    """Получить метрики для дашборда"""
    try:
        from src.common.database import get_async_session
        from src.comments.service import CommentService
        from comments.repository import CommentRepository
        from groups.service import GroupService
        from keywords.service import KeywordsService
        from keywords.models import KeywordsRepository
        
        # Получаем сессию БД
        async with get_async_session() as db_session:
            # Инициализируем сервисы
            comment_repo = CommentRepository(db_session)
            comment_service = CommentService(comment_repo)
            group_service = GroupService(db_session)
            keyword_repo = KeywordsRepository(db_session)
            keyword_service = KeywordsService(keyword_repo)
            
            # Получаем метрики
            total_comments = await comment_service.get_total_comments_count()
            comments_growth = await comment_service.get_comments_growth_percentage(30)
            
            active_groups = await group_service.get_active_groups_count()
            groups_growth = await group_service.get_groups_growth_percentage(30)
            
            total_keywords = await keyword_service.get_total_keywords_count()
            keywords_growth = await keyword_service.get_keywords_growth_percentage(30)
            
            # Заглушки для парсеров
            active_parsers = 0
            parsers_growth = 0.0
            
            return {
                "comments": {
                    "total": total_comments,
                    "growth_percentage": round(comments_growth, 1),
                    "trend": "рост с прошлого месяца" if comments_growth > 0 else "снижение с прошлого месяца"
                },
                "groups": {
                    "active": active_groups,
                    "growth_percentage": round(groups_growth, 1),
                    "trend": "рост с прошлого месяца" if groups_growth > 0 else "снижение с прошлого месяца"
                },
                "keywords": {
                    "total": total_keywords,
                    "growth_percentage": round(keywords_growth, 1),
                    "trend": "рост с прошлого месяца" if keywords_growth > 0 else "снижение с прошлого месяца"
                },
                "parsers": {
                    "active": active_parsers,
                    "growth_percentage": round(parsers_growth, 1),
                    "trend": "рост с прошлого месяца" if parsers_growth > 0 else "снижение с прошлого месяца"
                }
            }
            
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard metrics")


# Импортируем все модели для правильной инициализации relationships
try:
    from src.models import *  # noqa: F401, F403
except ImportError as e:
    logger.warning(f"Some models not available: {e}")

# Подключаем роутеры модулей
try:
    from src.auth.router import router as auth_router
    from src.authors.api import router as authors_router
    from src.comments.router import router as comments_router
    from src.groups.router import router as groups_router
    from src.keywords.router import router as keywords_router
    from src.user.routers import user_router
    from src.tasks.router import router as tasks_router

    app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
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
