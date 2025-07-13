"""
Агрегирующий роутер для API v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, info

api_router = APIRouter()
