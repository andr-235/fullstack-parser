"""
Агрегирующий роутер для API v1
"""

from app.api.v1.endpoints import health, info
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(info.router)
