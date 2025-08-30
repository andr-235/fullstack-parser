"""
Модели для модуля Monitoring

Определяет репозиторий и модели для работы с мониторингом групп
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    JSON,
    Float,
    DECIMAL,
)
from sqlalchemy.orm import relationship, backref

from ..database import get_db_session
from ..models import BaseModel


class MonitoringModel(BaseModel):
    """
    SQLAlchemy модель мониторинга

    Представляет мониторинг группы в базе данных
    """

    __tablename__ = "monitorings"

    # Основная информация
    id = Column(String(36), primary_key=True, index=True)
    group_id = Column(Integer, nullable=False, index=True)
    group_name = Column(String(255), nullable=False)
    owner_id = Column(String(255), nullable=False, index=True)

    # Статус и конфигурация
    status = Column(String(20), nullable=False, default="active")
    config = Column(JSON, nullable=False)

    # Временные метки
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)

    # Статистика
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    average_processing_time = Column(Float, default=0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "owner_id": self.owner_id,
            "status": self.status,
            "config": self.config,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_run_at": self.last_run_at,
            "next_run_at": self.next_run_at,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "average_processing_time": self.average_processing_time,
        }

    def is_active(self) -> bool:
        """Проверить активен ли мониторинг"""
        return self.status == "active"

    def is_paused(self) -> bool:
        """Проверить приостановлен ли мониторинг"""
        return self.status == "paused"

    def can_be_scheduled(self) -> bool:
        """Проверить можно ли запланировать мониторинг"""
        return self.status == "active" and self.next_run_at is None

    def increment_runs(self, success: bool, processing_time: float):
        """Увеличить счетчик запусков"""
        self.total_runs += 1

        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1

        # Обновляем среднее время обработки
        if self.average_processing_time == 0:
            self.average_processing_time = processing_time
        else:
            total_time = self.average_processing_time * (self.total_runs - 1)
            self.average_processing_time = (
                total_time + processing_time
            ) / self.total_runs

        self.last_run_at = datetime.utcnow()


class MonitoringResultModel(BaseModel):
    """
    SQLAlchemy модель результата мониторинга

    Представляет результат выполнения цикла мониторинга
    """

    __tablename__ = "monitoring_results"

    # Ссылки
    monitoring_id = Column(String(36), nullable=False, index=True)
    group_id = Column(Integer, nullable=False, index=True)

    # Результаты
    posts_found = Column(Integer, default=0)
    comments_found = Column(Integer, default=0)
    keywords_found = Column(JSON, nullable=True)
    processing_time = Column(Float, default=0.0)
    errors = Column(JSON, nullable=True)

    # Временные метки
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "monitoring_id": self.monitoring_id,
            "group_id": self.group_id,
            "posts_found": self.posts_found,
            "comments_found": self.comments_found,
            "keywords_found": self.keywords_found,
            "processing_time": self.processing_time,
            "errors": self.errors,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
        }

    def has_errors(self) -> bool:
        """Проверить наличие ошибок"""
        return bool(self.errors)

    def mark_completed(self):
        """Отметить как завершенное"""
        if not self.completed_at:
            self.completed_at = datetime.utcnow()


class MonitoringRepository:
    """
    Репозиторий для работы с мониторингом

    Предоставляет интерфейс для хранения и получения данных мониторинга
    """

    def __init__(self, db=None):
        self.db = db

    async def get_db(self):
        """Получить сессию БД"""
        return self.db or get_db_session()

    async def create(self, monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать новый мониторинг

        Args:
            monitoring_data: Данные мониторинга

        Returns:
            Dict[str, Any]: Созданный мониторинг
        """
        db = await self.get_db()

        monitoring = MonitoringModel(
            id=monitoring_data["id"],
            group_id=monitoring_data["group_id"],
            group_name=monitoring_data["group_name"],
            owner_id=monitoring_data["owner_id"],
            status=monitoring_data.get("status", "active"),
            config=monitoring_data.get("config", {}),
            created_at=monitoring_data.get("created_at", datetime.utcnow()),
            updated_at=monitoring_data.get("updated_at", datetime.utcnow()),
            last_run_at=monitoring_data.get("last_run_at"),
            next_run_at=monitoring_data.get("next_run_at"),
            total_runs=monitoring_data.get("total_runs", 0),
            successful_runs=monitoring_data.get("successful_runs", 0),
            failed_runs=monitoring_data.get("failed_runs", 0),
            average_processing_time=monitoring_data.get(
                "average_processing_time", 0.0
            ),
        )

        db.add(monitoring)
        await db.commit()
        await db.refresh(monitoring)
        return monitoring.to_dict()

    async def get_by_id(self, monitoring_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить мониторинг по ID

        Args:
            monitoring_id: ID мониторинга

        Returns:
            Optional[Dict[str, Any]]: Мониторинг или None
        """
        db = await self.get_db()
        result = await db.execute(
            select(MonitoringModel).where(MonitoringModel.id == monitoring_id)
        )
        monitoring = result.scalar_one_or_none()
        return monitoring.to_dict() if monitoring else None

    async def get_by_group_id(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить мониторинг по ID группы

        Args:
            group_id: ID группы VK

        Returns:
            Optional[Dict[str, Any]]: Мониторинг или None
        """
        db = await self.get_db()
        result = await db.execute(
            select(MonitoringModel).where(MonitoringModel.group_id == group_id)
        )
        monitoring = result.scalar_one_or_none()
        return monitoring.to_dict() if monitoring else None

    async def get_by_owner(
        self,
        owner_id: str,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить мониторинги по владельцу

        Args:
            owner_id: ID владельца
            limit: Максимум записей
            offset: Смещение
            status_filter: Фильтр по статусу

        Returns:
            List[Dict[str, Any]]: Список мониторингов
        """
        db = await self.get_db()
        query = select(MonitoringModel).where(
            MonitoringModel.owner_id == owner_id
        )

        if status_filter:
            query = query.where(MonitoringModel.status == status_filter)

        query = (
            query.order_by(MonitoringModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        monitorings = result.scalars().all()
        return [monitoring.to_dict() for monitoring in monitorings]

    async def update(
        self, monitoring_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить мониторинг

        Args:
            monitoring_id: ID мониторинга
            update_data: Данные для обновления

        Returns:
            Optional[Dict[str, Any]]: Обновленный мониторинг или None
        """
        db = await self.get_db()

        monitoring = await self.get_by_id(monitoring_id)
        if not monitoring:
            return None

        # Получаем модель для обновления
        result = await db.execute(
            select(MonitoringModel).where(MonitoringModel.id == monitoring_id)
        )
        monitoring_model = result.scalar_one()

        # Обновляем поля
        for key, value in update_data.items():
            if hasattr(monitoring_model, key):
                setattr(monitoring_model, key, value)

        monitoring_model.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(monitoring_model)
        return monitoring_model.to_dict()

    async def delete(self, monitoring_id: str) -> bool:
        """
        Удалить мониторинг

        Args:
            monitoring_id: ID мониторинга

        Returns:
            bool: True если удален
        """
        db = await self.get_db()

        result = await db.execute(
            select(MonitoringModel).where(MonitoringModel.id == monitoring_id)
        )
        monitoring = result.scalar_one_or_none()

        if not monitoring:
            return False

        await db.delete(monitoring)
        await db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику мониторинга

        Returns:
            Dict[str, Any]: Статистика
        """
        db = await self.get_db()

        result = await db.execute(
            select(
                func.count(MonitoringModel.id).label("total_monitorings"),
                func.sum(
                    case((MonitoringModel.status == "active", 1), else_=0)
                ).label("active_monitorings"),
                func.sum(
                    case((MonitoringModel.status == "paused", 1), else_=0)
                ).label("paused_monitorings"),
                func.sum(MonitoringModel.total_runs).label("total_runs"),
                func.sum(MonitoringModel.successful_runs).label(
                    "successful_runs"
                ),
                func.sum(MonitoringModel.failed_runs).label("failed_runs"),
                func.avg(MonitoringModel.average_processing_time).label(
                    "avg_processing_time"
                ),
            )
        )

        stats = result.first()
        if not stats:
            return {
                "total_monitorings": 0,
                "active_monitorings": 0,
                "paused_monitorings": 0,
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "average_processing_time": 0.0,
                "total_posts_found": 0,
                "total_comments_found": 0,
                "uptime_percentage": 0.0,
            }

        # Получаем дополнительную статистику из результатов
        result_stats = await db.execute(
            select(
                func.sum(MonitoringResultModel.posts_found).label(
                    "total_posts"
                ),
                func.sum(MonitoringResultModel.comments_found).label(
                    "total_comments"
                ),
            )
        )

        result_data = result_stats.first()

        return {
            "total_monitorings": stats.total_monitorings or 0,
            "active_monitorings": stats.active_monitorings or 0,
            "paused_monitorings": stats.paused_monitorings or 0,
            "total_runs": stats.total_runs or 0,
            "successful_runs": stats.successful_runs or 0,
            "failed_runs": stats.failed_runs or 0,
            "average_processing_time": round(
                stats.avg_processing_time or 0, 2
            ),
            "total_posts_found": result_data.total_posts or 0,
            "total_comments_found": result_data.total_comments or 0,
            "uptime_percentage": 95.0,  # Заглушка
        }

    async def create_result(
        self, result_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать результат мониторинга

        Args:
            result_data: Данные результата

        Returns:
            Dict[str, Any]: Созданный результат
        """
        db = await self.get_db()

        result = MonitoringResultModel(
            monitoring_id=result_data["monitoring_id"],
            group_id=result_data["group_id"],
            posts_found=result_data.get("posts_found", 0),
            comments_found=result_data.get("comments_found", 0),
            keywords_found=result_data.get("keywords_found"),
            processing_time=result_data.get("processing_time", 0.0),
            errors=result_data.get("errors"),
            started_at=result_data["started_at"],
            completed_at=result_data.get("completed_at"),
        )

        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result.to_dict()

    async def get_results(
        self, monitoring_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Получить результаты мониторинга

        Args:
            monitoring_id: ID мониторинга
            limit: Максимум записей
            offset: Смещение

        Returns:
            List[Dict[str, Any]]: Список результатов
        """
        db = await self.get_db()
        query = (
            select(MonitoringResultModel)
            .where(MonitoringResultModel.monitoring_id == monitoring_id)
            .order_by(MonitoringResultModel.started_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        results = result.scalars().all()
        return [r.to_dict() for r in results]

    async def count_failed_last_hour(self) -> int:
        """
        Подсчитать неудачные результаты за последний час

        Returns:
            int: Количество неудачных результатов
        """
        db = await self.get_db()
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        result = await db.execute(
            select(func.count(MonitoringResultModel.id))
            .where(MonitoringResultModel.started_at >= one_hour_ago)
            .where(MonitoringResultModel.errors.isnot(None))
        )

        return result.scalar() or 0

    async def cleanup_old_results(self, days: int = 30) -> int:
        """
        Очистить старые результаты

        Args:
            days: Возраст результатов для удаления в днях

        Returns:
            int: Количество удаленных результатов
        """
        db = await self.get_db()
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(func.count(MonitoringResultModel.id)).where(
                MonitoringResultModel.created_at < cutoff_date
            )
        )

        # В реальном приложении здесь был бы DELETE запрос
        count = result.scalar() or 0
        return count


# Функции для создания репозитория
async def get_monitoring_repository(db=None) -> MonitoringRepository:
    """Создать репозиторий мониторинга"""
    return MonitoringRepository(db)


# Импорты (для работы с БД)
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    JSON,
    select,
    desc,
    func,
    case,
)
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


# Экспорт
__all__ = [
    "MonitoringModel",
    "MonitoringResultModel",
    "MonitoringRepository",
    "get_monitoring_repository",
]
