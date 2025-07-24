"""
Модель для отдельных записей об ошибках
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import JSON, ForeignKey, Integer, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.schemas.error_report import ErrorSeverity, ErrorType


class ErrorEntry(BaseModel):
    """Модель записи об ошибке"""

    __tablename__ = "error_entries"

    # Связь с отчетом
    error_report_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("error_reports.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID отчета об ошибках",
    )

    # Основная информация об ошибке
    error_type: Mapped[ErrorType] = mapped_column(
        SQLEnum(ErrorType),
        nullable=False,
        comment="Тип ошибки",
    )
    severity: Mapped[ErrorSeverity] = mapped_column(
        SQLEnum(ErrorSeverity),
        nullable=False,
        comment="Уровень серьезности ошибки",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Сообщение об ошибке",
    )
    details: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Детали ошибки",
    )
    stack_trace: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Стек вызовов",
    )

    # Контекст ошибки
    context: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment="Контекст ошибки (user_id, group_id, vk_id, screen_name, operation, additional_data)",
    )

    # Связи
    error_report: Mapped["ErrorReport"] = relationship(
        "ErrorReport",
        back_populates="error_entries",
    )

    def __repr__(self):
        return f"<ErrorEntry(error_type={self.error_type}, severity={self.severity}, message={self.message[:50]}...)>"
