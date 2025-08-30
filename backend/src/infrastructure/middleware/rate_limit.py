"""
Enterprise-grade Rate Limiting Middleware для API v1 с DDD архитектурой

Этот модуль реализует продвинутый rate limiting с интеграцией
в DDD архитектуру и enterprise-grade error handling.
"""

import time
from collections import defaultdict
from typing import Dict, Any, Optional, List
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ...exceptions import create_rate_limit_error


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Продвинутый Rate Limiting Middleware с DDD интеграцией

    Реализует защиту от перегрузок с enterprise-grade error handling,
    интеграцией с request tracking и стандартизированными ответами.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        window_seconds: int = 60,
        burst_limit: Optional[int] = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.burst_limit = burst_limit or requests_per_minute * 2
        # История запросов по IP: список меток времени запросов
        self.requests: Dict[str, List[float]] = defaultdict(list)

        # Статистика для мониторинга
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "active_clients": 0,
        }

    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с rate limiting"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Обновляем статистику
        self.stats["total_requests"] += 1
        self.stats["active_clients"] = len(self.requests)

        # Очищаем старые запросы для этого клиента
        self._cleanup_old_requests(client_ip, current_time)

        # Проверяем burst limit (короткие всплески)
        if len(self.requests[client_ip]) >= self.burst_limit:
            return await self._create_rate_limit_response(
                request, client_ip, len(self.requests[client_ip]), "burst"
            )

        # Проверяем основной rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return await self._create_rate_limit_response(
                request, client_ip, len(self.requests[client_ip]), "sustained"
            )

        # Добавляем текущий запрос
        self.requests[client_ip].append(current_time)

        # Устанавливаем заголовки с информацией о лимите
        response = await call_next(request)
        await self._add_rate_limit_headers(response, client_ip)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Получить IP адрес клиента с учетом прокси"""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Берем первый IP из списка
            return forwarded_for.split(",")[0].strip()

        # Проверяем другие заголовки прокси
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Используем client.host как fallback
        return request.client.host if request.client else "unknown"

    def _cleanup_old_requests(
        self, client_ip: str, current_time: float
    ) -> None:
        """Очистить старые запросы для клиента"""
        self.requests[client_ip] = [
            req_time
            for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]

    async def _create_rate_limit_response(
        self,
        request: Request,
        client_ip: str,
        request_count: int,
        limit_type: str,
    ) -> JSONResponse:
        """Создать стандартизированный ответ с rate limit ошибкой"""
        # Обновляем статистику блокировки
        self.stats["blocked_requests"] += 1

        # Создаем ошибку с enterprise-grade информацией
        rate_limit_error = create_rate_limit_error(
            retry_after=self.window_seconds,
            client_ip=client_ip,
        )

        # Обогащаем детали ошибки дополнительными полями
        error_details = rate_limit_error.to_dict()
        error_details["request_count"] = request_count
        error_details["limit_type"] = limit_type

        # Создаем стандартизированный ответ
        from ...handlers import create_error_response

        return await create_error_response(
            request,
            rate_limit_error.status_code,
            rate_limit_error.error_code,
            rate_limit_error.detail,
            error_details,
        )

    async def _add_rate_limit_headers(self, response, client_ip: str) -> None:
        """Добавить заголовки с информацией о rate limit"""
        current_count = len(self.requests[client_ip])

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.requests_per_minute - current_count)
        )
        response.headers["X-RateLimit-Reset"] = str(self.window_seconds)

        # Добавляем burst limit информацию
        response.headers["X-RateLimit-Burst-Limit"] = str(self.burst_limit)
        response.headers["X-RateLimit-Burst-Remaining"] = str(
            max(0, self.burst_limit - current_count)
        )

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику middleware"""
        return {
            **self.stats,
            "window_seconds": self.window_seconds,
            "requests_per_minute": self.requests_per_minute,
            "burst_limit": self.burst_limit,
            "clients_count": len(self.requests),
        }

    def reset_stats(self) -> None:
        """Сбросить статистику"""
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "active_clients": 0,
        }

    def cleanup_inactive_clients(self, max_age_seconds: int = 3600) -> int:
        """Очистить неактивных клиентов"""
        current_time = time.time()
        clients_before = len(self.requests)

        self.requests = {
            client_ip: req_times
            for client_ip, req_times in self.requests.items()
            if req_times and (current_time - max(req_times)) < max_age_seconds
        }

        clients_after = len(self.requests)
        return clients_before - clients_after
