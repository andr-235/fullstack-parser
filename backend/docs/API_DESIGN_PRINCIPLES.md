# API Design Principles

## Текущие проблемы

- Непоследовательные URL patterns
- Отсутствует стандартизация ответов
- Слабая документация API
- Нет четких контрактов
- Отсутствует валидация на уровне API

## Рекомендации

### 1. RESTful Design

```python
# src/api/design/restful_patterns.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

class RESTfulRouter:
    """Базовый класс для RESTful роутеров"""

    def __init__(self, prefix: str, tags: List[str]):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._setup_standard_routes()

    def _setup_standard_routes(self):
        """Стандартные REST endpoints"""

        @self.router.get("/", response_model=List[BaseModel])
        async def list_resources(
            skip: int = 0,
            limit: int = 100,
            search: Optional[str] = None
        ):
            """GET /resources - Список ресурсов"""
            pass

        @self.router.get("/{resource_id}", response_model=BaseModel)
        async def get_resource(resource_id: int):
            """GET /resources/{id} - Получить ресурс"""
            pass

        @self.router.post("/", response_model=BaseModel, status_code=201)
        async def create_resource(resource: BaseModel):
            """POST /resources - Создать ресурс"""
            pass

        @self.router.put("/{resource_id}", response_model=BaseModel)
        async def update_resource(resource_id: int, resource: BaseModel):
            """PUT /resources/{id} - Обновить ресурс"""
            pass

        @self.router.patch("/{resource_id}", response_model=BaseModel)
        async def partial_update_resource(resource_id: int, resource: BaseModel):
            """PATCH /resources/{id} - Частичное обновление"""
            pass

        @self.router.delete("/{resource_id}", status_code=204)
        async def delete_resource(resource_id: int):
            """DELETE /resources/{id} - Удалить ресурс"""
            pass
```

### 2. Consistent Response Format

```python
# src/api/design/response_models.py
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class StandardResponse(BaseModel):
    """Стандартный формат ответа API"""

    status: ResponseStatus = Field(..., description="Статус ответа")
    data: Optional[Any] = Field(None, description="Основные данные")
    message: Optional[str] = Field(None, description="Сообщение")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Ошибки")
    meta: Optional[Dict[str, Any]] = Field(None, description="Метаданные")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="ID запроса")

class PaginatedResponse(StandardResponse):
    """Ответ с пагинацией"""

    pagination: Optional[Dict[str, Any]] = Field(None, description="Информация о пагинации")

    @classmethod
    def create_paginated(
        cls,
        data: List[Any],
        page: int,
        size: int,
        total: int,
        **kwargs
    ):
        return cls(
            data=data,
            pagination={
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size,
                "has_next": page * size < total,
                "has_prev": page > 1
            },
            **kwargs
        )
```

### 3. Input Validation

```python
# src/api/design/validation.py
from pydantic import BaseModel, validator, Field
from typing import Any, Optional, List
import re
from datetime import datetime

class BaseAPIRequest(BaseModel):
    """Базовая модель для API запросов"""

    class Config:
        # Запрет на дополнительные поля
        extra = "forbid"
        # Валидация при присваивании
        validate_assignment = True
        # Использование enum значений
        use_enum_values = True

class PaginationParams(BaseAPIRequest):
    """Параметры пагинации"""

    page: int = Field(1, ge=1, le=10000, description="Номер страницы")
    size: int = Field(20, ge=1, le=1000, description="Размер страницы")
    sort: Optional[str] = Field(None, description="Поле для сортировки")
    order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="Направление сортировки")

    @validator('sort')
    def validate_sort_field(cls, v):
        if v and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError('Invalid sort field name')
        return v

class SearchParams(BaseAPIRequest):
    """Параметры поиска"""

    q: Optional[str] = Field(None, min_length=1, max_length=255, description="Поисковый запрос")
    filters: Optional[Dict[str, Any]] = Field(None, description="Фильтры")
    date_from: Optional[datetime] = Field(None, description="Дата начала")
    date_to: Optional[datetime] = Field(None, description="Дата окончания")

    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v and 'date_from' in values and values['date_from'] and v < values['date_from']:
            raise ValueError('date_to must be after date_from')
        return v

class VKIDValidator(BaseAPIRequest):
    """Валидатор VK ID"""

    vk_id: int = Field(..., ge=1, le=2**31-1, description="VK ID")

    @validator('vk_id')
    def validate_vk_id(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ValueError('VK ID must be positive integer')
        return v
```

### 4. Error Handling Standards

```python
# src/api/design/error_handling.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging

class APIErrorHandler:
    """Централизованная обработка ошибок API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Создание стандартизированного ответа с ошибкой"""

        error_data = {
            "status": "error",
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            },
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }

        return JSONResponse(
            status_code=status_code,
            content=error_data
        )

    def handle_validation_error(self, exc: Exception, request: Request) -> JSONResponse:
        """Обработка ошибок валидации"""
        self.logger.warning(f"Validation error: {exc}")

        return self.create_error_response(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Invalid input data",
            details={"validation_errors": str(exc)},
            request_id=getattr(request.state, 'request_id', None)
        )

    def handle_not_found(self, resource: str, resource_id: Any, request: Request) -> JSONResponse:
        """Обработка ошибки 'не найдено'"""
        return self.create_error_response(
            status_code=404,
            error_code="NOT_FOUND",
            message=f"{resource} not found",
            details={"resource": resource, "resource_id": str(resource_id)},
            request_id=getattr(request.state, 'request_id', None)
        )

    def handle_internal_error(self, exc: Exception, request: Request) -> JSONResponse:
        """Обработка внутренних ошибок"""
        self.logger.error(f"Internal error: {exc}", exc_info=True)

        return self.create_error_response(
            status_code=500,
            error_code="INTERNAL_ERROR",
            message="Internal server error",
            request_id=getattr(request.state, 'request_id', None)
        )
```

### 5. API Documentation Standards

```python
# src/api/design/documentation.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

class APIDocumentation:
    """Управление документацией API"""

    def __init__(self, app: FastAPI):
        self.app = app
        self._setup_documentation()

    def _setup_documentation(self):
        """Настройка документации"""

        # Кастомная OpenAPI схема
        def custom_openapi():
            if self.app.openapi_schema:
                return self.app.openapi_schema

            openapi_schema = get_openapi(
                title="VK Parser API",
                version="1.7.0",
                description="""
                ## VK Comments Parser API

                Enterprise-grade API для парсинга и анализа комментариев VK.

                ### Основные возможности:
                - 🔐 Аутентификация и авторизация
                - 📊 Парсинг комментариев VK
                - 🏷️ Управление группами
                - 🔍 Морфологический анализ
                - 📈 Аналитика и отчеты

                ### Аутентификация:
                API использует JWT токены. Получите токен через `/auth/login`.

                ### Rate Limiting:
                - 100 запросов в минуту для обычных пользователей
                - 1000 запросов в минуту для премиум пользователей

                ### Коды ответов:
                - `200` - Успешный запрос
                - `201` - Ресурс создан
                - `400` - Некорректный запрос
                - `401` - Не авторизован
                - `403` - Доступ запрещен
                - `404` - Ресурс не найден
                - `422` - Ошибка валидации
                - `429` - Превышен лимит запросов
                - `500` - Внутренняя ошибка сервера
                """,
                routes=self.app.routes,
            )

            # Добавляем кастомные теги
            openapi_schema["tags"] = [
                {
                    "name": "Authentication",
                    "description": "Аутентификация и управление пользователями"
                },
                {
                    "name": "Comments",
                    "description": "Работа с комментариями VK"
                },
                {
                    "name": "Groups",
                    "description": "Управление группами VK"
                },
                {
                    "name": "Parser",
                    "description": "Парсинг данных VK"
                },
                {
                    "name": "Analytics",
                    "description": "Аналитика и отчеты"
                },
                {
                    "name": "Health",
                    "description": "Мониторинг состояния системы"
                }
            ]

            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema

        self.app.openapi = custom_openapi

    def add_example_responses(self, endpoint_func, examples: Dict[str, Any]):
        """Добавление примеров ответов к endpoint"""
        if not hasattr(endpoint_func, 'responses'):
            endpoint_func.responses = {}

        for status_code, example in examples.items():
            endpoint_func.responses[status_code] = {
                "description": example.get("description", ""),
                "content": {
                    "application/json": {
                        "example": example.get("content")
                    }
                }
            }
```

### 6. API Versioning Strategy

```python
# src/api/design/versioning.py
from fastapi import APIRouter, Depends, Header
from typing import Optional
from enum import Enum

class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"

class VersionManager:
    """Управление версиями API"""

    def __init__(self):
        self.supported_versions = [APIVersion.V1, APIVersion.V2]
        self.current_version = APIVersion.V2
        self.deprecated_versions = [APIVersion.V1]

    def get_version_from_header(self, x_api_version: Optional[str] = Header(None)) -> APIVersion:
        """Получение версии из заголовка"""
        if not x_api_version:
            return self.current_version

        try:
            version = APIVersion(x_api_version)
            if version not in self.supported_versions:
                raise ValueError(f"Unsupported version: {version}")
            return version
        except ValueError:
            return self.current_version

    def get_version_from_url(self, path: str) -> Optional[APIVersion]:
        """Получение версии из URL"""
        for version in APIVersion:
            if f"/{version.value}/" in path:
                return version
        return None

    def create_versioned_router(self, version: APIVersion, prefix: str, tags: List[str]) -> APIRouter:
        """Создание версионированного роутера"""
        router = APIRouter(prefix=f"/api/{version.value}{prefix}", tags=tags)

        # Добавляем информацию о версии в метаданные
        router.extra["version"] = version.value
        router.extra["deprecated"] = version in self.deprecated_versions

        return router
```

### 7. Request/Response Middleware

```python
# src/api/design/middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import json
from typing import Callable

class APIMiddleware(BaseHTTPMiddleware):
    """Middleware для стандартизации API"""

    def __init__(self, app, enable_logging: bool = True):
        super().__init__(app)
        self.enable_logging = enable_logging

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Генерируем request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Логируем начало запроса
        start_time = time.time()

        if self.enable_logging:
            self._log_request_start(request, request_id)

        # Обрабатываем запрос
        response = await call_next(request)

        # Логируем завершение запроса
        process_time = time.time() - start_time

        if self.enable_logging:
            self._log_request_end(request, response, process_time, request_id)

        # Добавляем заголовки
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response

    def _log_request_start(self, request: Request, request_id: str):
        """Логирование начала запроса"""
        print(f"[{request_id}] {request.method} {request.url}")

    def _log_request_end(self, request: Request, response: Response,
                        process_time: float, request_id: str):
        """Логирование завершения запроса"""
        print(f"[{request_id}] {response.status_code} - {process_time:.3f}s")
```

## Implementation Checklist

### Immediate (Week 1)

- [ ] Стандартизировать формат ответов
- [ ] Внедрить базовую валидацию
- [ ] Настроить error handling
- [ ] Добавить request ID tracking

### Short-term (Month 1)

- [ ] Реализовать RESTful patterns
- [ ] Настроить API versioning
- [ ] Улучшить документацию
- [ ] Добавить middleware

### Medium-term (Month 2-3)

- [ ] Внедрить advanced validation
- [ ] Настроить API testing
- [ ] Добавить performance monitoring
- [ ] Реализовать API analytics
