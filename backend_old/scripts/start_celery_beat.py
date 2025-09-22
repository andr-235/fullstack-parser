#!/usr/bin/env python3
"""
Скрипт запуска Celery Beat (планировщик)
"""

import os
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.common.celery_config import celery_app

if __name__ == "__main__":
    # Запускаем планировщик
    celery_app.start([
        "beat",
        "--loglevel=info",
        "--scheduler=celery.beat:PersistentScheduler"
    ])
