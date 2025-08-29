"""
Базовый роутер для API v1 с стандартизированными ответами
"""

from typing import List
from fastapi import APIRouter

from app.api.v1.schemas.responses import ErrorResponse


class BaseRouter(APIRouter):
    """Базовый роутер с предопределенными ответами на ошибки"""

    def __init__(self, prefix: str, tags: List[str]):
        super().__init__(
            prefix=prefix,
            tags=tags,
            responses={
                400: {"model": ErrorResponse, "description": "Bad Request"},
                401: {"model": ErrorResponse, "description": "Unauthorized"},
                403: {"model": ErrorResponse, "description": "Forbidden"},
                404: {"model": ErrorResponse, "description": "Not Found"},
                422: {
                    "model": ErrorResponse,
                    "description": "Validation Error",
                },
                429: {
                    "model": ErrorResponse,
                    "description": "Too Many Requests",
                },
                500: {
                    "model": ErrorResponse,
                    "description": "Internal Server Error",
                },
            },
        )
