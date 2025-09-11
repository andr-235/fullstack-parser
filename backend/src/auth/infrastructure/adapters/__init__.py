"""
Адаптеры модуля Auth

Содержит адаптеры для внешних сервисов
"""

from .security_service_adapter import (
    SecurityServicePasswordAdapter,
    SecurityServiceTokenAdapter,
)

__all__ = [
    "SecurityServicePasswordAdapter",
    "SecurityServiceTokenAdapter",
]
