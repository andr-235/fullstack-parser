"""
Модуль конфигурации структурированного логирования с использованием structlog.
"""

import logging
import sys

import structlog
from structlog.types import Processor


def setup_logging(log_level: str = "INFO", json_logs: bool = False):
    """
    Настраивает структурированное логирование для всего приложения.
    """
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    log_renderer: Processor
    if json_logs:
        log_renderer = structlog.processors.JSONRenderer()
    else:
        log_renderer = structlog.dev.ConsoleRenderer(colors=True)

    processors: list[Processor] = shared_processors + [log_renderer]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Настройка стандартного логгера для перехвата логов из других библиотек
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Настройка логов для uvicorn
    logging.getLogger("uvicorn.access").disabled = True
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.propagate = True
    uvicorn_error.level = getattr(logging, log_level.upper())


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Возвращает экземпляр логгера.
    """
    return structlog.get_logger(name)
