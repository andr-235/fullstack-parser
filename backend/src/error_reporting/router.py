"""
Переделанный роутер errors с новой архитектурой (DDD + Middleware)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Request, Depends, Query, Path
from ..application.error_report_service import ErrorReportApplicationService
from ..handlers.common import create_success_response, create_error_response
from ..dependencies import CommonDB, PageParam, SizeParam


router = APIRouter(prefix="/reports", tags=["Error Reports"])


# Dependency для Error Report Service
def get_error_report_service() -> ErrorReportApplicationService:
    """Получить экземпляр Error Report Service"""
    return ErrorReportApplicationService()


@router.get(
    "",
    summary="Get Error Reports",
    description="Получить список отчетов об ошибках с фильтрацией и пагинацией",
)
async def get_error_reports(
    request: Request,
    page: int = PageParam,
    size: int = SizeParam,
    error_type: Optional[str] = Query(
        None, description="Фильтр по типу ошибки"
    ),
    severity: Optional[str] = Query(None, description="Фильтр по серьезности"),
    operation: Optional[str] = Query(None, description="Фильтр по операции"),
    acknowledged: Optional[bool] = Query(
        None, description="Фильтр по статусу подтверждения"
    ),
    resolved: Optional[bool] = Query(
        None, description="Фильтр по статусу разрешения"
    ),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Получить список отчетов об ошибках с фильтрами"""
    try:
        result = await error_service.get_error_reports(
            page=page,
            size=size,
            error_type=error_type,
            severity=severity,
            operation=operation,
            acknowledged=acknowledged,
            resolved=resolved,
            start_date=start_date,
            end_date=end_date,
        )
        return await create_success_response(
            request,
            result["items"],
            {
                "page": result["page"],
                "size": result["size"],
                "total": result["total"],
                "pages": result["pages"],
                "has_next": result["has_next"],
                "has_prev": result["has_prev"],
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "ERROR_REPORTS_LOAD_FAILED",
            f"Failed to load error reports: {str(e)}",
        )


@router.get(
    "/{report_id}",
    summary="Get Error Report by ID",
    description="Получить конкретный отчет об ошибках по его ID",
)
async def get_error_report(
    request: Request,
    report_id: str = Path(..., description="ID отчета об ошибках"),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Получить конкретный отчет об ошибках"""
    try:
        report = await error_service.get_error_report(report_id)
        if not report:
            return await create_error_response(
                request,
                404,
                "ERROR_REPORT_NOT_FOUND",
                f"Error report with id '{report_id}' not found",
            )

        return await create_success_response(request, report.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "ERROR_REPORT_LOAD_FAILED",
            f"Failed to load error report: {str(e)}",
        )


@router.post(
    "",
    summary="Create Error Report",
    description="Создать новый отчет об ошибке",
)
async def create_error_report(
    request: Request,
    error_data: Dict[str, Any],
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Создать новый отчет об ошибке"""
    try:
        report = await error_service.create_error_report(
            error_type=error_data.get("error_type", "unknown"),
            severity=error_data.get("severity", "medium"),
            message=error_data.get("message", "Unknown error"),
            stack_trace=error_data.get("stack_trace"),
            operation=error_data.get("operation"),
            user_id=error_data.get("user_id"),
            request_id=error_data.get("request_id"),
            additional_context=error_data.get("additional_context", {}),
        )
        return await create_success_response(
            request,
            report.to_dict(),
            {"message": "Отчет об ошибке успешно создан"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "ERROR_REPORT_CREATION_FAILED",
            f"Failed to create error report: {str(e)}",
        )


@router.post(
    "/{report_id}/acknowledge",
    summary="Acknowledge Error Report",
    description="Подтвердить обработку отчета об ошибках",
)
async def acknowledge_error_report(
    request: Request,
    report_id: str = Path(..., description="ID отчета об ошибках"),
    acknowledged_by: str = Query(
        ..., description="Имя пользователя, подтверждающего отчет"
    ),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Подтвердить обработку отчета об ошибках"""
    try:
        report = await error_service.acknowledge_error_report(
            report_id, acknowledged_by
        )
        if not report:
            return await create_error_response(
                request,
                404,
                "ERROR_REPORT_NOT_FOUND",
                f"Error report with id '{report_id}' not found",
            )

        return await create_success_response(
            request,
            report.to_dict(),
            {"message": f"Отчет об ошибке '{report_id}' подтвержден"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "ERROR_REPORT_ACKNOWLEDGMENT_FAILED",
            f"Failed to acknowledge error report: {str(e)}",
        )


@router.delete(
    "/{report_id}",
    summary="Delete Error Report",
    description="Удалить отчет об ошибках",
)
async def delete_error_report(
    request: Request,
    report_id: str = Path(..., description="ID отчета об ошибках"),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Удалить отчет об ошибках"""
    try:
        deleted = await error_service.delete_error_report(report_id)
        if not deleted:
            return await create_error_response(
                request,
                404,
                "ERROR_REPORT_NOT_FOUND",
                f"Error report with id '{report_id}' not found",
            )

        return await create_success_response(
            request,
            None,
            {"message": f"Отчет об ошибке '{report_id}' успешно удален"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "ERROR_REPORT_DELETION_FAILED",
            f"Failed to delete error report: {str(e)}",
        )


@router.get(
    "/stats/overview",
    summary="Get Error Statistics",
    description="Получить общую статистику по ошибкам",
)
async def get_error_statistics(
    request: Request,
    days: int = Query(7, description="Количество дней для статистики"),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Получить статистику по ошибкам"""
    try:
        stats = await error_service.get_error_statistics(days=days)
        return await create_success_response(request, stats)
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "ERROR_STATISTICS_LOAD_FAILED",
            f"Failed to load error statistics: {str(e)}",
        )


@router.get(
    "/pending/list",
    summary="Get Pending Error Reports",
    description="Получить список неподтвержденных отчетов об ошибках",
)
async def get_pending_reports(
    request: Request,
    limit: int = Query(50, description="Максимальное количество отчетов"),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Получить список неподтвержденных отчетов об ошибках"""
    try:
        reports = await error_service.get_pending_reports(limit=limit)
        return await create_success_response(
            request, [report.to_dict() for report in reports]
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "PENDING_REPORTS_LOAD_FAILED",
            f"Failed to load pending error reports: {str(e)}",
        )


@router.get(
    "/critical/list",
    summary="Get Critical Error Reports",
    description="Получить список критических отчетов об ошибках",
)
async def get_critical_reports(
    request: Request,
    limit: int = Query(50, description="Максимальное количество отчетов"),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Получить список критических отчетов об ошибках"""
    try:
        reports = await error_service.get_critical_reports(limit=limit)
        return await create_success_response(
            request, [report.to_dict() for report in reports]
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "CRITICAL_REPORTS_LOAD_FAILED",
            f"Failed to load critical error reports: {str(e)}",
        )


@router.post(
    "/bulk/acknowledge",
    summary="Bulk Acknowledge Error Reports",
    description="Массовое подтверждение отчетов об ошибках",
)
async def bulk_acknowledge_reports(
    request: Request,
    report_ids: List[str],
    acknowledged_by: str = Query(
        ..., description="Имя пользователя, подтверждающего отчеты"
    ),
    error_service: ErrorReportApplicationService = Depends(
        get_error_report_service
    ),
) -> Dict[str, Any]:
    """Массовое подтверждение отчетов об ошибках"""
    try:
        result = await error_service.bulk_acknowledge_reports(
            report_ids, acknowledged_by
        )
        return await create_success_response(
            request,
            result,
            {"message": f"Обработано {result['total_processed']} отчетов"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "BULK_ACKNOWLEDGMENT_FAILED",
            f"Failed to bulk acknowledge error reports: {str(e)}",
        )
