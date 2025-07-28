#!/usr/bin/env python3
"""
Скрипт для запуска планировщика автоматического мониторинга
"""

import asyncio
import signal
import sys
from datetime import datetime, timezone

import structlog
from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings
from app.services.monitoring_service import MonitoringService
from app.services.vk_api_service import VKAPIService
from app.core.database import AsyncSessionLocal

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
        # Инициализируем Redis pool
        redis_pool = await create_pool(
            RedisSettings.from_dsn(settings.redis_url)
        )
        logger.info("✅ Подключение к Redis установлено")

        # Получаем интервал мониторинга
        monitoring_interval = getattr(
            settings, "monitoring_interval_seconds", 300
        )

        logger.info(
            "⏰ Планировщик запущен",
            interval_seconds=monitoring_interval,
            start_time=datetime.now(timezone.utc).isoformat(),
        )

        # Основной цикл планировщика
        while True:
            try:
                logger.info("🔄 Запуск цикла мониторинга")

                # Создаем сессию БД
                async with AsyncSessionLocal() as db:
                    # Инициализируем сервисы
                    vk_service = VKAPIService(
                        token=settings.vk.access_token,
                        api_version=settings.vk.api_version,
                    )
                    monitoring_service = MonitoringService(db, vk_service)

                    # Запускаем цикл мониторинга
                    result = await monitoring_service.run_monitoring_cycle()

                    logger.info("✅ Цикл мониторинга завершен", result=result)

                # Ждем до следующего цикла
                logger.info(
                    f"⏳ Ожидание {monitoring_interval} секунд до следующего цикла"
                )
                await asyncio.sleep(monitoring_interval)

            except Exception as e:
                logger.error(
                    "💥 Ошибка в цикле мониторинга",
                    error=str(e),
                    exc_info=True,
                )
                # Ждем 60 секунд перед повторной попыткой
                await asyncio.sleep(60)

    except KeyboardInterrupt:
        logger.info("🛑 Планировщик остановлен пользователем")
    except Exception as e:
        logger.error(
            "💥 Критическая ошибка планировщика", error=str(e), exc_info=True
        )
        sys.exit(1)
    finally:
        if "redis_pool" in locals():
            await redis_pool.close()
            logger.info("🔌 Соединение с Redis закрыто")


if __name__ == "__main__":
    asyncio.run(main())
