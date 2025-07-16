import asyncio

import structlog

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.monitoring_service import MonitoringService
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import get_redis_parser_manager
from app.services.vkbottle_service import VKBottleService

logger = structlog.get_logger(__name__)


async def run_parsing_task(
    ctx,
    group_id: int,
    max_posts: int | None = None,
    force_reparse: bool = False,
):
    """
    Задача для парсинга постов группы
    """
    logger.info(f"[ARQ] Запуск задачи парсинга для группы {group_id}")

    try:
        task_id = ctx["job_id"] if "job_id" in ctx else None
        redis_manager = get_redis_parser_manager()

        async def progress_callback(progress: float):
            res = redis_manager.update_task_progress(task_id, progress)
            if asyncio.iscoroutine(res):
                await res

        async with AsyncSessionLocal() as db:
            vk_token = settings.vk_access_token
            if not vk_token or vk_token == "your-vk-app-id":
                logger.warning(
                    f"[ARQ] VK_ACCESS_TOKEN не передан или дефолтный: {vk_token}"
                )
            else:
                logger.info(
                    f"[ARQ] VK_ACCESS_TOKEN начинается с: {vk_token[:8]}..."
                )
            logger.warning(
                f"[ARQ] VK_ACCESS_TOKEN (repr): {repr(settings.vk_access_token)}"
            )
            logger.warning(
                f"[ARQ] VK_ACCESS_TOKEN из settings: {settings.vk_access_token[:8]}..."
            )
            parser_service = ParserService(
                db=db,
                vk_service=VKBottleService(
                    token=vk_token, api_version=settings.vk_api_version
                ),
            )
            stats = await parser_service.parse_group_posts(
                group_id=group_id,
                max_posts_count=max_posts,
                force_reparse=force_reparse,
                progress_callback=progress_callback,
                task_id=task_id,
            )
            # Явно закрываем redis_manager, если есть метод close
            if hasattr(redis_manager, "close") and callable(
                redis_manager.close
            ):
                close_result = redis_manager.close()
                if asyncio.iscoroutine(close_result):
                    await close_result
            res = redis_manager.complete_task(task_id, stats.model_dump())
            if asyncio.iscoroutine(res):
                await res
            logger.info(f"[ARQ] Задача парсинга завершена успешно: {task_id}")
            return stats.model_dump()

    except Exception as e:
        logger.error(f"[ARQ] Ошибка задачи парсинга: {e}", exc_info=True)
        if "task_id" in locals():
            redis_manager = get_redis_parser_manager()
            res = redis_manager.fail_task(task_id, str(e))
            if asyncio.iscoroutine(res):
                await res
        raise e


async def run_monitoring_cycle(ctx):
    """
    Задача для запуска цикла автоматического мониторинга всех групп
    """
    logger.info("[ARQ] Запуск цикла автоматического мониторинга")

    try:
        async with AsyncSessionLocal() as db:
            vk_token = settings.vk_access_token
            if not vk_token:
                logger.error("[ARQ] VK_ACCESS_TOKEN не настроен")
                return {"error": "VK_ACCESS_TOKEN не настроен"}

            vk_service = VKBottleService(
                token=vk_token, api_version=settings.vk_api_version
            )

            monitoring_service = MonitoringService(
                db=db, vk_service=vk_service
            )

            # Запускаем цикл мониторинга
            stats = await monitoring_service.run_monitoring_cycle()

            logger.info("[ARQ] Цикл мониторинга завершён", **stats)

            return stats

    except Exception as e:
        logger.error(
            "[ARQ] Ошибка цикла мониторинга", error=str(e), exc_info=True
        )
        return {"error": str(e)}
