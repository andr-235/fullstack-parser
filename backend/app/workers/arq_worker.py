from arq.connections import RedisSettings
from backend.app.workers.arq_tasks import run_parsing_task


class WorkerSettings:
    functions = [run_parsing_task]
    redis_settings = RedisSettings()
    # Можно добавить on_startup/on_shutdown если потребуется
