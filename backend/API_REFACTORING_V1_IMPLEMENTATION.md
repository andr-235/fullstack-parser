# 🚀 ПЛАН РЕАЛИЗАЦИИ РЕФАКТОРИНГА API V1

## 📋 ШАГ 1: СОЗДАНИЕ ИНФРАСТРУКТУРЫ

### 1.1 Создание новой структуры папок

```bash
# В ветке api-refactoring-v1
mkdir -p app/api/v1/routers
mkdir -p app/api/v1/middleware
mkdir -p app/api/v1/schemas
mkdir -p app/api/v1/handlers
```

### 1.2 Базовые компоненты

#### Создаем стандартизированные ответы:
```python
# app/api/v1/schemas/responses.py
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from uuid import uuid4


class MetaInfo(BaseModel):
    request_id: str = str(uuid4())
    timestamp: str = datetime.utcnow().isoformat()
    processing_time: Optional[float] = None
    cached: bool = False


class PaginationInfo(BaseModel):
    page: int
    size: int
    total: int
    has_next: bool
    has_prev: bool


class SuccessResponse(BaseModel):
    data: Any
    pagination: Optional[PaginationInfo] = None
    meta: MetaInfo


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
    meta: MetaInfo
```

#### Создаем базовый роутер:
```python
# app/api/v1/routers/base.py
from typing import List
from fastapi import APIRouter

from app.api.v1.schemas.responses import ErrorResponse


class BaseRouter(APIRouter):
    def __init__(self, prefix: str, tags: List[str]):
        super().__init__(
            prefix=prefix,
            tags=tags,
            responses={
                400: {"model": ErrorResponse, "description": "Bad Request"},
                401: {"model": ErrorResponse, "description": "Unauthorized"},
                403: {"model": ErrorResponse, "description": "Forbidden"},
                404: {"model": ErrorResponse, "description": "Not Found"},
                422: {"model": ErrorResponse, "description": "Validation Error"},
                429: {"model": ErrorResponse, "description": "Too Many Requests"},
                500: {"model": ErrorResponse, "description": "Internal Server Error"},
            }
        )
```

## 📋 ШАГ 2: ПРОСТОЕ MIDDLEWARE

### 2.1 Rate Limiting Middleware

```python
# app/api/v1/middleware/rate_limit.py
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """Простое rate limiting без Redis"""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Очищаем старые запросы
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]

        # Проверяем лимит
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Try again later.",
                        "retry_after": 60
                    },
                    "meta": {
                        "request_id": "rate_limit",
                        "timestamp": time.time()
                    }
                }
            )

        # Добавляем текущий запрос
        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response
```

### 2.2 Logging Middleware

```python
# app/api/v1/middleware/logging.py
import time
import logging
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов"""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        start_time = time.time()

        # Логируем входящий запрос
        logger.info(
            f"➡️  {request.method} {request.url.path} - {request.client.host}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "query_params": dict(request.query_params)
            }
        )

        try:
            response = await call_next(request)
            processing_time = time.time() - start_time

            # Логируем успешный ответ
            logger.info(
                f"✅ {request.method} {request.url.path} - {response.status_code} ({processing_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "processing_time": processing_time
                }
            )

            # Добавляем заголовки
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = str(processing_time)

            return response

        except Exception as e:
            processing_time = time.time() - start_time

            # Логируем ошибку
            logger.error(
                f"❌ {request.method} {request.url.path} - Error ({processing_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "processing_time": processing_time
                },
                exc_info=True
            )
            raise
```

## 📋 ШАГ 3: УЛУЧШЕННЫЕ ОБРАБОТЧИКИ ОШИБОК

### 3.1 Создаем улучшенные ошибки

```python
# app/api/v1/schemas/errors.py
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class APIError(HTTPException):
    """Базовый класс для API ошибок"""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None
    ):
        self.error_code = error_code
        self.details = details or {}
        self.field = field

        super().__init__(status_code=status_code, detail=message)


class ValidationError(APIError):
    """Ошибка валидации"""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details,
            field=field
        )


class NotFoundError(APIError):
    """Ресурс не найден"""

    def __init__(self, resource: str, resource_id: Optional[Any] = None):
        message = f"{resource} not found"
        if resource_id is not None:
            message += f" with id {resource_id}"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
            details={"resource": resource, "resource_id": resource_id}
        )


class RateLimitError(APIError):
    """Превышен лимит запросов"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Try again later.",
            details={"retry_after": retry_after}
        )
```

### 3.2 Создаем улучшенные обработчики

```python
# app/api/v1/handlers/common.py
from typing import Any, Dict
from fastapi import Request
from fastapi.responses import JSONResponse
import time
from uuid import uuid4

from app.api.v1.schemas.responses import ErrorResponse, MetaInfo, ErrorDetail


async def create_error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    field: str = None
) -> JSONResponse:
    """Создает стандартизированный ответ с ошибкой"""

    error_detail = ErrorDetail(
        code=error_code,
        message=message,
        details=details or {},
        field=field
    )

    # Получаем время обработки из request state если есть
    processing_time = getattr(request.state, 'processing_time', None)

    response = ErrorResponse(
        error=error_detail,
        meta=MetaInfo(
            request_id=getattr(request.state, 'request_id', str(uuid4())),
            processing_time=processing_time
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=response.dict()
    )


async def create_success_response(
    request: Request,
    data: Any,
    pagination: Dict = None
) -> JSONResponse:
    """Создает стандартизированный успешный ответ"""

    from app.api.v1.schemas.responses import SuccessResponse, PaginationInfo

    pagination_info = None
    if pagination:
        pagination_info = PaginationInfo(**pagination)

    # Получаем время обработки из request state если есть
    processing_time = getattr(request.state, 'processing_time', None)

    response = SuccessResponse(
        data=data,
        pagination=pagination_info,
        meta=MetaInfo(
            request_id=getattr(request.state, 'request_id', str(uuid4())),
            processing_time=processing_time
        )
    )

    return JSONResponse(
        status_code=200,
        content=response.dict()
    )
```

## 📋 ШАГ 4: РЕФАКТОРИНГ ОСНОВНЫХ РОУТЕРОВ

### 4.1 Улучшенный роутер комментариев

```python
# app/api/v1/routers/comments.py
"""
Улучшенный роутер комментариев с:
- Стандартизированными ответами
- Улучшенной обработкой ошибок
- Пагинацией
- Валидацией
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request

from app.core.database import get_db
from app.services.comment_service import CommentService
from app.api.v1.routers.base import BaseRouter
from app.api.v1.handlers.common import create_success_response, create_error_response
from app.api.v1.schemas.errors import ValidationError, NotFoundError


router = BaseRouter("/comments", ["Comments"])


@router.get("/")
async def get_comments(
    request: Request,
    group_id: Optional[int] = Query(None, description="ID группы VK"),
    limit: int = Query(50, ge=1, le=100, description="Количество комментариев"),
    offset: int = Query(0, ge=0, description="Смещение"),
    include_group: bool = Query(False, description="Включить информацию о группе"),
    db=Depends(get_db),
):
    """
    Получить комментарии с фильтрацией и пагинацией.

    - **group_id**: ID группы VK для фильтрации
    - **limit**: Максимальное количество комментариев (1-100)
    - **offset**: Смещение для пагинации
    - **include_group**: Включить информацию о группе в ответ
    """
    if not group_id:
        return await create_error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Parameter 'group_id' is required",
            field="group_id"
        )

    service = CommentService(db)

    try:
        # Получаем общее количество
        total = await service.get_comments_count({"group_id": group_id})

        # Получаем комментарии
        comments = await service.get_comments_paginated(
            group_id=group_id,
            limit=limit,
            offset=offset,
            include_group=include_group
        )

        # Создаем информацию о пагинации
        pagination = {
            "page": (offset // limit) + 1,
            "size": limit,
            "total": total,
            "has_next": (offset + limit) < total,
            "has_prev": offset > 0,
        }

        return await create_success_response(request, comments, pagination)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch comments: {str(e)}"
        )


@router.get("/{comment_id}")
async def get_comment(
    request: Request,
    comment_id: int,
    db=Depends(get_db),
):
    """
    Получение комментария по ID.

    - **comment_id**: ID комментария в системе
    """
    service = CommentService(db)

    try:
        comment = await service.get_comment_with_keywords(comment_id)

        if not comment:
            return await create_error_response(
                request,
                404,
                "NOT_FOUND",
                f"Comment with id {comment_id} not found",
                details={"comment_id": comment_id}
            )

        return await create_success_response(request, comment)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch comment: {str(e)}"
        )
```

### 4.2 Улучшенный роутер групп

```python
# app/api/v1/routers/groups.py
"""
Улучшенный роутер групп с:
- Стандартизированными ответами
- Улучшенной валидацией
- Пагинацией
- Error handling
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request

from app.core.database import get_db
from app.services.group_manager import GroupManager
from app.api.v1.routers.base import BaseRouter
from app.api.v1.handlers.common import create_success_response, create_error_response


router = BaseRouter("/groups", ["Groups"])


@router.get("/")
async def get_groups(
    request: Request,
    active_only: bool = Query(True, description="Только активные группы"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    limit: int = Query(50, ge=1, le=100, description="Количество групп"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db=Depends(get_db),
):
    """
    Получить список групп VK с фильтрацией и пагинацией.

    - **active_only**: Показывать только активные группы
    - **search**: Поиск по названию группы
    - **limit**: Максимальное количество групп (1-100)
    - **offset**: Смещение для пагинации
    """
    manager = GroupManager()

    try:
        # Получаем общее количество
        total = await manager.get_groups_count(db, active_only=active_only, search=search)

        # Получаем группы
        groups = await manager.get_groups_paginated(
            db=db,
            active_only=active_only,
            search=search,
            limit=limit,
            offset=offset
        )

        # Создаем информацию о пагинации
        pagination = {
            "page": (offset // limit) + 1,
            "size": limit,
            "total": total,
            "has_next": (offset + limit) < total,
            "has_prev": offset > 0,
        }

        return await create_success_response(request, groups, pagination)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch groups: {str(e)}"
        )


@router.get("/{group_id}")
async def get_group(
    request: Request,
    group_id: int,
    db=Depends(get_db),
):
    """
    Получить информацию о конкретной группе.

    - **group_id**: ID группы в системе
    """
    manager = GroupManager()

    try:
        group = await manager.get_by_id(db, group_id)

        if not group:
            return await create_error_response(
                request,
                404,
                "NOT_FOUND",
                f"Group with id {group_id} not found",
                details={"group_id": group_id}
            )

        return await create_success_response(request, group)

    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to fetch group: {str(e)}"
        )


@router.post("/")
async def create_group(
    request: Request,
    group_data: dict,  # Здесь должна быть Pydantic схема
    db=Depends(get_db),
):
    """
    Создать новую группу VK.

    - **vk_id_or_screen_name**: ID или screen_name группы VK
    - **is_active**: Активность группы
    - **max_posts_to_check**: Максимум постов для проверки
    """
    manager = GroupManager()

    try:
        group = await manager.create_group(db, group_data)
        return await create_success_response(request, group)

    except ValueError as e:
        return await create_error_response(
            request,
            400,
            "VALIDATION_ERROR",
            str(e)
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            f"Failed to create group: {str(e)}"
        )
```

## 📋 ШАГ 5: ОБНОВЛЕНИЕ ГЛАВНОГО РОУТЕРА

### 5.1 Обновленный главный роутер

```python
# app/api/v1/api.py
"""
Главный роутер API v1 для VK Comments Parser
с улучшенной архитектурой и middleware
"""

from typing import Dict, Any
from fastapi import APIRouter

# Импорт улучшенных роутеров
from app.api.v1.routers.comments import router as comments_router
from app.api.v1.routers.groups import router as groups_router
from app.api.v1.routers.keywords import router as keywords_router
from app.api.v1.routers.parser import router as parser_router

# Импорт старых роутеров (пока оставляем для совместимости)
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.morphological import router as morphological_router
from app.api.v1.errors import router as errors_router
from app.api.v1.settings import router as settings_router
from app.api.v1.health import router as health_router

# Создаем главный роутер с метаданными
api_router = APIRouter(
    prefix="",
    tags=["API v1"],
    responses={
        404: {"description": "Endpoint not found"},
        500: {"description": "Internal server error"},
    },
)

# Подключаем улучшенные роутеры
api_router.include_router(comments_router, tags=["Comments"])
api_router.include_router(groups_router, tags=["Groups"])
api_router.include_router(keywords_router, tags=["Keywords"])
api_router.include_router(parser_router, tags=["Parser"])

# Подключаем остальные роутеры (пока без изменений)
api_router.include_router(monitoring_router, tags=["Monitoring"])
api_router.include_router(morphological_router, tags=["Morphological"])
api_router.include_router(errors_router, tags=["Errors"])
api_router.include_router(settings_router, tags=["Settings"])
api_router.include_router(health_router, tags=["Health"])


@api_router.get("/")
async def api_info() -> Dict[str, Any]:
    """Информация об API v1.5.0 с улучшениями"""
    return {
        "service": "VK Comments Parser API",
        "version": "v1.5.0",
        "description": "🚀 Улучшенная версия API v1 с middleware и стандартизацией",
        "status": "✅ API улучшен - добавлены middleware, стандартизированные ответы",
        "features": [
            "🛡️ Rate limiting для защиты от перегрузок",
            "📊 Структурированное логирование запросов",
            "🎯 Стандартизированные ответы и ошибки",
            "⚡ Улучшенная производительность",
            "🔍 Детальная информация о запросах",
            "📝 Полная документация API",
        ],
        "improvements": [
            "Rate Limiting Middleware",
            "Request Logging Middleware",
            "Standardized Response Format",
            "Enhanced Error Handling",
            "Request ID Tracking",
            "Performance Monitoring"
        ],
        "endpoints": {
            "comments": "/api/v1/comments",
            "groups": "/api/v1/groups",
            "keywords": "/api/v1/keywords",
            "parser": "/api/v1/parser",
            "monitoring": "/api/v1/monitoring",
            "morphological": "/api/v1/morphological",
            "errors": "/api/v1/errors",
            "settings": "/api/v1/settings",
            "health": "/api/v1/health"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "health_check": "/api/v1/health",
        "changelog": "Улучшена обработка ошибок, добавлены middleware"
    }
```

## 📋 ШАГ 6: ОБНОВЛЕНИЕ MAIN.PY

### 6.1 Добавление middleware

```python
# app/main.py
"""
Production-ready FastAPI приложение для VK Comments Parser
с улучшенной архитектурой и middleware
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импорт API роутеров
from app.api.v1.api import api_router as api_v1_router

# Импорт middleware
from app.api.v1.middleware.rate_limit import SimpleRateLimitMiddleware
from app.api.v1.middleware.logging import RequestLoggingMiddleware

from app.core.config import settings
from app.core.database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production-ready lifespan с полной инициализацией"""
    logger.info("🚀 Запуск VK Comments Parser v1.5.0...")

    # Инициализируем базу данных
    try:
        await init_db()
        logger.info("📊 База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise

    logger.info("✅ Система готова к работе!")
    logger.info("📋 API v1.5.0 доступен: /api/v1")
    logger.info("📚 Документация: /docs")

    yield

    logger.info("🛑 Остановка VK Comments Parser...")


# Создание FastAPI приложения
app = FastAPI(
    title="VK Comments Parser API",
    version="1.5.0",
    description="""
    🚀 **Улучшенная версия VK Comments Parser API**

    ## ✨ Новые возможности v1.5.0:
    - 🛡️ **Rate Limiting** - защита от перегрузок
    - 📊 **Request Logging** - структурированное логирование
    - 🎯 **Standardized Responses** - унифицированные ответы
    - ⚡ **Performance Monitoring** - отслеживание производительности
    - 🔍 **Request Tracking** - отслеживание запросов по ID

    ## 📚 API Endpoints:
    - **Comments**: `/api/v1/comments` - работа с комментариями
    - **Groups**: `/api/v1/groups` - управление группами VK
    - **Keywords**: `/api/v1/keywords` - ключевые слова
    - **Parser**: `/api/v1/parser` - парсинг данных
    - **Health**: `/api/v1/health` - проверка здоровья системы

    ## 🔧 Улучшения:
    - Стандартизированные ответы с метаданными
    - Улучшенная обработка ошибок
    - Rate limiting для защиты от DDoS
    - Структурированное логирование всех запросов
    - Request ID tracking для отладки
    - Performance monitoring headers

    ## 📖 Документация:
    - **Swagger UI**: `/docs`
    - **ReDoc**: `/redoc`
    - **OpenAPI**: `/openapi.json`
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# 🛡️ Middleware (добавляем в правильном порядке)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Добавляем наше middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SimpleRateLimitMiddleware, requests_per_minute=60)


# Подключаем API роутеры
app.include_router(api_v1_router, prefix="/api/v1")


# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
```

## 📋 ШАГ 7: ТЕСТИРОВАНИЕ

### 7.1 Запуск тестов

```bash
# Запуск интеграционных тестов
cd /opt/app/backend && python -m pytest tests/integration/ -v

# Запуск с покрытием
python -m pytest tests/integration/ --cov=app --cov-report=html

# Запуск конкретного теста
python -m pytest tests/integration/test_api_integration.py::TestAPIIntegration::test_api_root_endpoint -v
```

### 7.2 Проверка работы API

```bash
# Проверка основного endpoint
curl http://localhost:8000/api/v1/

# Проверка health check
curl http://localhost:8000/api/v1/health

# Проверка rate limiting (сделать много запросов)
for i in {1..70}; do curl -s http://localhost:8000/api/v1/health; done

# Проверка логирования (посмотреть логи)
tail -f logs/app.log
```

## 🎯 РЕЗУЛЬТАТ

После выполнения всех шагов вы получите:

### ✅ **Что будет улучшено:**
1. **Производительность** - кэширование и оптимизация запросов
2. **Безопасность** - rate limiting и улучшенная валидация
3. **Наблюдаемость** - структурированное логирование и метрики
4. **Качество** - стандартизированные ответы и ошибки
5. **Совместимость** - 100% backward compatibility

### ✅ **Новые возможности:**
- Rate limiting для защиты от DDoS
- Структурированное логирование всех запросов
- Стандартизированные ответы с метаданными
- Request ID tracking для отладки
- Performance monitoring headers
- Улучшенная обработка ошибок

### ✅ **Сохраненная совместимость:**
- Все существующие endpoints работают без изменений
- API контракты не нарушены
- Клиентские приложения не требуют обновления
- Данные остаются в том же формате

---

## 🚀 ГОТОВО К РЕАЛИЗАЦИИ!

**Этот план позволяет улучшить API v1 без риска поломать существующие интеграции, добавив современные возможности enterprise-grade приложений.**

**Начать можно с любого шага - они независимы и могут выполняться параллельно!** 🎉
