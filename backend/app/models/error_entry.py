"""
Модель для отдельных записей об ошибках
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, Text, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.schemas.error_report import ErrorSeverity, ErrorType

if TYPE_CHECKING:
    from app.models.error_report import ErrorReport


class ErrorEntry(BaseModel):
    """Модель записи об ошибке"""

    __tablename__ = "error_entries"

    # Связь с отчетом
    report_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("error_reports.id"),
        nullable=False,
        comment="ID отчета об ошибках",
    )

    # Основная информация об ошибке
    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Сообщение об ошибке",
    )
    stack_trace: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Стек вызовов",
    )
    context_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment="Контекст ошибки",
    )
    occurred_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Когда произошла ошибка",
    )

    # Дополнительные поля
    error_type: Mapped[Optional[ErrorType]] = mapped_column(
        SQLEnum(ErrorType),
        nullable=True,
        comment="Тип ошибки",
    )
    severity: Mapped[Optional[ErrorSeverity]] = mapped_column(
        SQLEnum(ErrorSeverity),
        nullable=True,
        comment="Уровень серьезности ошибки",
    )

    # Связи
    error_report: Mapped["ErrorReport"] = relationship(
        "ErrorReport",
        back_populates="error_entries",
    )

    def __repr__(self):
        return f"<ErrorEntry(error_type={self.error_type}, severity={self.severity}, message={self.error_message[:50]}...)>"
