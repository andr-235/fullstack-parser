# Этап 1: Сборка зависимостей
# Этот этап создает requirements.txt из poetry.lock.
# Он включает build-essential для компиляции пакетов, если это необходимо.
FROM python:3.11-slim AS requirements-stage

WORKDIR /tmp

# Устанавливаем системные зависимости, необходимые для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry==1.8.2

# Копируем файлы Poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/

# Отключаем создание виртуального окружения внутри Poetry
RUN poetry config virtualenvs.create false

# Экспортируем зависимости в requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Этап 2: Образ для разработки
# Этот этап используется для локальной разработки с hot-reloading.
FROM python:3.11-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Устанавливаем системные зависимости для разработки
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry==1.8.2

# Конфигурируем Poetry
RUN poetry config virtualenvs.create false

WORKDIR /app

# Копируем файлы зависимостей и устанавливаем ВСЕ зависимости (включая dev)
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

# Копируем остальной код приложения
COPY . /app/

EXPOSE 8000

# Команда по умолчанию для разработки
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Этап 3: Финальный образ для production
# Это оптимизированный, легковесный и безопасный образ.
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создаем пользователя без root-прав
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Устанавливаем ТОЛЬКО runtime системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements.txt из этапа сборки зависимостей
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

# Устанавливаем Python зависимости через pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код приложения от имени non-root пользователя
COPY --chown=appuser:appuser . /app/

# Переключаемся на non-root пользователя
USER appuser

EXPOSE 8000

# Проверка состояния
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда для запуска приложения в production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]