"""
ARQ задачи для фоновой обработки
"""

from datetime import datetime, timezone
from typing import Any, Dict

import structlog

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.monitoring_service import MonitoringService
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import get_redis_parser_manager
from app.services.scheduler_service import SchedulerService
from app.services.vkbottle_service import VKBottleService

logger = structlog.get_logger(__name__)


async def run_parsing_task(
    ctx: Dict[str, Any],
    group_id: int,
    max_posts: int | None = None,
    force_reparse: bool = False,
) -> Dict[str, Any]:
    """
    Задача парсинга группы VK

    Args:
        ctx: Контекст ARQ
        group_id: ID группы для парсинга
        max_posts: Максимальное количество постов
        force_reparse: Принудительный перепарсинг

    Returns:
        Результат выполнения задачи
    """
    start_time = datetime.now(timezone.utc)
    task_id = ctx.get("job_id")

    logger.info(
        "Запуск задачи парсинга",
        task_id=task_id,
        group_id=group_id,
        max_posts=max_posts,
        force_reparse=force_reparse,
    )

    try:
        # Получаем зависимости
        redis_manager = get_redis_parser_manager()
        vk_service = VKBottleService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

        # Создаем сессию БД
        async with AsyncSessionLocal() as db:
            parser_service = ParserService(db, vk_service)

            # Запускаем парсинг
            stats = await parser_service.parse_group_posts(
                group_id=group_id,
                max_posts_count=max_posts,
                force_reparse=force_reparse,
                task_id=task_id,
            )

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info(
            "Задача парсинга завершена успешно",
            task_id=task_id,
            group_id=group_id,
            duration=duration,
            stats=stats.model_dump(),
        )

        return {
            "status": "success",
            "group_id": group_id,
            "duration": duration,
            "stats": stats.model_dump(),
        }

    except Exception as e:
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.error(
            "Ошибка выполнения задачи парсинга",
            task_id=task_id,
            group_id=group_id,
            duration=duration,
            error=str(e),
            exc_info=True,
        )

        return {
            "status": "error",
            "group_id": group_id,
            "duration": duration,
            "error": str(e),
        }


async def run_monitoring_cycle(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Задача мониторинга групп VK

    Args:
        ctx: Контекст ARQ

    Returns:
        Результат выполнения задачи
    """
    start_time = datetime.now(timezone.utc)
    task_id = ctx.get("job_id")

    logger.info("Запуск цикла мониторинга", task_id=task_id)

    try:
        # Получаем зависимости
        redis_manager = get_redis_parser_manager()
        vk_service = VKBottleService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

        # Создаем сессию БД
        async with AsyncSessionLocal() as db:
            monitoring_service = MonitoringService(
                db, vk_service, redis_manager
            )
            scheduler_service = SchedulerService(db)

            # Запускаем мониторинг
            result = await monitoring_service.run_monitoring_cycle()

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info(
            "Цикл мониторинга завершен успешно",
            task_id=task_id,
            duration=duration,
            result=result,
        )

        return {
            "status": "success",
            "duration": duration,
            "result": result,
        }

    except Exception as e:
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.error(
            "Ошибка выполнения цикла мониторинга",
            task_id=task_id,
            duration=duration,
            error=str(e),
            exc_info=True,
        )

        return {
            "status": "error",
            "duration": duration,
            "error": str(e),
        }


async def run_scheduler_task(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Задача планировщика для запуска мониторинга

    Args:
        ctx: Контекст ARQ

    Returns:
        Результат выполнения задачи
    """
    start_time = datetime.now(timezone.utc)
    task_id = ctx.get("job_id")

    logger.info("Запуск задачи планировщика", task_id=task_id)

    try:
        # Получаем зависимости
        redis_manager = get_redis_parser_manager()

        # Создаем сессию БД
        async with AsyncSessionLocal() as db:
            scheduler_service = SchedulerService(db)

            # Проверяем и запускаем задачи мониторинга
            result = await scheduler_service.process_scheduled_tasks(
                redis_manager
            )

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info(
            "Задача планировщика завершена успешно",
            task_id=task_id,
            duration=duration,
            result=result,
        )

        return {
            "status": "success",
            "duration": duration,
            "result": result,
        }

    except Exception as e:
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.error(
            "Ошибка выполнения задачи планировщика",
            task_id=task_id,
            duration=duration,
            error=str(e),
            exc_info=True,
        )

        return {
            "status": "error",
            "duration": duration,
            "error": str(e),
        }


class WorkerSettings:
    """Настройки ARQ воркера"""

    functions = [
        run_parsing_task,
        run_monitoring_cycle,
        run_scheduler_task,
    ]

    redis_settings = settings.redis_url
    max_jobs = 10
    job_timeout = 3600  # 1 час
    keep_result = 3600  # Хранить результат 1 час
    max_tries = 3
    retry_delay = 60  # 1 минута между попытками
