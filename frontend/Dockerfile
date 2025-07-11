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

# Копируем только package.json и pnpm-lock.yaml для layer caching
COPY package.json pnpm-lock.yaml ./

# Устанавливаем зависимости
RUN pnpm install --frozen-lockfile

# Копируем исходники (исключая тесты, .git и т.д.)
COPY . .

# Собираем проект (standalone)
RUN pnpm build

# Stage 2: Production
FROM node:20-alpine3.18 AS production
WORKDIR /app

# Устанавливаем wget для healthcheck
RUN apk update && apk add --no-cache wget && rm -rf /var/cache/apk/*

# Создаём non-root пользователя
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# Копируем standalone-вывод, статику и public из builder
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Устанавливаем переменные окружения
ENV NODE_ENV=production

USER nextjs

EXPOSE 3000

# Добавляем healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --spider -q http://localhost:3000 || exit 1

# Запуск standalone-сервера
CMD ["node", "server.js"] 
