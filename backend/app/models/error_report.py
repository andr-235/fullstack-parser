"""
Модель для отчетов об ошибках
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.error_entry import ErrorEntry


class ErrorReport(BaseModel):
    """Модель отчета об ошибках"""

    __tablename__ = "error_reports"

    # Основная информация
    report_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        comment="Уникальный ID отчета",
    )
    operation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Операция, при которой произошли ошибки",
    )
    total_errors: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Общее количество ошибок",
    )

    # Статистика
    summary: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment="Статистика ошибок по типам",
    )
    recommendations: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        comment="Рекомендации по исправлению",
    )

    # Специфичные поля для отчетов о группах
    groups_processed: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Количество обработанных групп",
    )
    groups_successful: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Количество успешно загруженных групп",
    )
    groups_failed: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Количество групп с ошибками",
    )
    groups_skipped: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Количество пропущенных групп",
    )
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(
        Integer,
        comment="Время обработки в секундах",
    )

    # Статус
    is_acknowledged: Mapped[bool] = mapped_column(
        default=False,
        comment="Подтвержден ли отчет",
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        comment="Когда был подтвержден отчет",
    )
    acknowledged_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Кто подтвердил отчет",
    )

    # Связи
    error_entries: Mapped[List["ErrorEntry"]] = relationship(
        "ErrorEntry",
        back_populates="error_report",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ErrorReport(report_id={self.report_id}, operation={self.operation}, total_errors={self.total_errors})>"
