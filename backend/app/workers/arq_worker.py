import os
from pathlib import Path

from arq.connections import RedisSettings

from app.workers.arq_tasks import (
    run_monitoring_cycle,
    run_parsing_task,
    run_scheduler_task,
)

# Загружаем переменные окружения из .env.dev если находимся в dev режиме
if os.getenv("ENV") == "development":
    env_file = Path(__file__).parent.parent.parent.parent / ".env.dev"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = value


class WorkerSettings:
    functions = [run_parsing_task, run_monitoring_cycle, run_scheduler_task]
    redis_settings = RedisSettings.from_dsn(
        os.environ.get("REDIS_URL", "redis://redis:6379/0")
    )
    # Ограничения для предотвращения высокого потребления CPU

    max_jobs = int(
        os.environ.get("ARQ_MAX_JOBS", 5)
    )  # Максимум 5 задач одновременно
    job_timeout = int(
        os.environ.get("ARQ_JOB_TIMEOUT", 1800)
    )  # Таймаут задачи 30 минут
    keep_result = int(
        os.environ.get("ARQ_KEEP_RESULT", 3600)
    )  # Хранить результат 1 час
    poll_delay = float(
        os.environ.get("ARQ_POLL_DELAY", 1.0)
    )  # Задержка между проверками задач
    max_tries = int(
        os.environ.get("ARQ_MAX_TRIES", 3)
    )  # Максимум 3 попытки для задачи
    retry_delay = int(
        os.environ.get("ARQ_RETRY_DELAY", 60)
    )  # Задержка между попытками 1 минута
