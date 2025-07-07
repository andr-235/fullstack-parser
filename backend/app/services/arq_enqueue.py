from arq import create_pool
from arq.connections import RedisSettings

async def enqueue_run_parsing_task(group_id: int, max_posts: int | None = None, force_reparse: bool = False, job_id: str | None = None):
    redis = await create_pool(RedisSettings())
    await redis.enqueue_job(
        'run_parsing_task',
        group_id,
        max_posts,
        force_reparse,
        _job_id=job_id
    ) 