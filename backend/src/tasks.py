"""
Celery Tasks

Задачи для фоновой обработки в приложении VK Parser.
Замена для ARQ - более надежная система.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .celery_app import app
from .celery_tasks.service import (
    parse_vk_comments_task,
    analyze_text_morphology_task,
    extract_keywords_task,
    send_notification_task,
    generate_report_task,
    cleanup_old_data_task,
    process_batch_comments_task,
    update_statistics_task,
    backup_database_task,
)

logger = logging.getLogger(__name__)


# Вспомогательные функции для вызова задач
def enqueue_parse_vk_comments(
    group_id: int, post_id: Optional[int] = None, limit: int = 100
):
    """Добавление задачи парсинга в очередь"""
    return parse_vk_comments_task.delay(group_id, post_id, limit)


def enqueue_analyze_text(text: str, analysis_type: str = "full"):
    """Добавление задачи анализа текста в очередь"""
    return analyze_text_morphology_task.delay(text, analysis_type)


def enqueue_extract_keywords(
    text: str, min_frequency: int = 2, max_keywords: int = 20
):
    """Добавление задачи извлечения ключевых слов в очередь"""
    return extract_keywords_task.delay(text, min_frequency, max_keywords)


def enqueue_send_notification(
    recipient: str, message: str, notification_type: str = "email"
):
    """Добавление задачи отправки уведомления в очередь"""
    return send_notification_task.delay(recipient, message, notification_type)


def enqueue_generate_report(
    report_type: str,
    date_from: str,
    date_to: str,
    filters: Optional[Dict] = None,
):
    """Добавление задачи генерации отчета в очередь"""
    return generate_report_task.delay(report_type, date_from, date_to, filters)


def enqueue_cleanup_old_data(
    days_old: int = 30, data_types: Optional[List[str]] = None
):
    """Добавление задачи очистки данных в очередь"""
    return cleanup_old_data_task.delay(days_old, data_types)


def enqueue_process_batch_comments(
    comment_ids: List[int], operation: str = "analyze"
):
    """Добавление задачи пакетной обработки в очередь"""
    return process_batch_comments_task.delay(comment_ids, operation)


def enqueue_update_statistics(stat_type: str = "daily"):
    """Добавление задачи обновления статистики в очередь"""
    return update_statistics_task.delay(stat_type)


def enqueue_backup_database(backup_type: str = "full"):
    """Добавление задачи создания бэкапа в очередь"""
    return backup_database_task.delay(backup_type)
