"""
Модель VK группы для мониторинга
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.vk_post import VKPost


class VKGroup(BaseModel):
    """Модель VK группы для мониторинга"""

    __tablename__ = "vk_groups"

    # Основная информация
    vk_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="ID группы в ВК",
    )
    screen_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Короткое имя группы (@group_name)",
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Название группы"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="Описание группы"
    )

    # Настройки мониторинга
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Активен ли мониторинг группы"
    )
    max_posts_to_check: Mapped[int] = mapped_column(
        Integer, default=100, comment="Максимум постов для проверки"
    )

    # Настройки автоматического мониторинга
    auto_monitoring_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Включен ли автоматический мониторинг"
    )
    monitoring_interval_minutes: Mapped[int] = mapped_column(
        Integer, default=60, comment="Интервал мониторинга в минутах"
    )
    next_monitoring_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        comment="Когда следующий раз запускать мониторинг",
    )
    monitoring_priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
        comment="Приоритет мониторинга (1-10, где 10 - высший)",
    )

    # Статистика
    last_parsed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        comment="Когда последний раз парсили группу",
    )
    total_posts_parsed: Mapped[int] = mapped_column(
        Integer, default=0, comment="Общее количество обработанных постов"
    )
    total_comments_found: Mapped[int] = mapped_column(
        Integer, default=0, comment="Общее количество найденных комментариев"
    )

    # Статистика мониторинга
    monitoring_runs_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество запусков мониторинга"
    )
    last_monitoring_success: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        comment="Последний успешный запуск мониторинга",
    )
    last_monitoring_error: Mapped[Optional[str]] = mapped_column(
        Text, comment="Последняя ошибка мониторинга"
    )

    # Метаданные VK
    members_count: Mapped[Optional[int]] = mapped_column(
        Integer, comment="Количество участников"
    )
    is_closed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Закрытая ли группа"
    )
    photo_url: Mapped[Optional[str]] = mapped_column(
        String(500), comment="URL аватара группы"
    )

    # Связи
    posts: Mapped[List["VKPost"]] = relationship(
        "VKPost", back_populates="group", cascade="all, delete-orphan"
    )

    # DDD Domain Methods - Добавлены для совместимости с Domain Layer

    def validate_business_rules(self) -> None:
        """
        Валидация бизнес-правил домена (DDD метод)

        Выполняет проверки целостности данных группы
        согласно бизнес-правилам домена.
        """
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Group name cannot be empty")

        if not self.screen_name or len(self.screen_name.strip()) == 0:
            raise ValueError("Group screen_name cannot be empty")

        if self.vk_id <= 0:
            raise ValueError("Invalid VK group ID")

        if len(self.name) > 200:
            raise ValueError("Group name is too long (max 200 characters)")

        if len(self.screen_name) > 100:
            raise ValueError(
                "Group screen_name is too long (max 100 characters)"
            )

        # Валидация настроек мониторинга
        if self.monitoring_interval_minutes < 1:
            raise ValueError("Monitoring interval must be at least 1 minute")

        if not (1 <= self.monitoring_priority <= 10):
            raise ValueError("Monitoring priority must be between 1 and 10")

    def activate(self) -> None:
        """
        Активирует группу (DDD бизнес-метод)

        Включает мониторинг группы.
        """
        if not self.is_active:
            self.is_active = True
            # Здесь можно добавить Domain Event
            # self.add_domain_event(GroupActivatedEvent(self.id))

    def deactivate(self) -> None:
        """
        Деактивирует группу (DDD бизнес-метод)

        Отключает мониторинг группы.
        """
        if self.is_active:
            self.is_active = False
            # Здесь можно добавить Domain Event
            # self.add_domain_event(GroupDeactivatedEvent(self.id))

    def enable_monitoring(self) -> None:
        """
        Включает автоматический мониторинг (DDD бизнес-метод)
        """
        if not self.auto_monitoring_enabled:
            self.auto_monitoring_enabled = True
            self.calculate_next_monitoring_time()
            # Здесь можно добавить Domain Event
            # self.add_domain_event(MonitoringEnabledEvent(self.id))

    def disable_monitoring(self) -> None:
        """
        Отключает автоматический мониторинг (DDD бизнес-метод)
        """
        if self.auto_monitoring_enabled:
            self.auto_monitoring_enabled = False
            self.next_monitoring_at = None
            # Здесь можно добавить Domain Event
            # self.add_domain_event(MonitoringDisabledEvent(self.id))

    def calculate_next_monitoring_time(self) -> Optional[datetime]:
        """
        Вычисляет время следующего мониторинга (DDD бизнес-логика)

        Returns:
            Время следующего мониторинга или None если мониторинг отключен
        """
        if not self.auto_monitoring_enabled or not self.is_active:
            return None

        from datetime import timedelta

        return datetime.utcnow() + timedelta(
            minutes=self.monitoring_interval_minutes
        )

    def record_monitoring_success(self) -> None:
        """
        Записывает успешное выполнение мониторинга (DDD бизнес-метод)

        Обновляет статистику и время следующего мониторинга.
        """
        self.monitoring_runs_count += 1
        self.last_monitoring_success = datetime.utcnow()
        self.last_parsed_at = datetime.utcnow()

        # Очищаем ошибку при успешном выполнении
        if self.last_monitoring_error:
            self.last_monitoring_error = None

        # Вычисляем следующее время мониторинга
        self.next_monitoring_at = self.calculate_next_monitoring_time()

    def record_monitoring_error(self, error_message: str) -> None:
        """
        Записывает ошибку мониторинга (DDD бизнес-метод)

        Args:
            error_message: Сообщение об ошибке
        """
        self.last_monitoring_error = error_message

        # При ошибке все равно обновляем время следующего мониторинга
        self.next_monitoring_at = self.calculate_next_monitoring_time()

    def is_ready_for_monitoring(self) -> bool:
        """
        Проверяет, готова ли группа к мониторингу (DDD бизнес-правило)

        Returns:
            True если группа готова к мониторингу
        """
        if not self.is_active:
            return False

        if not self.auto_monitoring_enabled:
            return False

        if not self.next_monitoring_at:
            return True

        return datetime.utcnow() >= self.next_monitoring_at

    def update_monitoring_config(self, config: Dict[str, Any]) -> None:
        """
        Обновляет конфигурацию мониторинга (DDD бизнес-метод)

        Args:
            config: Новая конфигурация мониторинга
        """
        # Обновляем основные параметры
        if "interval_minutes" in config:
            self.monitoring_interval_minutes = config["interval_minutes"]

        if "priority" in config:
            self.monitoring_priority = config["priority"]

        if "max_posts_to_check" in config:
            self.max_posts_to_check = config["max_posts_to_check"]

        # Пересчитываем следующее время мониторинга
        self.next_monitoring_at = self.calculate_next_monitoring_time()

    def get_monitoring_status(self) -> str:
        """
        Получает статус мониторинга группы (DDD бизнес-метод)

        Returns:
            Статус: 'active', 'inactive', 'error', 'ready', 'waiting'
        """
        if not self.is_active:
            return "inactive"

        if self.last_monitoring_error:
            return "error"

        if self.is_ready_for_monitoring():
            return "ready"

        return "waiting"

    def can_be_monitored(self) -> bool:
        """
        Проверяет, можно ли мониторить группу (DDD бизнес-правило)

        Returns:
            True если группу можно мониторить
        """
        # Бизнес-правило: нельзя мониторить закрытые группы
        if self.is_closed:
            return False

        # Проверяем наличие screen_name для формирования ссылок
        if not self.screen_name:
            return False

        return True

    def get_monitoring_info(self) -> Dict[str, Any]:
        """
        Получает информацию о мониторинге группы (DDD бизнес-метод)

        Returns:
            Информация о мониторинге
        """
        return {
            "is_active": self.is_active,
            "auto_monitoring_enabled": self.auto_monitoring_enabled,
            "monitoring_interval_minutes": self.monitoring_interval_minutes,
            "monitoring_priority": self.monitoring_priority,
            "next_monitoring_at": (
                self.next_monitoring_at.isoformat()
                if self.next_monitoring_at
                else None
            ),
            "last_parsed_at": (
                self.last_parsed_at.isoformat()
                if self.last_parsed_at
                else None
            ),
            "monitoring_runs_count": self.monitoring_runs_count,
            "last_monitoring_success": (
                self.last_monitoring_success.isoformat()
                if self.last_monitoring_success
                else None
            ),
            "last_monitoring_error": self.last_monitoring_error,
            "status": self.get_monitoring_status(),
            "is_ready": self.is_ready_for_monitoring(),
        }

    def update_statistics(
        self, posts_parsed: int = 0, comments_found: int = 0
    ) -> None:
        """
        Обновляет статистику группы (DDD бизнес-метод)

        Args:
            posts_parsed: Количество обработанных постов
            comments_found: Количество найденных комментариев
        """
        self.total_posts_parsed += posts_parsed
        self.total_comments_found += comments_found

    # Domain Events Support - Поддержка событий домена
    _domain_events: List[dict] = []

    def add_domain_event(self, event_data: dict) -> None:
        """
        Добавляет Domain Event (DDD паттерн)

        Args:
            event_data: Данные события
        """
        event = {
            "event_type": event_data.get("event_type", "unknown"),
            "aggregate_id": self.id,
            "occurred_at": datetime.utcnow().isoformat(),
            "event_data": event_data,
        }
        self._domain_events.append(event)

    @property
    def domain_events(self) -> List[dict]:
        """
        Получает список Domain Events (DDD паттерн)

        Returns:
            Список событий домена
        """
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """
        Очищает список Domain Events (DDD паттерн)

        Вызывается после успешного сохранения агрегата.
        """
        self._domain_events.clear()

    def __repr__(self):
        return f"<VKGroup(vk_id={self.vk_id}, name={self.name}, active={self.is_active}, monitoring={self.get_monitoring_status()})>"
