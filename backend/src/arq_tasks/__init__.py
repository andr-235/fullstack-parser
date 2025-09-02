"""
ARQ модуль для асинхронных задач

Предоставляет функциональность для управления очередью задач через ARQ (Async Redis Queue).
"""

from .config import ArqConfig

__all__ = ["ArqConfig"]
