#!/usr/bin/env python3
"""
Скрипт запуска Celery воркера
"""

import os
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.celery_config import celery_app

if __name__ == "__main__":
    # Запускаем воркер
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--queues=default,parser,notifications,high_priority,low_priority",
        "--hostname=worker@%h"
    ])
