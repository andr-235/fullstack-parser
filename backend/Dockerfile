# =============================================================================
# Optimized Multi-stage Dockerfile for NestJS Backend Application
# =============================================================================

# ----------- Stage 1: Dependencies (with enhanced caching) -----------
# Пиннинг версии для воспроизводимости
FROM node:18-alpine@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c AS deps

# Установка системных зависимостей
RUN apk add --no-cache libc6-compat

# Создание пользователя для безопасности
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nestjs -u 1001

WORKDIR /app

# Копирование файлов зависимостей для кеширования
COPY package.json package-lock.json* ./

# Установка зависимостей с кешированием
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production && npm cache clean --force

# ----------- Stage 2: Builder (application build) -----------
FROM node:18-alpine AS builder
WORKDIR /app

# Копирование исходного кода
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Сборка приложения
RUN --mount=type=cache,target=/app/.nest/cache \
    npm run build

# ----------- Stage 3: Production (minimal runtime) -----------
FROM node:18-alpine AS runner
WORKDIR /app

# Создание пользователя
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nestjs -u 1001

# Копирование только необходимых файлов
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/prisma ./prisma

# Настройка безопасности
USER nestjs

# Метаданные образа
LABEL maintainer="team@company.com" \
      version="1.0" \
      description="Production NestJS application"

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Экспорт порта
EXPOSE 8000

# Переменные окружения
ENV NODE_ENV=production
ENV PORT=8000

# Точка входа
ENTRYPOINT ["node"]
CMD ["dist/main.js"]