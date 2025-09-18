"""
Базовый репозиторий для унификации работы с репозиториями

Предоставляет абстрактный базовый класс с общими методами CRUD
и декораторами обработки ошибок для устранения дублирования кода.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Any, Dict
from datetime import datetime, timedelta

from sqlalchemy import func, select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.keywords.shared.error_handlers import handle_repository_errors
from src.keywords.shared.constants import DEFAULT_LIMIT

# Типы для обобщений
T = TypeVar("T")  # Тип доменной сущности
M = TypeVar("M", bound=DeclarativeBase)  # Тип модели базы данных


class BaseRepository(ABC, Generic[T, M]):
  """
  Абстрактный базовый репозиторий с общими методами CRUD.

  Предоставляет унифицированный интерфейс для работы с репозиториями,
  устраняя дублирование кода и обеспечивая согласованность операций.

  Attributes:
    db: Асинхронная сессия базы данных SQLAlchemy
    model_class: Класс модели базы данных
  """

  def __init__(self, db: AsyncSession, model_class: type[M]):
    """
    Инициализация базового репозитория.

    Args:
      db: Асинхронная сессия базы данных
      model_class: Класс модели базы данных
    """
    self.db = db
    self.model_class = model_class

  @abstractmethod
  def to_domain(self, model: M) -> T:
    """
    Преобразование модели базы данных в доменную сущность.

    Args:
      model: Модель базы данных

    Returns:
      Доменная сущность
    """
    pass

  @abstractmethod
  def to_model(self, entity: T) -> M:
    """
    Преобразование доменной сущности в модель базы данных.

    Args:
      entity: Доменная сущность

    Returns:
      Модель базы данных
    """
    pass

  @handle_repository_errors
  async def save(self, entity: T) -> T:
    """
    Сохранить сущность в базе данных.

    Args:
      entity: Доменная сущность для сохранения

    Returns:
      Сохраненная доменная сущность с обновленными полями
    """
    model = self.to_model(entity)
    self.db.add(model)
    await self.db.commit()
    await self.db.refresh(model)
    return self.to_domain(model)

  @handle_repository_errors
  async def find_by_id(self, entity_id: int) -> Optional[T]:
    """
    Найти сущность по ID.

    Args:
      entity_id: ID сущности

    Returns:
      Найденная сущность или None
    """
    query = select(self.model_class).where(self.model_class.id == entity_id)
    result = await self.db.execute(query)
    model = result.scalar_one_or_none()
    return self.to_domain(model) if model else None

  @handle_repository_errors
  async def find_by_field(self, field_name: str, field_value: Any) -> Optional[T]:
    """
    Найти сущность по значению поля.

    Args:
      field_name: Имя поля для поиска
      field_value: Значение поля

    Returns:
      Найденная сущность или None
    """
    query = select(self.model_class).where(
      getattr(self.model_class, field_name) == field_value
    )
    result = await self.db.execute(query)
    model = result.scalar_one_or_none()
    return self.to_domain(model) if model else None

  @handle_repository_errors
  async def find_all(
    self,
    filters: Optional[Dict[str, Any]] = None,
    search_fields: Optional[List[str]] = None,
    search_text: Optional[str] = None,
    order_by: Optional[str] = None,
    order_desc: bool = True,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
  ) -> List[T]:
    """
    Найти все сущности с фильтрами и поиском.

    Args:
      filters: Словарь с фильтрами {field_name: field_value}
      search_fields: Список полей для текстового поиска
      search_text: Текст для поиска
      order_by: Поле для сортировки
      order_desc: Сортировка по убыванию
      limit: Максимальное количество результатов
      offset: Смещение для пагинации

    Returns:
      Список найденных сущностей
    """
    query = select(self.model_class)

    # Применяем фильтры
    if filters:
      conditions = []
      for field_name, field_value in filters.items():
        if hasattr(self.model_class, field_name):
          conditions.append(
            getattr(self.model_class, field_name) == field_value
          )
      if conditions:
        query = query.where(and_(*conditions))

    # Применяем поиск
    if search_text and search_fields:
      search_conditions = []
      for field_name in search_fields:
        if hasattr(self.model_class, field_name):
          search_conditions.append(
            getattr(self.model_class, field_name).ilike(f"%{search_text}%")
          )
      if search_conditions:
        query = query.where(or_(*search_conditions))

    # Применяем сортировку
    if order_by and hasattr(self.model_class, order_by):
      order_field = getattr(self.model_class, order_by)
      query = query.order_by(desc(order_field) if order_desc else order_field)
    else:
      # Сортировка по умолчанию по ID по убыванию
      query = query.order_by(desc(self.model_class.id))

    # Применяем пагинацию
    query = query.offset(offset).limit(limit)

    result = await self.db.execute(query)
    models = result.scalars().all()
    return [self.to_domain(model) for model in models]

  @handle_repository_errors
  async def update(self, entity: T) -> bool:
    """
    Обновить сущность в базе данных.

    Args:
      entity: Доменная сущность с обновленными данными

    Returns:
      True если обновление успешно, False в противном случае
    """
    model = self.to_model(entity)

    # Получаем существующую запись для обновления
    query = select(self.model_class).where(
      self.model_class.id == getattr(entity, "id", None)
    ).with_for_update()

    result = await self.db.execute(query)
    existing_model = result.scalar_one_or_none()

    if not existing_model:
      return False

    # Обновляем поля
    update_data = {}
    for column in self.model_class.__table__.columns:
      if column.name != "id" and hasattr(model, column.name):
        value = getattr(model, column.name)
        if value is not None:
          update_data[column.name] = value

    # Добавляем timestamp обновления, если поле существует
    if hasattr(self.model_class, "updated_at"):
      update_data["updated_at"] = datetime.utcnow()

    if update_data:
      for field, value in update_data.items():
        setattr(existing_model, field, value)
      await self.db.commit()
      return True

    return False

  @handle_repository_errors
  async def delete(self, entity_id: int) -> bool:
    """
    Удалить сущность по ID.

    Args:
      entity_id: ID сущности для удаления

    Returns:
      True если удаление успешно, False в противном случае
    """
    query = select(self.model_class).where(self.model_class.id == entity_id)
    result = await self.db.execute(query)
    model = result.scalar_one_or_none()

    if model:
      await self.db.delete(model)
      await self.db.commit()
      return True

    return False

  @handle_repository_errors
  async def exists_by_field(self, field_name: str, field_value: Any) -> bool:
    """
    Проверить существование сущности по значению поля.

    Args:
      field_name: Имя поля
      field_value: Значение поля

    Returns:
      True если сущность существует, False в противном случае
    """
    query = select(func.count(self.model_class.id)).where(
      getattr(self.model_class, field_name) == field_value
    )
    result = await self.db.execute(query)
    count = result.scalar() or 0
    return count > 0

  @handle_repository_errors
  async def count(
    self,
    filters: Optional[Dict[str, Any]] = None,
    search_fields: Optional[List[str]] = None,
    search_text: Optional[str] = None,
  ) -> int:
    """
    Подсчитать количество сущностей с фильтрами.

    Args:
      filters: Словарь с фильтрами {field_name: field_value}
      search_fields: Список полей для текстового поиска
      search_text: Текст для поиска

    Returns:
      Количество найденных сущностей
    """
    query = select(func.count(self.model_class.id))

    # Применяем фильтры
    if filters:
      conditions = []
      for field_name, field_value in filters.items():
        if hasattr(self.model_class, field_name):
          conditions.append(
            getattr(self.model_class, field_name) == field_value
          )
      if conditions:
        query = query.where(and_(*conditions))

    # Применяем поиск
    if search_text and search_fields:
      search_conditions = []
      for field_name in search_fields:
        if hasattr(self.model_class, field_name):
          search_conditions.append(
            getattr(self.model_class, field_name).ilike(f"%{search_text}%")
          )
      if search_conditions:
        query = query.where(or_(*search_conditions))

    result = await self.db.execute(query)
    return result.scalar() or 0

  @handle_repository_errors
  async def count_by_period(self, days: int, date_field: str = "created_at") -> int:
    """
    Подсчитать количество сущностей за период.

    Args:
      days: Количество дней назад от текущего момента
      date_field: Имя поля с датой (по умолчанию created_at)

    Returns:
      Количество сущностей за период
    """
    if not hasattr(self.model_class, date_field):
      return 0

    since_date = datetime.utcnow() - timedelta(days=days)
    query = select(func.count(self.model_class.id)).where(
      getattr(self.model_class, date_field) >= since_date
    )
    result = await self.db.execute(query)
    return result.scalar() or 0

  @handle_repository_errors
  async def get_stats(self) -> Dict[str, Any]:
    """
    Получить базовую статистику по сущностям.

    Returns:
      Словарь со статистикой
    """
    # Общее количество
    total_query = select(func.count(self.model_class.id))
    total_result = await self.db.execute(total_query)
    total = total_result.scalar() or 0

    # Статистика по периодам
    week_count = await self.count_by_period(7)
    month_count = await self.count_by_period(30)

    return {
      "total": total,
      "last_week": week_count,
      "last_month": month_count,
    }