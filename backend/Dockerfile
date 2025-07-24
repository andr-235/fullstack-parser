# =============================================================================
# Optimized Multi-stage Dockerfile for FastAPI Backend Application
# =============================================================================

# ----------- Stage 1: Dependencies (with enhanced caching) -----------
# Пиннинг версии для воспроизводимости
FROM python:3.13-slim AS deps
WORKDIR /app

# Установка системных зависимостей для компиляции
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копирование только файлов зависимостей для лучшего кеширования
COPY pyproject.toml poetry.lock* ./

# Установка poetry с оптимизацией
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==1.8.3 && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10 && \
    poetry config installer.parallel true && \
    poetry install --no-root --only=main --no-interaction

# ----------- Stage 2: Builder (application build) -----------
FROM python:3.13-slim AS builder
WORKDIR /app

# Копирование установленных пакетов
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Копирование исходного кода
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./

# ----------- Stage 3: Production (minimal runtime) -----------
FROM python:3.13-slim AS production
WORKDIR /app

# Установка только runtime зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    tzdata \
    dumb-init \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Настройка часового пояса для Владивостока
ENV TZ=Asia/Vladivostok
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Копирование Python пакетов и кода
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
COPY entrypoint.sh /entrypoint.sh

# Настройка прав доступа
RUN chmod +x /entrypoint.sh && \
    chown -R appuser:appuser /app

# Метаданные образа
LABEL maintainer="team@company.com" \
      version="1.0" \
      description="Production FastAPI application"

# Настройка безопасности
USER appuser

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Экспорт порта
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Точка входа с dumb-init для правильной обработки сигналов
ENTRYPOINT ["dumb-init", "--"]

# Команда запуска
CMD ["/entrypoint.sh"]