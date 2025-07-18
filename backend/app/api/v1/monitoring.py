"""
API endpoints для управления автоматическим мониторингом
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.schemas.base import StatusResponse, PaginatedResponse, PaginationParams
from app.schemas.monitoring import (
    GroupMonitoringConfig,
    GroupMonitoringResponse,
    MonitoringStats,
    SchedulerStatus,
)
from app.services.monitoring_service import MonitoringService
from app.services.scheduler_service import get_scheduler_service
from app.services.vkbottle_service import VKBottleService

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/stats", response_model=MonitoringStats)
async def get_monitoring_stats(
    db: AsyncSession = Depends(get_db),
) -> MonitoringStats:
    """Получить статистику мониторинга"""
    vk_service = VKBottleService(
        token="stub", api_version="5.131"
    )  # TODO: заменить на settings
    monitoring_service = MonitoringService(db=db, vk_service=vk_service)

    stats = await monitoring_service.get_monitoring_stats()
    return MonitoringStats(**stats)


@router.get("/groups", response_model=PaginatedResponse[GroupMonitoringResponse])
async def get_monitoring_groups(
    pagination: PaginationParams = Depends(),
    active_only: bool = True,
    monitoring_enabled: bool = True,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[GroupMonitoringResponse]:
    """Получить список групп с мониторингом"""
    from app.models.vk_group import VKGroup

    # Базовый запрос
    query = select(VKGroup)
    
    # Фильтры
    conditions = []
    if active_only:
        conditions.append(VKGroup.is_active.is_(True))
    if monitoring_enabled:
        conditions.append(VKGroup.auto_monitoring_enabled.is_(True))
    
    if conditions:
        query = query.where(and_(*conditions))

    # Подсчет общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Получение данных с пагинацией
    result = await db.execute(
        query.offset(pagination.skip).limit(pagination.size)
    )
    groups = result.scalars().all()

    # Преобразование в ответ
    items = []
    for group in groups:
        items.append(GroupMonitoringResponse(
            group_id=group.id,
            group_name=group.name,
            auto_monitoring_enabled=group.auto_monitoring_enabled,
            monitoring_interval_minutes=group.monitoring_interval_minutes,
            monitoring_priority=group.monitoring_priority,
            next_monitoring_at=group.next_monitoring_at,
            monitoring_runs_count=group.monitoring_runs_count,
            last_monitoring_success=group.last_monitoring_success,
            last_monitoring_error=group.last_monitoring_error,
        ))

    return PaginatedResponse(
        total=total,
        page=pagination.page,
        size=pagination.size,
        items=items,
    )


@router.get("/scheduler/status", response_model=SchedulerStatus)
async def get_scheduler_status() -> SchedulerStatus:
    """Получить статус планировщика"""
    scheduler = await get_scheduler_service()
    status_data = await scheduler.get_scheduler_status()
    return SchedulerStatus(**status_data)


@router.post("/scheduler/start", response_model=StatusResponse)
async def start_scheduler(interval_seconds: int = 300) -> StatusResponse:
    """Запустить планировщик мониторинга"""
    try:
        scheduler = await get_scheduler_service()

        # Запускаем планировщик в фоновом режиме
        import asyncio

        asyncio.create_task(
            scheduler.start_monitoring_scheduler(interval_seconds)
        )

        return StatusResponse(
            status="success",
            message=f"Планировщик запущен с интервалом {interval_seconds} секунд",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка запуска планировщика: {str(e)}",
        ) from e


@router.post("/scheduler/stop", response_model=StatusResponse)
async def stop_scheduler() -> StatusResponse:
    """Остановить планировщик мониторинга"""
    try:
        scheduler = await get_scheduler_service()
        await scheduler.stop_monitoring_scheduler()

        return StatusResponse(
            status="success", message="Планировщик остановлен"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка остановки планировщика: {str(e)}",
        ) from e


@router.post("/run-cycle", response_model=StatusResponse)
async def run_monitoring_cycle() -> StatusResponse:
    """Запустить цикл мониторинга вручную"""
    try:
        scheduler = await get_scheduler_service()
        job_id = await scheduler.run_manual_monitoring_cycle()

        if job_id:
            return StatusResponse(
                status="success",
                message=f"Цикл мониторинга запущен (job_id: {job_id})",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось запустить цикл мониторинга",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка запуска цикла мониторинга: {str(e)}",
        ) from e


@router.post("/groups/{group_id}/enable", response_model=StatusResponse)
async def enable_group_monitoring(
    group_id: int,
    config: GroupMonitoringConfig,
    db: AsyncSession = Depends(get_db),
) -> StatusResponse:
    """Включить автоматический мониторинг для группы"""
    vk_service = VKBottleService(
        token="stub", api_version="5.131"
    )  # TODO: заменить на settings
    monitoring_service = MonitoringService(db=db, vk_service=vk_service)

    success = await monitoring_service.enable_group_monitoring(
        group_id=group_id,
        interval_minutes=config.interval_minutes,
        priority=config.priority,
    )

    if success:
        return StatusResponse(
            status="success",
            message=f"Мониторинг включен для группы {group_id}",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось включить мониторинг для группы",
        )


@router.post("/groups/{group_id}/disable", response_model=StatusResponse)
async def disable_group_monitoring(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> StatusResponse:
    """Отключить автоматический мониторинг для группы"""
    vk_service = VKBottleService(
        token="stub", api_version="5.131"
    )  # TODO: заменить на settings
    monitoring_service = MonitoringService(db=db, vk_service=vk_service)

    success = await monitoring_service.disable_group_monitoring(
        group_id=group_id
    )

    if success:
        return StatusResponse(
            status="success",
            message=f"Мониторинг отключен для группы {group_id}",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось отключить мониторинг для группы",
        )


@router.put("/groups/{group_id}/settings", response_model=StatusResponse)
async def update_group_monitoring_settings(
    group_id: int,
    config: GroupMonitoringConfig,
    db: AsyncSession = Depends(get_db),
) -> StatusResponse:
    """Обновить настройки мониторинга группы"""
    from app.models.vk_group import VKGroup

    result = await db.execute(select(VKGroup).where(VKGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    if not group.auto_monitoring_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мониторинг не включен для этой группы",
        )

    # Обновляем настройки
    group.monitoring_interval_minutes = max(1, min(1440, config.interval_minutes))
    group.monitoring_priority = max(1, min(10, config.priority))

    await db.commit()

    return StatusResponse(
        status="success",
        message=f"Настройки мониторинга обновлены для группы {group_id}",
    )


@router.post("/groups/{group_id}/run", response_model=StatusResponse)
async def run_group_monitoring(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> StatusResponse:
    """Запустить мониторинг группы вручную"""
    from app.models.vk_group import VKGroup
    
    vk_service = VKBottleService(
        token="stub", api_version="5.131"
    )  # TODO: заменить на settings
    monitoring_service = MonitoringService(db=db, vk_service=vk_service)

    # Получаем группу
    result = await db.execute(select(VKGroup).where(VKGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    success = await monitoring_service.start_group_monitoring(group)

    if success:
        return StatusResponse(
            status="success",
            message=f"Мониторинг запущен для группы {group_id}",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось запустить мониторинг для группы",
        )


@router.post("/run-cycle", response_model=dict)
async def run_monitoring_cycle_endpoint(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Запустить цикл мониторинга всех готовых групп"""
    vk_service = VKBottleService(
        token="stub", api_version="5.131"
    )  # TODO: заменить на settings
    monitoring_service = MonitoringService(db=db, vk_service=vk_service)

    result = await monitoring_service.run_monitoring_cycle()
    return result


@router.get(
    "/groups/{group_id}/status", response_model=GroupMonitoringResponse
)
async def get_group_monitoring_status(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> GroupMonitoringResponse:
    """Получить статус мониторинга группы"""
    from sqlalchemy import select

    from app.models.vk_group import VKGroup

    result = await db.execute(select(VKGroup).where(VKGroup.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    return GroupMonitoringResponse(
        group_id=group.id,
        group_name=group.name,
        auto_monitoring_enabled=group.auto_monitoring_enabled,
        monitoring_interval_minutes=group.monitoring_interval_minutes,
        monitoring_priority=group.monitoring_priority,
        next_monitoring_at=group.next_monitoring_at,
        monitoring_runs_count=group.monitoring_runs_count,
        last_monitoring_success=group.last_monitoring_success,
        last_monitoring_error=group.last_monitoring_error,
    )
