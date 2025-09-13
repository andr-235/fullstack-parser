#!/usr/bin/env python3
"""
Скрипт запуска Flower (мониторинг Celery)
"""

import os
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.celery_config import celery_app

if __name__ == "__main__":
    # Запускаем Flower
    celery_app.start([
        "flower",
        "--port=5555",
        "--broker=redis://localhost:6379/0",
        "--basic_auth=admin:admin"
    ])
