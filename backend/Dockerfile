# syntax=docker/dockerfile:1.6

# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app

# Системные зависимости для сборки и установка poetry/uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-build.txt ./
RUN pip install --no-cache-dir -r requirements-build.txt && poetry config virtualenvs.create false

# Копируем только poetry-файлы для layer caching
COPY pyproject.toml poetry.lock* ./

# Экспортируем зависимости poetry в requirements.txt и устанавливаем их
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes \
    && uv pip install --system --no-deps --requirement requirements.txt

# Копируем только нужные директории (исключая тесты, .git и т.д.)
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# force rebuild for latest tag push

# Stage 2: Production
FROM python:3.11-slim AS production
WORKDIR /app

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаём non-root пользователя
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Копируем установленные библиотеки и бинарники
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем только нужные файлы приложения
COPY --from=builder /app /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
