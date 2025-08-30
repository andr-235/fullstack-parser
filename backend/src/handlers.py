"""
Enterprise-grade обработчики для создания стандартизированных ответов с DDD архитектурой

Этот модуль содержит обработчики для создания унифицированных ответов API,
полностью интегрированных с DDD архитектурой и enterprise-grade системами.
"""

from typing import Any, Dict, Optional, List
from fastapi import Request
from fastapi.responses import JSONResponse
import time
from uuid import uuid4

from .responses import (
    ErrorResponse,
    SuccessResponse,
    MetaInfo,
    ErrorDetail,
    PaginationInfo,
    HealthStatusResponse,
    ValidationResponse,
    StatisticsResponse,
)


async def create_error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    field: Optional[str] = None,
    suggestions: Optional[List[str]] = None,
) -> JSONResponse:
    """
    Создает стандартизированный ответ с ошибкой с DDD интеграцией

    Args:
        request: FastAPI Request объект
        status_code: HTTP статус код ошибки
        error_code: Код ошибки для программной обработки
        message: Человеко-читаемое сообщение об ошибке
        details: Дополнительные детали ошибки
        field: Поле, вызвавшее ошибку (для валидации)
        suggestions: Предложения по исправлению ошибки

    Returns:
        JSONResponse: Стандартизированный ответ с ошибкой
    """
    # Параметр suggestions не поддерживается схемой ErrorDetail напрямую,
    # передаем его в details, чтобы сохранить подсказки и удовлетворить mypy
    extra_details = {**(details or {})}
    if suggestions:
        extra_details["suggestions"] = suggestions

    error_detail = ErrorDetail(
        code=error_code,
        message=message,
        details=extra_details,
        field=field,
    )

    # Получаем время обработки из request state если есть
    processing_time = getattr(request.state, "processing_time", None)
    request_id = getattr(request.state, "request_id", str(uuid4()))

    response = ErrorResponse(
        error=error_detail,
        meta=MetaInfo(
            request_id=request_id,
            processing_time=processing_time,
        ),
    )

    return JSONResponse(status_code=status_code, content=response.dict())


async def create_success_response(
    request: Request,
    data: Any,
    pagination: Optional[Dict] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Создает стандартизированный успешный ответ с DDD интеграцией

    Args:
        request: FastAPI Request объект
        data: Основные данные ответа
        pagination: Информация о пагинации (если применимо)
        meta: Дополнительная мета-информация

    Returns:
        JSONResponse: Стандартизированный успешный ответ
    """
    pagination_info = None
    if pagination:
        pagination_info = PaginationInfo(**pagination)

    # Получаем время обработки из request state если есть
    processing_time = getattr(request.state, "processing_time", None)
    request_id = getattr(request.state, "request_id", str(uuid4()))

    # Создаем мета-информацию
    meta_info = MetaInfo(
        request_id=request_id,
        processing_time=processing_time,
    )

    # Обновляем мета-информацию если переданы дополнительные данные
    if meta:
        for key, value in meta.items():
            if hasattr(meta_info, key):
                setattr(meta_info, key, value)

    response = SuccessResponse(
        data=data,
        pagination=pagination_info,
        meta=meta_info,
    )

    return JSONResponse(status_code=200, content=response.dict())


async def create_health_response(
    request: Request,
    health_data: Dict[str, Any],
) -> JSONResponse:
    """
    Создает ответ со статусом здоровья системы

    Args:
        request: FastAPI Request объект
        health_data: Данные о здоровье системы

    Returns:
        JSONResponse: Ответ со статусом здоровья
    """
    health_response = HealthStatusResponse(
        status=health_data.get("status", "unknown"),
        service=health_data.get("service", "vk-comments-parser"),
        version=health_data.get("version", "v1.6.0"),
        components=health_data.get("components", {}),
        uptime_seconds=health_data.get("uptime_seconds"),
        meta=MetaInfo(
            request_id=getattr(request.state, "request_id", str(uuid4())),
            processing_time=getattr(request.state, "processing_time", None),
        ),
    )

    status_code = 200 if health_data.get("status") == "healthy" else 503
    return JSONResponse(
        status_code=status_code, content=health_response.dict()
    )


async def create_validation_response(
    request: Request,
    validation_data: Dict[str, Any],
) -> JSONResponse:
    """
    Создает ответ валидации с детальной информацией

    Args:
        request: FastAPI Request объект
        validation_data: Данные валидации

    Returns:
        JSONResponse: Ответ валидации
    """
    validation_response = ValidationResponse(
        valid=validation_data.get("valid", False),
        issues=validation_data.get("issues", {}),
        total_sections=validation_data.get("total_sections", 0),
        sections_with_issues=validation_data.get("sections_with_issues", 0),
        meta=MetaInfo(
            request_id=getattr(request.state, "request_id", str(uuid4())),
            processing_time=getattr(request.state, "processing_time", None),
        ),
    )

    status_code = 200 if validation_data.get("valid") else 400
    return JSONResponse(
        status_code=status_code, content=validation_response.dict()
    )


async def create_statistics_response(
    request: Request,
    stats_data: Dict[str, Any],
) -> JSONResponse:
    """
    Создает ответ со статистикой системы

    Args:
        request: FastAPI Request объект
        stats_data: Статистические данные

    Returns:
        JSONResponse: Ответ со статистикой
    """
    stats_response = StatisticsResponse(
        period_days=stats_data.get("period_days", 7),
        total_reports=stats_data.get("total_reports", 0),
        acknowledged_reports=stats_data.get("acknowledged_reports", 0),
        resolved_reports=stats_data.get("resolved_reports", 0),
        critical_reports=stats_data.get("critical_reports", 0),
        acknowledgment_rate=stats_data.get("acknowledgment_rate", 0.0),
        resolution_rate=stats_data.get("resolution_rate", 0.0),
        error_types_stats=stats_data.get("error_types_stats", {}),
        severity_stats=stats_data.get("severity_stats", {}),
        operation_stats=stats_data.get("operation_stats", {}),
        meta=MetaInfo(
            request_id=getattr(request.state, "request_id", str(uuid4())),
            processing_time=getattr(request.state, "processing_time", None),
        ),
    )

    return JSONResponse(status_code=200, content=stats_response.dict())


def create_pagination_info(
    page: int,
    size: int,
    total: int,
    has_next: Optional[bool] = None,
    has_prev: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Создает информацию о пагинации

    Args:
        page: Текущий номер страницы
        size: Размер страницы
        total: Общее количество элементов
        has_next: Есть ли следующая страница (автоматически если None)
        has_prev: Есть ли предыдущая страница (автоматически если None)

    Returns:
        Dict[str, Any]: Информация о пагинации
    """
    if has_next is None:
        has_next = page * size < total
    if has_prev is None:
        has_prev = page > 1

    total_pages = (total + size - 1) // size if total > 0 else 1

    return {
        "page": page,
        "size": size,
        "total": total,
        "has_next": has_next,
        "has_prev": has_prev,
        "total_pages": total_pages,
    }


async def create_empty_success_response(
    request: Request,
    message: str = "Операция выполнена успешно",
) -> JSONResponse:
    """
    Создает пустой успешный ответ

    Args:
        request: FastAPI Request объект
        message: Сообщение об успешном выполнении

    Returns:
        JSONResponse: Пустой успешный ответ
    """
    return await create_success_response(
        request, None, meta={"message": message}
    )
