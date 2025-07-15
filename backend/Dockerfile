# syntax=docker/dockerfile:1.6

# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app

# Системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry и uv с pin-версией
RUN pip install --no-cache-dir poetry==2.1.3 poetry-plugin-export uv==0.1.39

# Отключаем создание виртуального окружения poetry
RUN poetry config virtualenvs.create false

# Копируем только poetry-файлы для layer caching
COPY pyproject.toml poetry.lock* ./

# Экспортируем зависимости poetry в requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Устанавливаем зависимости через uv
RUN uv pip install --system --no-deps --requirement requirements.txt

# Копируем только нужные директории (исключая тесты, .git и т.д.)
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# force rebuild for latest tag push

# Stage 2: Production
FROM python:3.13-slim AS production
WORKDIR /app

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаём non-root пользователя
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Копируем установленные библиотеки и бинарники
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем только нужные файлы приложения
COPY --from=builder /app /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
