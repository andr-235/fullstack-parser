"""
Domain сущности для системы отчетов об ошибках (DDD)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from .base import Entity, ValueObject


class ErrorSeverity(ValueObject):
    """Уровень серьезности ошибки"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __init__(self, level: str = MEDIUM):
        if level not in [self.LOW, self.MEDIUM, self.HIGH, self.CRITICAL]:
            raise ValueError(f"Invalid severity level: {level}")
        self.level = level

    def is_critical(self) -> bool:
        return self.level == self.CRITICAL

    def is_high(self) -> bool:
        return self.level in [self.HIGH, self.CRITICAL]

    def __str__(self) -> str:
        return self.level


class ErrorType(ValueObject):
    """Тип ошибки"""

    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    UNKNOWN = "unknown"

    def __init__(self, error_type: str = UNKNOWN):
        valid_types = [
            self.NETWORK,
            self.DATABASE,
            self.API,
            self.VALIDATION,
            self.AUTHENTICATION,
            self.AUTHORIZATION,
            self.BUSINESS_LOGIC,
            self.EXTERNAL_SERVICE,
            self.SYSTEM,
            self.UNKNOWN,
        ]
        if error_type not in valid_types:
            raise ValueError(f"Invalid error type: {error_type}")
        self.error_type = error_type

    def __str__(self) -> str:
        return self.error_type


class ErrorContext(ValueObject):
    """Контекст ошибки"""

    def __init__(
        self,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        self.operation = operation
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id
        self.endpoint = endpoint
        self.method = method
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.additional_data = additional_data or {}


class ErrorReport(Entity):
    """Доменная сущность отчета об ошибке"""

    def __init__(
        self,
        id: Optional[str] = None,
        error_type: ErrorType = None,
        severity: ErrorSeverity = None,
        message: str = None,
        stack_trace: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ):
        super().__init__(id)
        self.error_type = error_type or ErrorType()
        self.severity = severity or ErrorSeverity()
        self.message = message
        self.stack_trace = stack_trace
        self.context = context or ErrorContext()
        self.acknowledged = False
        self.acknowledged_by: Optional[str] = None
        self.acknowledged_at: Optional[datetime] = None
        self.resolved = False
        self.resolved_at: Optional[datetime] = None
        self.resolution_notes: Optional[str] = None

    def acknowledge(self, acknowledged_by: str) -> None:
        """Подтвердить обработку ошибки"""
        if self.acknowledged:
            raise ValueError("Error report is already acknowledged")

        self.acknowledged = True
        self.acknowledged_by = acknowledged_by
        self.acknowledged_at = datetime.utcnow()
        self.update()

    def resolve(self, resolution_notes: Optional[str] = None) -> None:
        """Разрешить ошибку"""
        if not self.acknowledged:
            raise ValueError("Error must be acknowledged before resolution")

        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolution_notes = resolution_notes
        self.update()

    def reopen(self) -> None:
        """Переоткрыть ошибку"""
        self.resolved = False
        self.resolved_at = None
        self.resolution_notes = None
        self.update()

    @property
    def is_critical(self) -> bool:
        return self.severity.is_critical()

    @property
    def is_pending(self) -> bool:
        return not self.acknowledged

    @property
    def is_resolved(self) -> bool:
        return self.resolved

    @property
    def time_to_acknowledge(self) -> Optional[float]:
        """Время до подтверждения в часах"""
        if not self.acknowledged_at:
            return None
        return (self.acknowledged_at - self.created_at).total_seconds() / 3600

    @property
    def time_to_resolve(self) -> Optional[float]:
        """Время до разрешения в часах"""
        if not self.resolved_at:
            return None
        return (self.resolved_at - self.created_at).total_seconds() / 3600

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "error_type": str(self.error_type),
            "severity": str(self.severity),
            "message": self.message,
            "stack_trace": self.stack_trace,
            "context": {
                "operation": self.context.operation,
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "endpoint": self.context.endpoint,
                "method": self.context.method,
                "ip_address": self.context.ip_address,
                "user_agent": self.context.user_agent,
                "additional_data": self.context.additional_data,
            },
            "status": {
                "acknowledged": self.acknowledged,
                "acknowledged_by": self.acknowledged_by,
                "acknowledged_at": (
                    self.acknowledged_at.isoformat()
                    if self.acknowledged_at
                    else None
                ),
                "resolved": self.resolved,
                "resolved_at": (
                    self.resolved_at.isoformat() if self.resolved_at else None
                ),
                "resolution_notes": self.resolution_notes,
            },
            "timestamps": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "time_to_acknowledge": self.time_to_acknowledge,
                "time_to_resolve": self.time_to_resolve,
            },
        }
