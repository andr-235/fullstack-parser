from celery import Celery, Task
from app.core.config import settings
import asyncio


class AsyncTask(Task):
    """
    Кастомный класс задачи для поддержки `async` функций.
    Обеспечивает корректное управление циклом событий asyncio для каждой задачи.
    """

    def __call__(self, *args, **kwargs):
        if asyncio.iscoroutinefunction(self.run):
            # Если задача - это корутина, запускаем ее в новом цикле событий
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.run(*args, **kwargs))
            finally:
                loop.close()
        # Для обычных синхронных задач вызываем стандартный обработчик
        return super().__call__(*args, **kwargs)


celery_app = Celery(
    "worker",
    task_cls=AsyncTask,
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
)
