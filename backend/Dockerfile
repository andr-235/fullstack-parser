# Stage 1: Dependencies (оптимизированный кешируемый слой)
FROM python:3.13-slim AS deps
WORKDIR /app

# Устанавливаем системные зависимости для компиляции
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем только файлы зависимостей для лучшего кеширования
COPY pyproject.toml poetry.lock ./

# Устанавливаем poetry с кешированием
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==1.8.3 && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10 && \
    poetry install --no-root --only=main --no-interaction

# Stage 2: Builder (только код приложения)
FROM python:3.13-slim AS builder
WORKDIR /app

# Копируем только установленные пакеты
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Копируем только необходимые файлы приложения
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./

# Stage 3: Production (минимальный образ)
FROM python:3.13-slim AS production
WORKDIR /app

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Копируем Python пакеты и код
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
COPY --from=builder /entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]