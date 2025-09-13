"""
Сервис для работы с парсингом VK данных

Упрощенный сервис с объединенными компонентами
"""

import asyncio
import time
from typing import List, Optional, Dict, Any, Protocol
from datetime import datetime
from uuid import uuid4

from parser.config import parser_settings
from parser.models import TaskStatus, TaskPriority, ParsingTask
from parser.group_parser import GroupParser, VKAPIServiceProtocol
from infrastructure.logging import get_loguru_logger

logger = get_loguru_logger("parser-service")


class ParserService:
    """Основной сервис парсера"""

    def __init__(self, group_parser: GroupParser):
        self.group_parser = group_parser
        self._logger = get_loguru_logger("parser-service")
        self.tasks: Dict[str, ParsingTask] = {}

    async def start_parsing(
        self,
        group_ids: List[int],
        max_posts: int = 10,
        max_comments_per_post: int = 100,
        force_reparse: bool = False,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """Запустить парсинг групп"""
        try:
            # Валидация входных данных
            if not group_ids:
                raise ValueError("group_ids не может быть пустым")
            
            if len(group_ids) > parser_settings.max_group_ids_per_request:
                raise ValueError(f"Слишком много групп: {len(group_ids)} > {parser_settings.max_group_ids_per_request}")

            # Создаем задачу
            task_id = str(uuid4())
            task = ParsingTask(
                task_id=task_id,
                group_ids=group_ids,
                config={
                    "max_posts": max_posts,
                    "max_comments_per_post": max_comments_per_post,
                    "force_reparse": force_reparse,
                },
                status=TaskStatus.PENDING,
                priority=priority,
                groups_total=len(group_ids),
            )

            self.tasks[task_id] = task

            # Запускаем парсинг асинхронно
            asyncio.create_task(self._run_parsing(task_id))

            self._logger.info(f"Started parsing task {task_id} for {len(group_ids)} groups")
            return task_id

        except Exception as e:
            self._logger.error(f"Failed to start parsing: {str(e)}")
            raise

    async def get_task_status(self, task_id: str) -> Optional[ParsingTask]:
        """Получить статус задачи"""
        return self.tasks.get(task_id)

    async def stop_parsing(self, task_id: str) -> bool:
        """Остановить парсинг"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.STOPPED
            task.completed_at = datetime.utcnow()
            self._logger.info(f"Stopped parsing task {task_id}")
            return True

        return False

    async def get_all_tasks(self) -> List[ParsingTask]:
        """Получить все задачи"""
        return list(self.tasks.values())

    async def _run_parsing(self, task_id: str):
        """Выполнить парсинг задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return

        try:
            # Обновляем статус на RUNNING
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()

            total_posts = 0
            total_comments = 0
            errors = []

            # Парсим каждую группу
            for i, group_id in enumerate(task.group_ids):
                try:
                    self._logger.info(f"Parsing group {group_id} ({i+1}/{len(task.group_ids)})")
                    
                    # Парсим группу
                    result = await self.group_parser.parse_group(
                        group_id=group_id,
                        max_posts=task.config.get("max_posts", 10),
                        max_comments_per_post=task.config.get("max_comments_per_post", 100),
                    )

                    # Обновляем статистику
                    posts_found = result.get("posts_found", 0)
                    comments_found = result.get("comments_found", 0)
                    
                    total_posts += posts_found
                    total_comments += comments_found

                    # Обновляем прогресс
                    progress = int(((i + 1) / len(task.group_ids)) * 100)
                    task.progress = progress
                    task.groups_completed = i + 1
                    task.current_group = group_id
                    task.posts_found = total_posts
                    task.comments_found = total_comments

                    self._logger.info(
                        f"Group {group_id} parsed: {posts_found} posts, {comments_found} comments"
                    )

                except Exception as e:
                    error_msg = f"Error parsing group {group_id}: {str(e)}"
                    errors.append(error_msg)
                    self._logger.error(error_msg)

            # Завершаем задачу
            if errors:
                task.status = TaskStatus.FAILED
                task.errors = errors
            else:
                task.status = TaskStatus.COMPLETED
                task.progress = 100

            task.completed_at = datetime.utcnow()
            task.result = {
                "total_posts": total_posts,
                "total_comments": total_comments,
                "groups_processed": len(task.group_ids),
                "errors": errors,
            }

            self._logger.info(
                f"Completed parsing task {task_id}: {total_posts} posts, {total_comments} comments"
            )

        except Exception as e:
            self._logger.error(f"Failed to parse task {task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.errors = [str(e)]
            task.completed_at = datetime.utcnow()

    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику парсера"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED)
        running_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.RUNNING)

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        }