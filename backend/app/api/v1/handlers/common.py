"""
Общие обработчики для создания стандартизированных ответов
"""

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
    field: str = None,
) -> JSONResponse:
    """Создает стандартизированный ответ с ошибкой"""

    error_detail = ErrorDetail(
        code=error_code, message=message, details=details or {}, field=field
    )

    # Получаем время обработки из request state если есть
    processing_time = getattr(request.state, "processing_time", None)

    response = ErrorResponse(
        error=error_detail,
        meta=MetaInfo(
            request_id=getattr(request.state, "request_id", str(uuid4())),
            processing_time=processing_time,
        ),
    )

    return JSONResponse(status_code=status_code, content=response.dict())


async def create_success_response(
    request: Request, data: Any, pagination: Dict = None
) -> JSONResponse:
    """Создает стандартизированный успешный ответ"""

    from app.api.v1.schemas.responses import SuccessResponse, PaginationInfo

    pagination_info = None
    if pagination:
        pagination_info = PaginationInfo(**pagination)

    # Получаем время обработки из request state если есть
    processing_time = getattr(request.state, "processing_time", None)

    response = SuccessResponse(
        data=data,
        pagination=pagination_info,
        meta=MetaInfo(
            request_id=getattr(request.state, "request_id", str(uuid4())),
            processing_time=processing_time,
        ),
    )

    return JSONResponse(status_code=200, content=response.dict())
