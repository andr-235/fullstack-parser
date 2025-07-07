# Тут будут задачи для Celery

import asyncio
from celery.utils.log import get_task_logger

from app.core.database import AsyncSessionLocal
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import get_redis_parser_manager
from app.services.vk_api_service import VKAPIService
from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
async def run_parsing_task(
    self, group_id: int, max_posts: int | None = None, force_reparse: bool = False
):
    """
    Асинхронная задача Celery для парсинга постов группы.
    """
    task_id = self.request.id
    logger.info(f"Starting parsing task {task_id} for group {group_id}")

    redis_manager = get_redis_parser_manager()

    async def progress_callback(progress: float):
        await redis_manager.update_task_progress(task_id, progress)

    try:
        async with AsyncSessionLocal() as db:
            parser_service = ParserService(db=db, vk_api=VKAPIService())
            stats = await parser_service.parse_group_posts(
                group_id=group_id,
                max_posts_count=max_posts,
                force_reparse=force_reparse,
                progress_callback=progress_callback,
            )
        await redis_manager.complete_task(task_id, stats.model_dump())
        logger.info(f"Task {task_id} completed successfully.")
        return stats.model_dump()
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        error_message = str(e)
        await redis_manager.fail_task(task_id, error_message)
        self.update_state(state="FAILURE", meta={"error": error_message})
        raise
