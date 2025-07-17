import os

from arq.connections import RedisSettings

from app.workers.arq_tasks import run_monitoring_cycle, run_parsing_task


class WorkerSettings:
    functions = [run_parsing_task, run_monitoring_cycle]
    redis_settings = RedisSettings.from_dsn(
        os.environ.get("REDIS_URL", "redis://redis:6379/0")
    )
    # Ограничения для предотвращения высокого потребления CPU
    max_jobs = 1  # Максимум 1 задача одновременно
    job_timeout = 300  # Таймаут задачи 5 минут
    keep_result = 60  # Хранить результат 1 минуту
    poll_delay = 1.0  # Задержка между проверками задач
    max_tries = 3  # Максимум 3 попытки для задачи
