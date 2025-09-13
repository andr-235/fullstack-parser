"""
Логирование
"""

import logging
import sys


def get_logger(name: str = None) -> logging.Logger:
    """Получить логгер"""
    logger = logging.getLogger(name or __name__)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler = logging.StreamHandler(sys.stderr)  # Используем stderr для ошибок
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)  # Увеличиваем уровень логирования

    return logger


def setup_logging():
    """Настроить логирование для всего приложения"""
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Очищаем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Обработчик для stdout (INFO и выше)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(lambda record: record.levelno >= logging.INFO)
    
    # Обработчик для stderr (ERROR и выше)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)
    stderr_handler.addFilter(lambda record: record.levelno >= logging.ERROR)
    
    # Добавляем обработчики
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)
    
    # Настраиваем uvicorn логирование
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    # Настраиваем fastapi логирование
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
