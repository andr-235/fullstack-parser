"""
Модели базы данных для ARQ

Содержит модели для хранения информации о задачах и их результатах.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TaskLog(Base):
    """
    Модель для логирования выполнения задач

    Хранит информацию о выполненных задачах для аналитики и отладки.
    """

    __tablename__ = "arq_task_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, index=True, nullable=False)
    function_name = Column(String(255), nullable=False)
    status = Column(
        String(50), nullable=False
    )  # pending, running, complete, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # в секундах
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    args = Column(JSON, nullable=True)
    kwargs = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    def __repr__(self):
        return f"<TaskLog(job_id='{self.job_id}', function='{self.function_name}', status='{self.status}')>"


class CronJob(Base):
    """
    Модель для cron задач

    Хранит информацию о запланированных задачах.
    """

    __tablename__ = "arq_cron_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    function_name = Column(String(255), nullable=False)
    cron_expression = Column(String(255), nullable=False)
    args = Column(JSON, default=list, nullable=False)
    kwargs = Column(JSON, default=dict, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<CronJob(name='{self.name}', function='{self.function_name}', enabled={self.enabled})>"


class TaskStatistics(Base):
    """
    Модель для статистики выполнения задач

    Хранит агрегированную статистику по задачам.
    """

    __tablename__ = "arq_task_statistics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    function_name = Column(String(255), nullable=False, index=True)
    total_tasks = Column(Integer, default=0, nullable=False)
    successful_tasks = Column(Integer, default=0, nullable=False)
    failed_tasks = Column(Integer, default=0, nullable=False)
    average_duration = Column(Integer, nullable=True)  # в секундах
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TaskStatistics(date='{self.date}', function='{self.function_name}', total={self.total_tasks})>"
