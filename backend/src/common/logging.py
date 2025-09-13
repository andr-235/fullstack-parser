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
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
