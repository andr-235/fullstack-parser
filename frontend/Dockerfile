# syntax=docker/dockerfile:1.6

# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Build args
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV DOCKER=true

# Устанавливаем pnpm той же версии, что и локально
RUN npm install -g pnpm@10.12.4

# Настраиваем pnpm для ускорения установки
RUN pnpm config set network-timeout 300000 && \
    pnpm config set fetch-timeout 300000 && \
    pnpm config set fetch-retries 5 && \
    pnpm config set store-dir /tmp/.pnpm-store

# Копируем только package.json и pnpm-lock.yaml для layer caching
COPY package.json pnpm-lock.yaml ./

# Устанавливаем зависимости с увеличенными таймаутами и retry логикой
RUN pnpm install --frozen-lockfile --network-timeout=300000 --fetch-timeout=300000 || \
    (echo "Retrying pnpm install..." && sleep 5 && pnpm install --frozen-lockfile --network-timeout=300000 --fetch-timeout=300000) || \
    (echo "Second retry..." && sleep 10 && pnpm install --frozen-lockfile --network-timeout=300000 --fetch-timeout=300000)

# Копируем исходники (исключая тесты, .git и т.д.)
COPY . .

# Собираем проект (standalone) с таймаутом
RUN pnpm build

# Копируем .env.local (если есть) для локальной разработки и build-time env
COPY .env.local .env.local

# Stage 2: Production
FROM node:20-alpine3.18 AS production
WORKDIR /app

# Устанавливаем curl для healthcheck с таймаутом
RUN apk update && apk add --no-cache curl && rm -rf /var/cache/apk/*

# Создаём non-root пользователя
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# Копируем standalone-вывод, статику и public из builder
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Копируем .env.local в production (если есть)
RUN [ -f .env.local ] && cp .env.local .env.local || true

# Устанавливаем переменные окружения
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0

USER nextjs

EXPOSE 3000

# Добавляем healthcheck с увеличенным таймаутом
HEALTHCHECK --interval=30s --timeout=20s --start-period=60s --retries=3 \
    CMD curl -f --max-time 15 http://localhost:3000 || exit 1

# Запуск standalone-сервера
CMD ["node", "server.js"]
