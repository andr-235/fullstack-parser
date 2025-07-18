# Stage 1: Dependencies (кешируемый слой)
FROM python:3.13-slim AS deps
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only=main

# Stage 2: Builder (копируем код)
FROM python:3.13-slim AS builder
WORKDIR /app
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . .

# Stage 3: Production
FROM python:3.13-slim AS production
WORKDIR /app
RUN apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
ENTRYPOINT ["/entrypoint.sh"] 