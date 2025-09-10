"""
Celery Tasks Service

Сервис с асинхронными задачами для Celery.
Переход с ARQ на более надежную систему очередей.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..celery_app import app

logger = logging.getLogger(__name__)


# Реальная реализация парсинга комментариев VK
async def parse_vk_comments(
    ctx: Dict[str, Any],
    group_id: int,
    post_id: Optional[int] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Реальная реализация парсинга комментариев VK"""
    logger.info(f"🚀 Начало парсинга комментариев для группы {group_id}")

    try:
        # Импортируем необходимые зависимости
        from ..parser.service import ParserService
        from ..vk_api.dependencies import create_vk_api_service_sync
        from ..comments.dependencies import get_comment_repository
        from ..database import get_db_session

        # Создаем VK API сервис с правильным закрытием сессий
        vk_api_service = create_vk_api_service_sync()

        try:
            # Создаем парсер сервис
            parser_service = ParserService(vk_api_service=vk_api_service)

            # Выполняем парсинг группы
            result = await parser_service.parse_group(
                group_id=group_id,
                max_posts=10,  # Ограничиваем количество постов
                max_comments_per_post=limit,
            )
        finally:
            # Закрываем HTTP-сессии
            await vk_api_service.close_sessions()

        logger.info(
            f"✅ Парсинг завершен: {result.get('comments_saved', 0)} комментариев"
        )

        return {
            "status": "success",
            "group_id": group_id,
            "post_id": post_id,
            "comments_parsed": result.get("comments_found", 0),
            "comments_saved": result.get("comments_saved", 0),
            "errors": result.get("errors", []),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка парсинга группы {group_id}: {str(e)}")
        return {
            "status": "error",
            "group_id": group_id,
            "post_id": post_id,
            "comments_parsed": 0,
            "comments_saved": 0,
            "errors": [str(e)],
            "timestamp": datetime.now().isoformat(),
        }


async def analyze_text_morphology(
    ctx: Dict[str, Any], text: str, analysis_type: str = "full"
) -> Dict[str, Any]:
    """Реальная реализация морфологического анализа текста"""
    logger.info(
        f"🔍 Начало морфологического анализа текста (длина: {len(text)} символов)"
    )

    try:
        # Импортируем необходимые зависимости
        from ..nlp.morphology import MorphologyAnalyzer
        from ..database import get_db_session

        # Создаем анализатор морфологии
        analyzer = MorphologyAnalyzer()

        # Выполняем анализ
        result = await analyzer.analyze_text(text, analysis_type)

        logger.info(
            f"✅ Морфологический анализ завершен: {result.get('words_count', 0)} слов"
        )

        return {
            "status": "success",
            "words_count": result.get("words_count", 0),
            "analysis_type": analysis_type,
            "morphology_data": result.get("morphology_data", {}),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка морфологического анализа: {str(e)}")
        return {
            "status": "error",
            "words_count": 0,
            "analysis_type": analysis_type,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def extract_keywords(
    ctx: Dict[str, Any],
    text: str,
    min_frequency: int = 2,
    max_keywords: int = 20,
) -> Dict[str, Any]:
    """Реальная реализация извлечения ключевых слов"""
    logger.info(
        f"🔑 Начало извлечения ключевых слов из текста (длина: {len(text)} символов)"
    )

    try:
        # Импортируем необходимые зависимости
        from ..nlp.keywords import KeywordExtractor
        from ..database import get_db_session

        # Создаем экстрактор ключевых слов
        extractor = KeywordExtractor()

        # Извлекаем ключевые слова
        keywords = await extractor.extract_keywords(
            text=text, min_frequency=min_frequency, max_keywords=max_keywords
        )

        logger.info(
            f"✅ Извлечение ключевых слов завершено: {len(keywords)} слов"
        )

        return {
            "status": "success",
            "keyword_count": len(keywords),
            "keywords": keywords,
            "min_frequency": min_frequency,
            "max_keywords": max_keywords,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка извлечения ключевых слов: {str(e)}")
        return {
            "status": "error",
            "keyword_count": 0,
            "keywords": [],
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def send_notification(
    ctx: Dict[str, Any],
    recipient: str,
    message: str,
    notification_type: str = "email",
) -> Dict[str, Any]:
    """Реальная реализация отправки уведомлений"""
    logger.info(
        f"📧 Начало отправки {notification_type} уведомления для {recipient}"
    )

    try:
        # Импортируем необходимые зависимости
        from ..notifications.service import NotificationService
        from ..database import get_db_session

        # Создаем сервис уведомлений
        notification_service = NotificationService()

        # Отправляем уведомление
        result = await notification_service.send_notification(
            recipient=recipient,
            message=message,
            notification_type=notification_type,
        )

        logger.info(
            f"✅ Уведомление отправлено: {result.get('message_id', 'unknown')}"
        )

        return {
            "status": "success",
            "sent": result.get("sent", False),
            "recipient": recipient,
            "notification_type": notification_type,
            "message_id": result.get("message_id"),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка отправки уведомления: {str(e)}")
        return {
            "status": "error",
            "sent": False,
            "recipient": recipient,
            "notification_type": notification_type,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def generate_report(
    ctx: Dict[str, Any],
    report_type: str,
    date_from: str,
    date_to: str,
    filters: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Реальная реализация генерации отчетов"""
    logger.info(
        f"📊 Начало генерации отчета '{report_type}' с {date_from} по {date_to}"
    )

    try:
        # Импортируем необходимые зависимости
        from ..reports.service import ReportService
        from ..database import get_db_session
        from datetime import datetime

        # Создаем сервис отчетов
        report_service = ReportService()

        # Парсим даты
        date_from_dt = datetime.fromisoformat(date_from)
        date_to_dt = datetime.fromisoformat(date_to)

        # Генерируем отчет
        result = await report_service.generate_report(
            report_type=report_type,
            date_from=date_from_dt,
            date_to=date_to_dt,
            filters=filters or {},
        )

        logger.info(
            f"✅ Отчет сгенерирован: {result.get('file_path', 'unknown')}"
        )

        return {
            "status": "success",
            "generated": True,
            "report_type": report_type,
            "record_count": result.get("record_count", 0),
            "file_path": result.get("file_path"),
            "file_size": result.get("file_size"),
            "date_from": date_from,
            "date_to": date_to,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка генерации отчета: {str(e)}")
        return {
            "status": "error",
            "generated": False,
            "report_type": report_type,
            "record_count": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def cleanup_old_data(
    ctx: Dict[str, Any],
    days_old: int = 30,
    data_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Реальная реализация очистки старых данных"""
    logger.info(f"🧹 Начало очистки данных старше {days_old} дней")

    try:
        # Импортируем необходимые зависимости
        from ..cleanup.service import CleanupService
        from ..database import get_db_session
        from datetime import datetime, timedelta

        # Создаем сервис очистки
        cleanup_service = CleanupService()

        # Вычисляем дату отсечения
        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Выполняем очистку
        result = await cleanup_service.cleanup_old_data(
            cutoff_date=cutoff_date,
            data_types=data_types or ["comments", "logs", "reports"],
        )

        logger.info(
            f"✅ Очистка завершена: {result.get('total_deleted', 0)} записей удалено"
        )

        return {
            "status": "success",
            "total_deleted": result.get("total_deleted", 0),
            "data_types": data_types or ["all"],
            "cutoff_date": cutoff_date.isoformat(),
            "deleted_by_type": result.get("deleted_by_type", {}),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка очистки данных: {str(e)}")
        return {
            "status": "error",
            "total_deleted": 0,
            "data_types": data_types or ["all"],
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def process_batch_comments(
    ctx: Dict[str, Any], comment_ids: List[int], operation: str = "analyze"
) -> Dict[str, Any]:
    """Реальная реализация пакетной обработки комментариев"""
    logger.info(
        f"📦 Начало пакетной обработки {len(comment_ids)} комментариев (операция: {operation})"
    )

    try:
        # Импортируем необходимые зависимости
        from ..comments.service import CommentService
        from ..database import get_db_session

        # Создаем сервис комментариев
        async with get_db_session() as db:
            comment_service = CommentService(db)

            # Выполняем пакетную обработку
            result = await comment_service.process_batch_comments(
                comment_ids=comment_ids, operation=operation
            )

        logger.info(
            f"✅ Пакетная обработка завершена: {result.get('successful', 0)}/{len(comment_ids)} успешно"
        )

        return {
            "status": "success",
            "total_comments": len(comment_ids),
            "successful": result.get("successful", 0),
            "failed": result.get("failed", 0),
            "operation": operation,
            "errors": result.get("errors", []),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка пакетной обработки комментариев: {str(e)}")
        return {
            "status": "error",
            "total_comments": len(comment_ids),
            "successful": 0,
            "failed": len(comment_ids),
            "operation": operation,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def update_statistics(
    ctx: Dict[str, Any], stat_type: str = "daily"
) -> Dict[str, Any]:
    """Реальная реализация обновления статистики"""
    logger.info(f"📈 Начало обновления {stat_type} статистики")

    try:
        # Импортируем необходимые зависимости
        from ..statistics.service import StatisticsService
        from ..database import get_db_session

        # Создаем сервис статистики
        async with get_db_session() as db:
            stats_service = StatisticsService(db)

            # Обновляем статистику
            result = await stats_service.update_statistics(stat_type=stat_type)

        logger.info(
            f"✅ Статистика обновлена: {result.get('records_updated', 0)} записей"
        )

        return {
            "status": "success",
            "updated": True,
            "stat_type": stat_type,
            "records_updated": result.get("records_updated", 0),
            "statistics_data": result.get("statistics_data", {}),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка обновления статистики: {str(e)}")
        return {
            "status": "error",
            "updated": False,
            "stat_type": stat_type,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def backup_database(
    ctx: Dict[str, Any], backup_type: str = "full"
) -> Dict[str, Any]:
    """Реальная реализация создания резервной копии базы данных"""
    logger.info(f"💾 Начало создания {backup_type} бэкапа базы данных")

    try:
        # Импортируем необходимые зависимости
        from ..backup.service import BackupService
        from ..database import get_db_session

        # Создаем сервис резервного копирования
        backup_service = BackupService()

        # Создаем резервную копию
        result = await backup_service.create_backup(backup_type=backup_type)

        logger.info(
            f"✅ Резервная копия создана: {result.get('file_path', 'unknown')}"
        )

        return {
            "status": "success",
            "created": True,
            "backup_type": backup_type,
            "file_path": result.get("file_path"),
            "file_size": result.get("file_size"),
            "compression_ratio": result.get("compression_ratio"),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка создания резервной копии: {str(e)}")
        return {
            "status": "error",
            "created": False,
            "backup_type": backup_type,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# Обновляем функции для работы с Celery
async def parse_vk_comments_celery(
    ctx: Dict[str, Any],
    group_id: int,
    post_id: Optional[int] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await parse_vk_comments(ctx, group_id, post_id, limit)


async def analyze_text_morphology_celery(
    ctx: Dict[str, Any], text: str, analysis_type: str = "full"
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await analyze_text_morphology(ctx, text, analysis_type)


async def extract_keywords_celery(
    ctx: Dict[str, Any],
    text: str,
    min_frequency: int = 2,
    max_keywords: int = 20,
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await extract_keywords(ctx, text, min_frequency, max_keywords)


async def send_notification_celery(
    ctx: Dict[str, Any],
    recipient: str,
    message: str,
    notification_type: str = "email",
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await send_notification(ctx, recipient, message, notification_type)


async def generate_report_celery(
    ctx: Dict[str, Any],
    report_type: str,
    date_from: str,
    date_to: str,
    filters: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await generate_report(ctx, report_type, date_from, date_to, filters)


async def cleanup_old_data_celery(
    ctx: Dict[str, Any],
    days_old: int = 30,
    data_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await cleanup_old_data(ctx, days_old, data_types)


async def process_batch_comments_celery(
    ctx: Dict[str, Any], comment_ids: List[int], operation: str = "analyze"
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await process_batch_comments(ctx, comment_ids, operation)


async def update_statistics_celery(
    ctx: Dict[str, Any], stat_type: str = "daily"
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await update_statistics(ctx, stat_type)


async def backup_database_celery(
    ctx: Dict[str, Any], backup_type: str = "full"
) -> Dict[str, Any]:
    """Адаптер для работы с Celery"""
    return await backup_database(ctx, backup_type)


# Определяем Celery задачи
@app.task(bind=True, name="celery_tasks.parse_vk_comments")
def parse_vk_comments_task(
    self, group_id: int, post_id: Optional[int] = None, limit: int = 100
) -> Dict[str, Any]:
    """
    Задача Celery для парсинга комментариев VK

    Args:
        group_id: ID группы VK
        post_id: ID поста (опционально)
        limit: Максимальное количество комментариев

    Returns:
        Dict с результатами парсинга
    """
    import asyncio

    try:
        logger.info(f"🚀 Начало парсинга комментариев для группы {group_id}")

        # Имитируем контекст ARQ для совместимости
        ctx: Dict[str, Any] = {}

        # Запускаем асинхронную функцию
        result = asyncio.run(
            parse_vk_comments_celery(ctx, group_id, post_id, limit)
        )

        logger.info(
            f"✅ Парсинг завершен: {result.get('comments_parsed', 0)} комментариев"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка парсинга комментариев: {e}")
        raise self.retry(countdown=60, exc=e)


@app.task(bind=True, name="celery_tasks.analyze_text_morphology")
def analyze_text_morphology_task(
    self, text: str, analysis_type: str = "full"
) -> Dict[str, Any]:
    """
    Задача Celery для морфологического анализа текста
    """
    import asyncio

    try:
        logger.info(
            f"🔍 Начало морфологического анализа текста (длина: {len(text)} символов)"
        )

        ctx: Dict[str, Any] = {}
        result = asyncio.run(
            analyze_text_morphology_celery(ctx, text, analysis_type)
        )

        logger.info(
            f"✅ Морфологический анализ завершен для {result.get('words_count', 0)} слов"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка морфологического анализа: {e}")
        raise self.retry(countdown=30, exc=e)


@app.task(bind=True, name="celery_tasks.extract_keywords")
def extract_keywords_task(
    self, text: str, min_frequency: int = 2, max_keywords: int = 20
) -> Dict[str, Any]:
    """
    Задача Celery для извлечения ключевых слов
    """
    import asyncio

    try:
        logger.info(
            f"🔑 Начало извлечения ключевых слов (мин. частота: {min_frequency})"
        )

        ctx: Dict[str, Any] = {}
        result = asyncio.run(
            extract_keywords_celery(ctx, text, min_frequency, max_keywords)
        )

        logger.info(
            f"✅ Извлечено {result.get('keyword_count', 0)} ключевых слов"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка извлечения ключевых слов: {e}")
        raise self.retry(countdown=30, exc=e)


@app.task(bind=True, name="celery_tasks.send_notification")
def send_notification_task(
    self, recipient: str, message: str, notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Задача Celery для отправки уведомлений
    """
    import asyncio

    try:
        logger.info(
            f"📧 Отправка {notification_type} уведомления для {recipient}"
        )

        ctx: Dict[str, Any] = {}
        result = asyncio.run(
            send_notification_celery(
                ctx, recipient, message, notification_type
            )
        )

        if result.get("sent"):
            logger.info(f"✅ Уведомление успешно отправлено {recipient}")
        else:
            logger.warning(
                f"⚠️ Ошибка отправки уведомления {recipient}: {result.get('error')}"
            )

        return result

    except Exception as e:
        logger.error(f"❌ Ошибка отправки уведомления: {e}")
        raise self.retry(countdown=60, exc=e)


@app.task(bind=True, name="celery_tasks.generate_report")
def generate_report_task(
    self,
    report_type: str,
    date_from: str,
    date_to: str,
    filters: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Задача Celery для генерации отчетов
    """
    import asyncio

    try:
        logger.info(
            f"📊 Генерация отчета '{report_type}' за период {date_from} - {date_to}"
        )

        ctx: Dict[str, Any] = {}
        result = asyncio.run(
            generate_report_celery(
                ctx, report_type, date_from, date_to, filters
            )
        )

        if result.get("generated"):
            logger.info(f"✅ Отчет '{report_type}' сгенерирован")
        else:
            logger.warning(f"⚠️ Отчет '{report_type}' не был сгенерирован")

        return result

    except Exception as e:
        logger.error(f"❌ Ошибка генерации отчета '{report_type}': {e}")
        raise self.retry(countdown=120, exc=e)


@app.task(bind=True, name="celery_tasks.cleanup_old_data")
def cleanup_old_data_task(
    self, days_old: int = 30, data_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Задача Celery для очистки старых данных
    """
    import asyncio

    try:
        logger.info(f"🧹 Очистка данных старше {days_old} дней")

        ctx: Dict[str, Any] = {}
        result = asyncio.run(
            cleanup_old_data_celery(ctx, days_old, data_types)
        )

        logger.info(
            f"✅ Очистка завершена: удалено {result.get('total_deleted', 0)} записей"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка очистки данных: {e}")
        raise self.retry(countdown=300, exc=e)


@app.task(bind=True, name="celery_tasks.process_batch_comments")
def process_batch_comments_task(
    self, comment_ids: List[int], operation: str = "analyze"
) -> Dict[str, Any]:
    """
    Задача Celery для пакетной обработки комментариев
    """
    import asyncio

    try:
        logger.info(
            f"📦 Пакетная обработка {len(comment_ids)} комментариев (операция: {operation})"
        )

        ctx: Dict[str, Any] = {}
        result = asyncio.run(
            process_batch_comments_celery(ctx, comment_ids, operation)
        )

        logger.info(
            f"✅ Пакетная обработка завершена: {result.get('successful', 0)}/{result.get('total_comments', 0)} успешно"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка пакетной обработки комментариев: {e}")
        raise self.retry(countdown=60, exc=e)


@app.task(bind=True, name="celery_tasks.update_statistics")
def update_statistics_task(self, stat_type: str = "daily") -> Dict[str, Any]:
    """
    Задача Celery для обновления статистики
    """
    import asyncio

    try:
        logger.info(f"📈 Обновление {stat_type} статистики")

        ctx: Dict[str, Any] = {}
        result = asyncio.run(update_statistics_celery(ctx, stat_type))

        logger.info(f"✅ Статистика '{stat_type}' обновлена")
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка обновления статистики '{stat_type}': {e}")
        raise self.retry(countdown=120, exc=e)


@app.task(bind=True, name="celery_tasks.backup_database")
def backup_database_task(self, backup_type: str = "full") -> Dict[str, Any]:
    """
    Задача Celery для создания резервной копии базы данных
    """
    import asyncio

    try:
        logger.info(f"💾 Создание {backup_type} бэкапа базы данных")

        ctx: Dict[str, Any] = {}
        result = asyncio.run(backup_database_celery(ctx, backup_type))

        if result.get("created"):
            logger.info(f"✅ Бэкап создан")
        else:
            logger.warning(f"⚠️ Бэкап не был создан")

        return result

    except Exception as e:
        logger.error(f"❌ Ошибка создания бэкапа: {e}")
        raise self.retry(countdown=600, exc=e)


# Экспорт всех задач
__all__ = [
    "parse_vk_comments_task",
    "analyze_text_morphology_task",
    "extract_keywords_task",
    "send_notification_task",
    "generate_report_task",
    "cleanup_old_data_task",
    "process_batch_comments_task",
    "update_statistics_task",
    "backup_database_task",
]
