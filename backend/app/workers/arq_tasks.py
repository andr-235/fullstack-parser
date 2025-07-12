import asyncio
import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import get_redis_parser_manager
from app.services.vkbottle_service import VKBottleService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arq.worker")


async def run_parsing_task(
    ctx, group_id: int, max_posts: int | None = None, force_reparse: bool = False
):
    """
    Асинхронная задача Arq для парсинга постов группы.
    ctx — служебный контекст Arq (можно расширить через on_startup)
    """
    logger.info(
        f"[ARQ] Запущена задача run_parsing_task: group_id={group_id}, max_posts={max_posts}, force_reparse={force_reparse}"
    )
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
                logger.info(f"[ARQ] VK_ACCESS_TOKEN начинается с: {vk_token[:8]}...")
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
            if hasattr(redis_manager, "close") and callable(redis_manager.close):
                close_result = redis_manager.close()
                if asyncio.iscoroutine(close_result):
                    await close_result
            res = redis_manager.complete_task(task_id, stats.model_dump())
            if asyncio.iscoroutine(res):
                await res
            logger.info(
                f"[ARQ] Задача run_parsing_task завершена успешно: group_id={group_id}"
            )
            return stats.model_dump()
    except Exception as e:
        logger.error(f"[ARQ] Ошибка в run_parsing_task: {e}", exc_info=True)
        error_message = str(e)
        res = redis_manager.fail_task(task_id, error_message)
        if asyncio.iscoroutine(res):
            await res
        raise
