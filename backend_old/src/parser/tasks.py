"""
Задачи парсера VK
"""

import asyncio
from typing import Any, Dict, List, Optional

from celery import Task
from celery.exceptions import Retry

from ..common.celery_config import celery_app
from ..common.logging import get_logger
from ..common.redis_client import redis_client

logger = get_logger(__name__)


class ParserTask(Task):
    """Базовый класс для задач парсера"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Обработчик успешного выполнения"""
        logger.info(
            f"Parser task {self.name} completed successfully",
            task_id=task_id,
            args=args,
            kwargs=kwargs
        )
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработчик ошибки выполнения"""
        logger.error(
            f"Parser task {self.name} failed",
            task_id=task_id,
            args=args,
            kwargs=kwargs,
            error=str(exc),
            traceback=str(einfo)
        )


@celery_app.task(
    bind=True,
    base=ParserTask,
    name="parser.parse_group_posts",
    queue="parser",
    max_retries=3,
    default_retry_delay=60
)
def parse_group_posts_task(
    self,
    group_id: int,
    count: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """Задача парсинга постов группы"""
    try:
        logger.info(f"Starting posts parsing for group {group_id}")
        
        # Здесь должна быть логика парсинга постов
        # Пока что имитируем процесс
        
        # Проверяем блокировку
        lock_key = f"parse_group_posts:{group_id}"
        if not redis_client.lock(lock_key, timeout=300):
            logger.warning(f"Group {group_id} is already being parsed")
            return {"status": "skipped", "reason": "already_parsing"}
        
        try:
            # Имитация парсинга
            posts_data = []
            for i in range(min(count, 10)):  # Ограничиваем для демо
                post_data = {
                    "id": f"{group_id}_{offset + i}",
                    "text": f"Post {offset + i} from group {group_id}",
                    "date": "2024-01-01T00:00:00Z",
                    "likes": 0,
                    "reposts": 0,
                    "views": 0
                }
                posts_data.append(post_data)
            
            # Сохраняем результаты в Redis
            redis_client.set_json(
                f"parsed_posts:{group_id}:{offset}",
                posts_data,
                ttl=3600
            )
            
            # Обновляем статистику
            redis_client.hset(
                f"group_stats:{group_id}",
                "last_parsed",
                str(offset + len(posts_data))
            )
            
            logger.info(
                f"Parsed {len(posts_data)} posts for group {group_id}",
                group_id=group_id,
                posts_count=len(posts_data),
                offset=offset
            )
            
            return {
                "status": "success",
                "group_id": group_id,
                "posts_parsed": len(posts_data),
                "offset": offset,
                "task_id": self.request.id
            }
            
        finally:
            # Освобождаем блокировку
            redis_client.unlock(lock_key)
            
    except Exception as e:
        logger.error(f"Posts parsing failed for group {group_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=ParserTask,
    name="parser.parse_post_comments",
    queue="parser",
    max_retries=3,
    default_retry_delay=60
)
def parse_post_comments_task(
    self,
    group_id: int,
    post_id: int,
    count: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """Задача парсинга комментариев поста"""
    try:
        logger.info(f"Starting comments parsing for post {post_id} in group {group_id}")
        
        # Проверяем блокировку
        lock_key = f"parse_post_comments:{group_id}:{post_id}"
        if not redis_client.lock(lock_key, timeout=300):
            logger.warning(f"Post {post_id} is already being parsed")
            return {"status": "skipped", "reason": "already_parsing"}
        
        try:
            # Имитация парсинга комментариев
            comments_data = []
            for i in range(min(count, 20)):  # Ограничиваем для демо
                comment_data = {
                    "id": f"{group_id}_{post_id}_{offset + i}",
                    "text": f"Comment {offset + i} for post {post_id}",
                    "author_id": 12345 + i,
                    "date": "2024-01-01T00:00:00Z",
                    "likes": 0,
                    "replies_count": 0
                }
                comments_data.append(comment_data)
            
            # Сохраняем результаты в Redis
            redis_client.set_json(
                f"parsed_comments:{group_id}:{post_id}:{offset}",
                comments_data,
                ttl=3600
            )
            
            # Обновляем статистику
            redis_client.hset(
                f"post_stats:{group_id}:{post_id}",
                "last_parsed",
                str(offset + len(comments_data))
            )
            
            logger.info(
                f"Parsed {len(comments_data)} comments for post {post_id}",
                group_id=group_id,
                post_id=post_id,
                comments_count=len(comments_data),
                offset=offset
            )
            
            return {
                "status": "success",
                "group_id": group_id,
                "post_id": post_id,
                "comments_parsed": len(comments_data),
                "offset": offset,
                "task_id": self.request.id
            }
            
        finally:
            # Освобождаем блокировку
            redis_client.unlock(lock_key)
            
    except Exception as e:
        logger.error(f"Comments parsing failed for post {post_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=ParserTask,
    name="parser.parse_group_info",
    queue="parser",
    max_retries=3,
    default_retry_delay=60
)
def parse_group_info_task(
    self,
    group_id: int
) -> Dict[str, Any]:
    """Задача парсинга информации о группе"""
    try:
        logger.info(f"Starting group info parsing for group {group_id}")
        
        # Имитация парсинга информации о группе
        group_info = {
            "id": group_id,
            "name": f"Group {group_id}",
            "description": f"Description for group {group_id}",
            "members_count": 1000 + group_id,
            "type": "public",
            "verified": False,
            "last_activity": "2024-01-01T00:00:00Z"
        }
        
        # Сохраняем информацию в Redis
        redis_client.set_json(
            f"group_info:{group_id}",
            group_info,
            ttl=86400  # 24 часа
        )
        
        logger.info(
            f"Parsed group info for group {group_id}",
            group_id=group_id,
            group_name=group_info["name"]
        )
        
        return {
            "status": "success",
            "group_id": group_id,
            "group_info": group_info,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Group info parsing failed for group {group_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=ParserTask,
    name="parser.batch_parse_groups",
    queue="parser",
    max_retries=3,
    default_retry_delay=60
)
def batch_parse_groups_task(
    self,
    group_ids: List[int],
    parse_posts: bool = True,
    parse_comments: bool = True
) -> Dict[str, Any]:
    """Задача пакетного парсинга групп"""
    try:
        logger.info(f"Starting batch parsing for {len(group_ids)} groups")
        
        results = []
        for group_id in group_ids:
            try:
                # Парсим информацию о группе
                group_info_result = parse_group_info_task.delay(group_id)
                group_info = group_info_result.get(timeout=30)
                
                # Парсим посты если нужно
                posts_result = None
                if parse_posts:
                    posts_result = parse_group_posts_task.delay(group_id, count=50)
                
                # Парсим комментарии если нужно
                comments_result = None
                if parse_comments and posts_result:
                    # Здесь должна быть логика получения post_id из результатов парсинга постов
                    pass
                
                results.append({
                    "group_id": group_id,
                    "group_info": group_info,
                    "posts_task_id": posts_result.id if posts_result else None,
                    "comments_task_id": comments_result.id if comments_result else None
                })
                
            except Exception as e:
                logger.error(f"Failed to parse group {group_id}: {e}")
                results.append({
                    "group_id": group_id,
                    "error": str(e)
                })
        
        logger.info(
            f"Batch parsing completed for {len(group_ids)} groups",
            groups_count=len(group_ids),
            successful=len([r for r in results if "error" not in r])
        )
        
        return {
            "status": "completed",
            "groups_count": len(group_ids),
            "results": results,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Batch parsing failed: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=ParserTask,
    name="parser.cleanup_old_data",
    queue="low_priority",
    max_retries=3,
    default_retry_delay=60
)
def cleanup_old_data_task(
    self,
    days_old: int = 7
) -> Dict[str, Any]:
    """Задача очистки старых данных парсинга"""
    try:
        logger.info(f"Starting cleanup of data older than {days_old} days")
        
        # Паттерны для поиска старых данных
        patterns = [
            "parsed_posts:*",
            "parsed_comments:*",
            "group_stats:*",
            "post_stats:*"
        ]
        
        total_cleaned = 0
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            for key in keys:
                # Проверяем возраст данных
                ttl = redis_client.ttl(key)
                if ttl > days_old * 86400:  # Конвертируем дни в секунды
                    redis_client.delete(key)
                    total_cleaned += 1
        
        logger.info(
            f"Cleanup completed",
            days_old=days_old,
            keys_cleaned=total_cleaned
        )
        
        return {
            "status": "completed",
            "days_old": days_old,
            "keys_cleaned": total_cleaned,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        raise self.retry(exc=e, countdown=60)
