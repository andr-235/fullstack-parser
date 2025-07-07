import asyncio
from app.core.database import AsyncSessionLocal
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import get_redis_parser_manager
from app.services.vk_api_service import VKAPIService


async def run_parsing_task(
    ctx, group_id: int, max_posts: int | None = None, force_reparse: bool = False
):
    """
    Асинхронная задача Arq для парсинга постов группы.
    ctx — служебный контекст Arq (можно расширить через on_startup)
    """
    task_id = ctx["job_id"] if "job_id" in ctx else None
    redis_manager = get_redis_parser_manager()

    async def progress_callback(progress: float):
        res = redis_manager.update_task_progress(task_id, progress)
        if asyncio.iscoroutine(res):
            await res

    async with AsyncSessionLocal() as db:
        parser_service = ParserService(db=db, vk_api=VKAPIService())
        try:
            stats = await parser_service.parse_group_posts(
                group_id=group_id,
                max_posts_count=max_posts,
                force_reparse=force_reparse,
                progress_callback=progress_callback,
            )
            # Явно закрываем redis_manager, если есть метод close
            if hasattr(redis_manager, "close") and callable(redis_manager.close):
                close_result = redis_manager.close()
                if asyncio.iscoroutine(close_result):
                    await close_result
            res = redis_manager.complete_task(task_id, stats.model_dump())
            if asyncio.iscoroutine(res):
                await res
            return stats.model_dump()
        except Exception as e:
            error_message = str(e)
            res = redis_manager.fail_task(task_id, error_message)
            if asyncio.iscoroutine(res):
                await res
            raise
