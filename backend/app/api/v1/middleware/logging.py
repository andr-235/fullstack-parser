"""
Middleware для логирования запросов с request ID tracking
"""

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

        # Сохраняем request_id в request state для использования в обработчиках
        request.state.request_id = request_id

        # Логируем входящий запрос
        logger.info(
            f"➡️  {request.method} {request.url.path} - {request.client.host}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "query_params": dict(request.query_params),
            },
        )

        try:
            response = await call_next(request)
            processing_time = time.time() - start_time

            # Сохраняем время обработки в request state
            request.state.processing_time = processing_time

            # Логируем успешный ответ
            logger.info(
                f"✅ {request.method} {request.url.path} - {response.status_code} ({processing_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "processing_time": processing_time,
                },
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
                    "processing_time": processing_time,
                },
                exc_info=True,
            )
            raise
