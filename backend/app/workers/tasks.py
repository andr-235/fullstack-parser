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
def run_parsing_task(
    self,
    group_id: int,
    max_posts: int | None = None,
    force_reparse: bool = False,
):
    """
    Синхронная задача Celery для парсинга постов группы.
    ВАЖНО: Сессия базы данных создаётся внутри задачи (DI),
    чтобы избежать ошибок параллельного доступа (asyncpg InterfaceError).
    """
    task_id = self.request.id
    logger.info(f"Starting parsing task {task_id} for group {group_id}")

    redis_manager = get_redis_parser_manager()

    async def progress_callback(progress: float):
        res = redis_manager.update_task_progress(task_id, progress)
        if asyncio.iscoroutine(res):
            await res

    def sync_parse():
        async def inner():
            async with AsyncSessionLocal() as db:
                parser_service = ParserService(db=db, vk_api=VKAPIService())
                stats = await parser_service.parse_group_posts(
                    group_id=group_id,
                    max_posts_count=max_posts,
                    force_reparse=force_reparse,
                    progress_callback=progress_callback,
                )

                # Явно закрываем redis_manager, если есть метод close
                if hasattr(redis_manager, "close") and callable(
                    redis_manager.close
                ):
                    close_result = redis_manager.close()
                    if asyncio.iscoroutine(close_result):
                        await close_result
                return stats.model_dump()

        return asyncio.run(inner())

    try:
        stats = sync_parse()
        res = redis_manager.complete_task(task_id, stats)
        if asyncio.iscoroutine(res):
            asyncio.run(res)
        logger.info(f"Task {task_id} completed successfully.")
        return stats
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        error_message = str(e)
        res = redis_manager.fail_task(task_id, error_message)
        if asyncio.iscoroutine(res):
            asyncio.run(res)
        raise e
