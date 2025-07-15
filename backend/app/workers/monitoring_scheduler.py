#!/usr/bin/env python3
"""
Скрипт для запуска планировщика автоматического мониторинга
"""

import asyncio
import signal
import sys
from datetime import datetime, timezone

import structlog

from app.core.config import settings
from app.services.scheduler_service import start_background_scheduler

logger = structlog.get_logger(__name__)


async def main():
    """Основная функция запуска планировщика"""
    logger.info("🚀 Запуск планировщика автоматического мониторинга")

    # Настройка обработчика сигналов для graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"📡 Получен сигнал {signum}, завершение работы...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Запускаем планировщик с интервалом 5 минут
        monitoring_interval = getattr(
            settings, "monitoring_interval_seconds", 300
        )

        logger.info(
            "⏰ Планировщик запущен",
            interval_seconds=monitoring_interval,
            start_time=datetime.now(timezone.utc).isoformat(),
        )

        await start_background_scheduler(monitoring_interval)

    except KeyboardInterrupt:
        logger.info("🛑 Планировщик остановлен пользователем")
    except Exception as e:
        logger.error(
            "💥 Критическая ошибка планировщика", error=str(e), exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
