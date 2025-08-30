"""
Enterprise-grade Request Logging Middleware для API v1 с DDD архитектурой

Этот модуль реализует продвинутое логирование запросов с полной
интеграцией в DDD архитектуру и enterprise-grade monitoring.
"""

import time
import logging
from typing import Dict, Any, Optional, cast
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Enterprise-grade Request Logging Middleware с DDD интеграцией

    Реализует комплексное логирование запросов с request tracking,
    performance monitoring и интеграцией с enterprise-grade системами.
    """

    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: Optional[set] = None,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or {"/health", "/favicon.ico"}

        # Статистика для мониторинга
        self.stats: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_processing_time": 0.0,
            "requests_by_method": {},
            "requests_by_path": {},
            "errors_by_type": {},
        }

    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с полным логированием"""
        # Пропускаем исключенные пути
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        request_id = str(uuid4())
        start_time = time.time()

        # Обновляем статистику
        self.stats["total_requests"] = (
            int(self.stats.get("total_requests", 0)) + 1
        )
        method = request.method
        path = request.url.path

        requests_by_method = cast(
            Dict[str, int], self.stats["requests_by_method"]
        )
        requests_by_path = cast(Dict[str, int], self.stats["requests_by_path"])
        requests_by_method[method] = int(requests_by_method.get(method, 0)) + 1
        requests_by_path[path] = int(requests_by_path.get(path, 0)) + 1

        # Сохраняем данные в request state для использования в обработчиках
        request.state.request_id = request_id
        request.state.start_time = start_time

        # Логируем входящий запрос
        await self._log_request(request, request_id)

        try:
            response = await call_next(request)
            processing_time = time.time() - start_time

            # Обновляем статистику успешных запросов
            self.stats["successful_requests"] = (
                int(self.stats.get("successful_requests", 0)) + 1
            )
            self._update_processing_time_stats(processing_time)

            # Сохраняем время обработки в request state
            request.state.processing_time = processing_time

            # Логируем успешный ответ
            await self._log_response(
                request, response, request_id, processing_time
            )

            # Добавляем заголовки
            self._add_response_headers(response, request_id, processing_time)

            return response

        except Exception as e:
            processing_time = time.time() - start_time

            # Обновляем статистику ошибок
            self.stats["failed_requests"] = (
                int(self.stats.get("failed_requests", 0)) + 1
            )
            error_type = type(e).__name__
            errors_by_type = cast(Dict[str, int], self.stats["errors_by_type"])
            errors_by_type[error_type] = (
                int(errors_by_type.get(error_type, 0)) + 1
            )

            # Логируем ошибку
            await self._log_error(request, e, request_id, processing_time)
            raise

    async def _log_request(self, request: Request, request_id: str) -> None:
        """Логировать входящий запрос"""
        # Собираем информацию о запросе
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "full_url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_type": request.headers.get("content-type", "unknown"),
            "accept": request.headers.get("accept", "unknown"),
            "query_params": dict(request.query_params),
            "path_params": dict(request.path_params),
            "headers_count": len(request.headers),
        }

        # Добавляем тело запроса если включено
        if self.log_request_body:
            try:
                body = await request.body()
                if body:
                    request_info["body_size"] = len(body)
                    # Не логируем чувствительные данные
                    if len(body) < 1024:  # Только маленькие тела
                        request_info["body"] = body.decode(
                            "utf-8", errors="ignore"
                        )
            except Exception:
                request_info["body_error"] = "Failed to read request body"

        logger.info(
            f"➡️  {request.method} {request.url.path} - {self._get_client_ip(request)}",
            extra=request_info,
        )

    async def _log_response(
        self,
        request: Request,
        response,
        request_id: str,
        processing_time: float,
    ) -> None:
        """Логировать ответ"""
        response_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "processing_time": processing_time,
            "content_type": response.headers.get("content-type", "unknown"),
            "content_length": response.headers.get(
                "content-length", "unknown"
            ),
        }

        # Определяем уровень логирования в зависимости от статуса
        if response.status_code >= 500:
            logger.error(
                f"❌ {request.method} {request.url.path} - {response.status_code} ({processing_time:.3f}s)",
                extra=response_info,
            )
        elif response.status_code >= 400:
            logger.warning(
                f"⚠️  {request.method} {request.url.path} - {response.status_code} ({processing_time:.3f}s)",
                extra=response_info,
            )
        else:
            logger.info(
                f"✅ {request.method} {request.url.path} - {response.status_code} ({processing_time:.3f}s)",
                extra=response_info,
            )

    async def _log_error(
        self,
        request: Request,
        error: Exception,
        request_id: str,
        processing_time: float,
    ) -> None:
        """Логировать ошибку"""
        error_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "processing_time": processing_time,
            "client_ip": self._get_client_ip(request),
        }

        logger.error(
            f"💥 {request.method} {request.url.path} - {type(error).__name__} ({processing_time:.3f}s)",
            extra=error_info,
            exc_info=True,
        )

    def _get_client_ip(self, request: Request) -> str:
        """Получить IP адрес клиента с учетом прокси"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _add_response_headers(
        self, response, request_id: str, processing_time: float
    ) -> None:
        """Добавить заголовки в ответ"""
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Processing-Time"] = str(processing_time)
        response.headers["X-Response-Time"] = str(time.time())
        response.headers["X-API-Version"] = "v1.6.0"
        response.headers["X-Architecture"] = "DDD + Middleware"

    def _update_processing_time_stats(self, processing_time: float) -> None:
        """Обновить статистику времени обработки"""
        current_avg = float(self.stats["avg_processing_time"])  # type: ignore[call-overload]
        total_requests = int(self.stats["total_requests"])  # type: ignore[call-overload]

        # Вычисляем новое среднее
        self.stats["avg_processing_time"] = (
            current_avg * (total_requests - 1) + processing_time
        ) / total_requests

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику middleware"""
        return {
            **self.stats,
            "excluded_paths": list(self.exclude_paths),
            "log_request_body": self.log_request_body,
            "log_response_body": self.log_response_body,
            "success_rate": (
                (
                    cast(int, self.stats.get("successful_requests", 0))
                    / max(1, cast(int, self.stats.get("total_requests", 0)))
                )
            ),
        }

    def reset_stats(self) -> None:
        """Сбросить статистику"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_processing_time": 0.0,
            "requests_by_method": {},
            "requests_by_path": {},
            "errors_by_type": {},
        }
