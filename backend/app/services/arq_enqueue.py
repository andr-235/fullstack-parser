from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings


async def enqueue_run_parsing_task(
    group_id: int,
    max_posts: int | None = None,
    force_reparse: bool = False,
    job_id: str | None = None,
):
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    job = await redis.enqueue_job(
        "run_parsing_task", group_id, max_posts, force_reparse, _job_id=job_id
    )
    if job is not None:
        print(
            f"[ENQUEUE] Задача поставлена: job_id={job.job_id}, status={await job.status()}"
        )
    else:
        print(
            f"[ENQUEUE] Задача с таким job_id уже есть в очереди или выполняется: job_id={job_id}"
        )
