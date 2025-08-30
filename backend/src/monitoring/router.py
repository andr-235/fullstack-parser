"""
FastAPI роутер для модуля Monitoring

Определяет API эндпоинты для управления мониторингом групп VK
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from .dependencies import get_monitoring_service
from .schemas import (
    MonitoringCreate,
    MonitoringUpdate,
    MonitoringResponse,
    MonitoringListResponse,
    MonitoringResultResponse,
    MonitoringStats,
    MonitoringHealth,
    BulkMonitoringAction,
    BulkMonitoringResponse,
    MonitoringReport,
)
from .service import MonitoringService
from ..pagination import (
    get_pagination_params,
    PaginationParams,
    create_paginated_response,
    PageParam,
    SizeParam,
    SearchParam,
)

router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
    responses={
        404: {"description": "Monitoring not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable"},
    },
)


@router.post(
    "",
    response_model=MonitoringResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать мониторинг группы",
    description="Создать новый мониторинг для группы VK"
)
async def create_monitoring(
    monitoring_data: MonitoringCreate,
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringResponse:
    """Создать мониторинг группы"""
    try:
        monitoring = await service.create_monitoring(
            group_id=monitoring_data.group_id,
            group_name=monitoring_data.group_name,
            owner_id=monitoring_data.owner_id,
            config=monitoring_data.config.model_dump() if monitoring_data.config else None,
        )
        return MonitoringResponse(**monitoring)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "",
    response_model=MonitoringListResponse,
    summary="Получить мониторинги пользователя",
    description="Получить список мониторингов для указанного пользователя"
)
async def get_user_monitorings(
    owner_id: str = Query(..., description="ID владельца мониторингов"),
    page: PageParam = 1,
    size: SizeParam = 20,
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringListResponse:
    """Получить мониторинги пользователя"""

    pagination = PaginationParams(
        page=page,
        size=size,
    )

    # Получаем мониторинги
    monitorings = await service.get_user_monitorings(
        owner_id=owner_id,
        limit=pagination.limit,
        offset=pagination.offset,
        status_filter=status,
    )

    # В реальности нужно получить total из БД
    total = len(monitorings)  # Заглушка

    return create_paginated_response(monitorings, total, pagination)


@router.get(
    "/{monitoring_id}",
    response_model=MonitoringResponse,
    summary="Получить мониторинг",
    description="Получить информацию о конкретном мониторинге"
)
async def get_monitoring(
    monitoring_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringResponse:
    """Получить мониторинг по ID"""
    try:
        monitoring = await service.get_monitoring(monitoring_id)
        if not monitoring:
            raise HTTPException(status_code=404, detail="Мониторинг не найден")
        return MonitoringResponse(**monitoring)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{monitoring_id}",
    response_model=MonitoringResponse,
    summary="Обновить мониторинг",
    description="Обновить настройки мониторинга"
)
async def update_monitoring(
    monitoring_id: str,
    monitoring_data: MonitoringUpdate,
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringResponse:
    """Обновить мониторинг"""
    try:
        updated_data = monitoring_data.model_dump(exclude_unset=True)
        if monitoring_data.config:
            updated_data["config"] = monitoring_data.config.model_dump()

        monitoring = await service.update_monitoring(monitoring_id, updated_data)
        return MonitoringResponse(**monitoring)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{monitoring_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить мониторинг",
    description="Удалить мониторинг группы"
)
async def delete_monitoring(
    monitoring_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
):
    """Удалить мониторинг"""
    try:
        success = await service.delete_monitoring(monitoring_id)
        if not success:
            raise HTTPException(status_code=404, detail="Мониторинг не найден")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{monitoring_id}/start",
    response_model=MonitoringResponse,
    summary="Запустить мониторинг",
    description="Запустить автоматический мониторинг группы"
)
async def start_monitoring(
    monitoring_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringResponse:
    """Запустить мониторинг"""
    try:
        monitoring = await service.start_monitoring(monitoring_id)
        return MonitoringResponse(**monitoring)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{monitoring_id}/stop",
    response_model=MonitoringResponse,
    summary="Остановить мониторинг",
    description="Остановить автоматический мониторинг группы"
)
async def stop_monitoring(
    monitoring_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringResponse:
    """Остановить мониторинг"""
    try:
        monitoring = await service.stop_monitoring(monitoring_id)
        return MonitoringResponse(**monitoring)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{monitoring_id}/pause",
    response_model=MonitoringResponse,
    summary="Приостановить мониторинг",
    description="Приостановить автоматический мониторинг группы"
)
async def pause_monitoring(
    monitoring_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringResponse:
    """Приостановить мониторинг"""
    try:
        monitoring = await service.pause_monitoring(monitoring_id)
        return MonitoringResponse(**monitoring)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{monitoring_id}/run",
    response_model=MonitoringResultResponse,
    summary="Выполнить цикл мониторинга",
    description="Принудительно выполнить один цикл мониторинга"
)
async def run_monitoring_cycle(
    monitoring_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringResultResponse:
    """Выполнить цикл мониторинга"""
    try:
        result = await service.run_monitoring_cycle(monitoring_id)
        return MonitoringResultResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/bulk-action",
    response_model=BulkMonitoringResponse,
    summary="Массовое действие",
    description="Выполнить действие над несколькими мониторингами одновременно"
)
async def bulk_action(
    action_data: BulkMonitoringAction,
    service: MonitoringService = Depends(get_monitoring_service),
) -> BulkMonitoringResponse:
    """Массовое действие с мониторингами"""
    try:
        result = await service.bulk_action(
            monitoring_ids=action_data.monitoring_ids,
            action=action_data.action,
            reason=action_data.reason,
        )
        return BulkMonitoringResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/stats/overview",
    response_model=MonitoringStats,
    summary="Статистика мониторинга",
    description="Получить общую статистику системы мониторинга"
)
async def get_monitoring_stats(
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringStats:
    """Получить статистику мониторинга"""
    try:
        stats = await service.get_monitoring_stats()
        return MonitoringStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health/status",
    response_model=MonitoringHealth,
    summary="Здоровье системы",
    description="Проверить состояние здоровья системы мониторинга"
)
async def get_monitoring_health(
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringHealth:
    """Проверить здоровье системы мониторинга"""
    try:
        health = await service.get_monitoring_health()
        return MonitoringHealth(**health)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{monitoring_id}/report",
    response_model=MonitoringReport,
    summary="Отчет по мониторингу",
    description="Получить отчет о работе мониторинга за период"
)
async def get_monitoring_report(
    monitoring_id: str,
    days: int = Query(7, description="Период в днях", ge=1, le=90),
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringReport:
    """Получить отчет по мониторингу"""
    try:
        # Заглушка - в реальном приложении здесь будет генерация отчета
        report_data = {
            "monitoring_id": monitoring_id,
            "period_start": datetime.utcnow() - timedelta(days=days),
            "period_end": datetime.utcnow(),
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "posts_found": 0,
            "comments_found": 0,
            "average_processing_time": 0.0,
            "uptime_percentage": 0.0,
            "top_keywords": [],
        }

        return MonitoringReport(**report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Импорт для работы с datetime
from datetime import datetime, timedelta


# Экспорт роутера
__all__ = ["router"]
