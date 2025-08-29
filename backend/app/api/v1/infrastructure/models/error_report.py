"""
Infrastructure модели для отчетов об ошибках (DDD)

SQLAlchemy модели для работы с отчетами об ошибках в Infrastructure Layer
"""

from typing import Any, Dict, List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from .base import BaseModel


class ErrorReportModel(BaseModel):
    """Infrastructure модель отчета об ошибках"""

    __tablename__ = "error_reports"

    report_id = Column(String(255), unique=True, nullable=False, index=True)
    operation = Column(String(255), nullable=False)
    total_errors = Column(Integer, default=0)
    summary = Column(Text)  # JSON
    recommendations = Column(Text)  # JSON
    is_acknowledged = Column(Boolean, default=False)

    # Статистика по группам
    groups_processed = Column(Integer)
    groups_successful = Column(Integer)
    groups_failed = Column(Integer)
    groups_skipped = Column(Integer)
    processing_time_seconds = Column(Integer)

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        import json

        summary = {}
        recommendations = []

        try:
            if self.summary:
                summary = json.loads(self.summary)
        except:
            summary = {}

        try:
            if self.recommendations:
                recommendations = json.loads(self.recommendations)
        except:
            recommendations = []

        return {
            "id": self.id,
            "report_id": self.report_id,
            "operation": self.operation,
            "total_errors": self.total_errors or 0,
            "summary": summary,
            "recommendations": recommendations,
            "is_acknowledged": self.is_acknowledged or False,
            "groups_processed": self.groups_processed,
            "groups_successful": self.groups_successful,
            "groups_failed": self.groups_failed,
            "groups_skipped": self.groups_skipped,
            "processing_time_seconds": self.processing_time_seconds,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_domain_dict(cls, data: Dict[str, Any]) -> "ErrorReportModel":
        """Создать модель из словаря Domain Entity"""
        import json

        model = cls()
        model.report_id = data.get("report_id")
        model.operation = data.get("operation")
        model.total_errors = data.get("total_errors", 0)
        model.summary = json.dumps(data.get("summary", {}))
        model.recommendations = json.dumps(data.get("recommendations", []))
        model.is_acknowledged = data.get("is_acknowledged", False)
        model.groups_processed = data.get("groups_processed")
        model.groups_successful = data.get("groups_successful")
        model.groups_failed = data.get("groups_failed")
        model.groups_skipped = data.get("groups_skipped")
        model.processing_time_seconds = data.get("processing_time_seconds")
        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        import json

        if "report_id" in data:
            self.report_id = data["report_id"]
        if "operation" in data:
            self.operation = data["operation"]
        if "total_errors" in data:
            self.total_errors = data["total_errors"]
        if "summary" in data:
            self.summary = json.dumps(data["summary"])
        if "recommendations" in data:
            self.recommendations = json.dumps(data["recommendations"])
        if "is_acknowledged" in data:
            self.is_acknowledged = data["is_acknowledged"]
        if "groups_processed" in data:
            self.groups_processed = data["groups_processed"]
        if "groups_successful" in data:
            self.groups_successful = data["groups_successful"]
        if "groups_failed" in data:
            self.groups_failed = data["groups_failed"]
        if "groups_skipped" in data:
            self.groups_skipped = data["groups_skipped"]
        if "processing_time_seconds" in data:
            self.processing_time_seconds = data["processing_time_seconds"]

    def __repr__(self) -> str:
        return (
            f"<ErrorReportModel(id={self.id}, report_id='{self.report_id}')>"
        )


class ErrorEntryModel(BaseModel):
    """Infrastructure модель записи об ошибке"""

    __tablename__ = "error_entries"

    error_report_id = Column(ForeignKey("error_reports.id"), nullable=False)
    error_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(Text)
    context = Column(Text)  # JSON
    stack_trace = Column(Text)

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        import json

        context = {}
        try:
            if self.context:
                context = json.loads(self.context)
        except:
            context = {}

        return {
            "id": self.id,
            "error_report_id": self.error_report_id,
            "error_type": self.error_type,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "context": context,
            "stack_trace": self.stack_trace,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_domain_dict(cls, data: Dict[str, Any]) -> "ErrorEntryModel":
        """Создать модель из словаря Domain Entity"""
        import json

        model = cls()
        model.error_report_id = data.get("error_report_id")
        model.error_type = data.get("error_type")
        model.severity = data.get("severity")
        model.message = data.get("message")
        model.details = data.get("details")
        model.context = json.dumps(data.get("context", {}))
        model.stack_trace = data.get("stack_trace")
        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        import json

        if "error_report_id" in data:
            self.error_report_id = data["error_report_id"]
        if "error_type" in data:
            self.error_type = data["error_type"]
        if "severity" in data:
            self.severity = data["severity"]
        if "message" in data:
            self.message = data["message"]
        if "details" in data:
            self.details = data["details"]
        if "context" in data:
            self.context = json.dumps(data["context"])
        if "stack_trace" in data:
            self.stack_trace = data["stack_trace"]

    def __repr__(self) -> str:
        return (
            f"<ErrorEntryModel(id={self.id}, error_type='{self.error_type}')>"
        )
