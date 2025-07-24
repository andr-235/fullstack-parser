"""
API endpoints для работы с отчетами об ошибках
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.base import PaginatedResponse
from app.schemas.error_report import (
    ErrorReport,
    ErrorReportResponse,
    ErrorSeverity,
    ErrorType,
)
from app.services.error_reporting_service import error_reporting_service
from app.services.error_report_db_service import ErrorReportDBService

router = APIRouter(tags=["Error Reports"])


@router.get("/reports", response_model=PaginatedResponse[ErrorReport])
async def get_error_reports(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    error_type: Optional[ErrorType] = Query(
        None, description="Фильтр по типу ошибки"
    ),
    severity: Optional[ErrorSeverity] = Query(
        None, description="Фильтр по серьезности"
    ),
    operation: Optional[str] = Query(None, description="Фильтр по операции"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    is_acknowledged: Optional[bool] = Query(
        None, description="Фильтр по статусу подтверждения"
    ),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ErrorReport]:
    """
    Получить список отчетов об ошибках с фильтрацией

    Args:
        page: Номер страницы
        size: Размер страницы
        error_type: Тип ошибки для фильтрации
        severity: Уровень серьезности для фильтрации
        operation: Операция для фильтрации
        start_date: Начальная дата для фильтрации
        end_date: Конечная дата для фильтрации
        is_acknowledged: Статус подтверждения для фильтрации
        db: Сессия базы данных

    Returns:
        Пагинированный список отчетов об ошибках
    """
    error_db_service = ErrorReportDBService(db)
    return await error_db_service.get_error_reports(
        page=page,
        size=size,
        error_type=error_type,
        severity=severity,
        operation=operation,
        start_date=start_date,
        end_date=end_date,
        is_acknowledged=is_acknowledged,
    )


@router.get("/reports/{report_id}", response_model=ErrorReportResponse)
async def get_error_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
) -> ErrorReportResponse:
    """
    Получить конкретный отчет об ошибках

    Args:
        report_id: ID отчета
        db: Сессия базы данных

    Returns:
        Отчет об ошибках
    """
    error_db_service = ErrorReportDBService(db)
    report = await error_db_service.get_error_report(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отчет не найден",
        )

    return ErrorReportResponse(
        success=True,
        report=report,
        message="Отчет успешно получен",
    )


@router.get("/stats", response_model=dict)
async def get_error_stats(
    days: int = Query(7, description="Количество дней для статистики"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Получить статистику ошибок за указанный период

    Args:
        days: Количество дней для статистики
        db: Сессия базы данных

    Returns:
        Статистика ошибок
    """
    error_db_service = ErrorReportDBService(db)
    return await error_db_service.get_error_stats(days)


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_error_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Удалить отчет об ошибках

    Args:
        report_id: ID отчета
        db: Сессия базы данных
    """
    error_db_service = ErrorReportDBService(db)
    deleted = await error_db_service.delete_error_report(report_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отчет не найден",
        )


@router.post(
    "/reports/{report_id}/acknowledge", response_model=ErrorReportResponse
)
async def acknowledge_error_report(
    report_id: str,
    acknowledged_by: str = Query(
        ..., description="Имя пользователя, подтверждающего отчет"
    ),
    db: AsyncSession = Depends(get_db),
) -> ErrorReportResponse:
    """
    Подтвердить обработку отчета об ошибках

    Args:
        report_id: ID отчета
        acknowledged_by: Имя пользователя, подтверждающего отчет
        db: Сессия базы данных

    Returns:
        Обновленный отчет
    """
    error_db_service = ErrorReportDBService(db)
    report = await error_db_service.acknowledge_error_report(
        report_id, acknowledged_by
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отчет не найден",
        )

    return ErrorReportResponse(
        success=True,
        message="Отчет успешно подтвержден",
    )
