"""
Middleware для структурированного логирования HTTP-запросов.
"""

import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

# Контекстные переменные для request_id
request_id_var = structlog.contextvars.bind_contextvars

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования входящих HTTP-запросов.
    - Генерирует уникальный request_id для каждого запроса.
    - Логирует начало и конец обработки запроса.
    - Добавляет request_id в контекст лога для всех последующих записей.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())

        # Биндим request_id к контексту на время жизни запроса
        request_id_var(request_id=request_id)

        start_time = time.time()

        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id

            logger.info(
                "Request finished",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=round(process_time, 4),
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(
                "Request failed with exception",
                method=request.method,
                path=request.url.path,
                process_time=round(process_time, 4),
            )
            raise e
