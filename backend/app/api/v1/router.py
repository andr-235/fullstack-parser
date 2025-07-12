"""
Агрегирующий роутер для API v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, info

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(info.router)
