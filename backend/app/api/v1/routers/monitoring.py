"""
Переделанный роутер monitoring с новой архитектурой (DDD + Middleware)
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Request, Depends, Query, Path
from ..application.monitoring_service import MonitoringApplicationService
from ..handlers.common import create_success_response, create_error_response
from ..dependencies import CommonDB, PageParam, SizeParam


router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


# Dependency для Monitoring Service
def get_monitoring_service() -> MonitoringApplicationService:
    """Получить экземпляр Monitoring Service"""
    return MonitoringApplicationService()


@router.post(
    "",
    summary="Create Group Monitoring",
    description="Создать мониторинг для VK группы",
)
async def create_monitoring(
    request: Request,
    group_id: int = Query(..., description="ID VK группы"),
    group_name: str = Query(..., description="Название группы"),
    owner_id: str = Query(..., description="ID владельца мониторинга"),
    config: Optional[Dict[str, Any]] = None,
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Создать мониторинг для VK группы"""
    try:
        monitoring = await monitoring_service.create_monitoring(
            group_id=group_id,
            group_name=group_name,
            owner_id=owner_id,
            config=config,
        )
        return await create_success_response(
            request,
            monitoring.to_dict(),
            {
                "message": f"Мониторинг для группы '{group_name}' успешно создан"
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "MONITORING_CREATION_FAILED",
            f"Failed to create monitoring: {str(e)}",
        )


@router.get(
    "",
    summary="Get User Monitorings",
    description="Получить список мониторингов пользователя",
)
async def get_user_monitorings(
    request: Request,
    owner_id: str = Query(..., description="ID владельца мониторингов"),
    page: int = PageParam,
    size: int = SizeParam,
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Получить список мониторингов пользователя"""
    try:
        result = await monitoring_service.get_user_monitorings(
            owner_id=owner_id,
            page=page,
            size=size,
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
            "MONITORINGS_LOAD_FAILED",
            f"Failed to load monitorings: {str(e)}",
        )


@router.get(
    "/{monitoring_id}",
    summary="Get Monitoring by ID",
    description="Получить мониторинг по его ID",
)
async def get_monitoring(
    request: Request,
    monitoring_id: str = Path(..., description="ID мониторинга"),
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Получить мониторинг по ID"""
    try:
        monitoring = await monitoring_service.get_monitoring(monitoring_id)
        if not monitoring:
            return await create_error_response(
                request,
                404,
                "MONITORING_NOT_FOUND",
                f"Monitoring with id '{monitoring_id}' not found",
            )

        return await create_success_response(request, monitoring.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "MONITORING_LOAD_FAILED",
            f"Failed to load monitoring: {str(e)}",
        )


@router.post(
    "/{monitoring_id}/start",
    summary="Start Monitoring",
    description="Запустить мониторинг",
)
async def start_monitoring(
    request: Request,
    monitoring_id: str = Path(..., description="ID мониторинга"),
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Запустить мониторинг"""
    try:
        monitoring = await monitoring_service.start_monitoring(monitoring_id)
        return await create_success_response(
            request,
            monitoring.to_dict(),
            {"message": f"Мониторинг '{monitoring_id}' запущен"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "MONITORING_START_FAILED",
            f"Failed to start monitoring: {str(e)}",
        )


@router.post(
    "/{monitoring_id}/pause",
    summary="Pause Monitoring",
    description="Приостановить мониторинг",
)
async def pause_monitoring(
    request: Request,
    monitoring_id: str = Path(..., description="ID мониторинга"),
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Приостановить мониторинг"""
    try:
        monitoring = await monitoring_service.pause_monitoring(monitoring_id)
        return await create_success_response(
            request,
            monitoring.to_dict(),
            {"message": f"Мониторинг '{monitoring_id}' приостановлен"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "MONITORING_PAUSE_FAILED",
            f"Failed to pause monitoring: {str(e)}",
        )


@router.post(
    "/{monitoring_id}/stop",
    summary="Stop Monitoring",
    description="Остановить мониторинг",
)
async def stop_monitoring(
    request: Request,
    monitoring_id: str = Path(..., description="ID мониторинга"),
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Остановить мониторинг"""
    try:
        monitoring = await monitoring_service.stop_monitoring(monitoring_id)
        return await create_success_response(
            request,
            monitoring.to_dict(),
            {"message": f"Мониторинг '{monitoring_id}' остановлен"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "MONITORING_STOP_FAILED",
            f"Failed to stop monitoring: {str(e)}",
        )


@router.put(
    "/{monitoring_id}/config",
    summary="Update Monitoring Config",
    description="Обновить конфигурацию мониторинга",
)
async def update_monitoring_config(
    request: Request,
    monitoring_id: str = Path(..., description="ID мониторинга"),
    config_updates: Dict[str, Any] = None,
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Обновить конфигурацию мониторинга"""
    try:
        monitoring = await monitoring_service.update_config(
            monitoring_id, config_updates or {}
        )
        return await create_success_response(
            request,
            monitoring.to_dict(),
            {
                "message": f"Конфигурация мониторинга '{monitoring_id}' обновлена"
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "CONFIG_UPDATE_FAILED",
            f"Failed to update monitoring config: {str(e)}",
        )


@router.delete(
    "/{monitoring_id}",
    summary="Delete Monitoring",
    description="Удалить мониторинг",
)
async def delete_monitoring(
    request: Request,
    monitoring_id: str = Path(..., description="ID мониторинга"),
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Удалить мониторинг"""
    try:
        deleted = await monitoring_service.delete_monitoring(monitoring_id)
        if not deleted:
            return await create_error_response(
                request,
                404,
                "MONITORING_NOT_FOUND",
                f"Monitoring with id '{monitoring_id}' not found",
            )

        return await create_success_response(
            request,
            None,
            {"message": f"Мониторинг '{monitoring_id}' успешно удален"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "MONITORING_DELETION_FAILED",
            f"Failed to delete monitoring: {str(e)}",
        )


@router.post(
    "/{monitoring_id}/execute",
    summary="Execute Monitoring Cycle",
    description="Выполнить цикл мониторинга",
)
async def execute_monitoring_cycle(
    request: Request,
    monitoring_id: str = Path(..., description="ID мониторинга"),
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Выполнить цикл мониторинга"""
    try:
        result = await monitoring_service.execute_monitoring_cycle(
            monitoring_id
        )
        return await create_success_response(
            request,
            result.to_dict(),
            {"message": f"Цикл мониторинга '{monitoring_id}' выполнен"},
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "CYCLE_EXECUTION_FAILED",
            f"Failed to execute monitoring cycle: {str(e)}",
        )


@router.get(
    "/stats/system",
    summary="Get System Monitoring Stats",
    description="Получить статистику системы мониторинга",
)
async def get_system_stats(
    request: Request,
    owner_id: Optional[str] = Query(
        None, description="ID пользователя (опционально)"
    ),
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Получить статистику системы мониторинга"""
    try:
        stats = await monitoring_service.get_system_stats(owner_id=owner_id)
        return await create_success_response(request, stats.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SYSTEM_STATS_LOAD_FAILED",
            f"Failed to load system stats: {str(e)}",
        )


@router.post(
    "/bulk/start",
    summary="Bulk Start Monitoring",
    description="Массовый запуск мониторинга",
)
async def bulk_start_monitoring(
    request: Request,
    monitoring_ids: List[str],
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Массовый запуск мониторинга"""
    try:
        result = await monitoring_service.bulk_start_monitoring(monitoring_ids)
        return await create_success_response(
            request,
            result,
            {
                "message": f"Обработано {result['total_processed']} мониторингов"
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "BULK_START_FAILED",
            f"Failed to bulk start monitoring: {str(e)}",
        )


@router.post(
    "/bulk/stop",
    summary="Bulk Stop Monitoring",
    description="Массовая остановка мониторинга",
)
async def bulk_stop_monitoring(
    request: Request,
    monitoring_ids: List[str],
    monitoring_service: MonitoringApplicationService = Depends(
        get_monitoring_service
    ),
) -> Dict[str, Any]:
    """Массовая остановка мониторинга"""
    try:
        result = await monitoring_service.bulk_stop_monitoring(monitoring_ids)
        return await create_success_response(
            request,
            result,
            {
                "message": f"Обработано {result['total_processed']} мониторингов"
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "BULK_STOP_FAILED",
            f"Failed to bulk stop monitoring: {str(e)}",
        )
