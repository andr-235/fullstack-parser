import os
from arq.connections import RedisSettings
from app.workers.arq_tasks import run_parsing_task


class WorkerSettings:
    functions = [run_parsing_task]
    redis_settings = RedisSettings.from_dsn(
        os.environ.get("REDIS_URL", "redis://redis:6379/0")
    )
    # Можно добавить on_startup/on_shutdown если потребуется
