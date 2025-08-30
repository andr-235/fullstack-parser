# =============================================================================
# Optimized Multi-stage Dockerfile for Next.js 15 Frontend Application with Bun
# =============================================================================

# ----------- Stage 1: Dependencies (with enhanced caching) -----------
FROM oven/bun:1.2.19-alpine AS deps

# Установка системных зависимостей
RUN apk add --no-cache libc6-compat

# Создание непривилегированного пользователя
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

WORKDIR /app

# Копирование оптимизированного package.json для быстрой сборки
COPY package.json.production.json ./package.json
COPY bun.lock.build ./bun.lock

# Настройка bun для production и кеширования
ENV BUN_INSTALL_CACHE_DIR=/tmp/bun-cache

# Установка оптимизированных зависимостей для сборки
RUN --mount=type=cache,target=/tmp/bun-cache \
    bun install

# ----------- Stage 2: Production Dependencies -----------
FROM oven/bun:1.2.19-alpine AS production-deps

WORKDIR /app

# Копирование оптимизированного package.json для production
COPY package.json.production.json ./package.json

# Настройка bun для кеширования
ENV BUN_INSTALL_CACHE_DIR=/tmp/bun-cache

# Установка только production зависимостей
RUN --mount=type=cache,target=/tmp/bun-cache \
    bun install --production

# ----------- Stage 3: Builder (optimized build) -----------
FROM oven/bun:1.2.19-alpine AS builder

WORKDIR /app

# Копирование всех зависимостей для сборки
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/bun.lock ./bun.lock

# Копирование исходного кода
COPY . .

# Настройка переменных окружения для сборки
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    DOCKER=true \
    CI=true \
    BUN_INSTALL_CACHE_DIR=/tmp/bun-cache

# Сборка приложения с кешированием
RUN --mount=type=cache,target=/app/.next/cache \
    --mount=type=cache,target=/tmp/bun-cache \
    bun run build

# ----------- Stage 4: Production (minimal runtime) -----------
FROM node:20-alpine AS runner
WORKDIR /app

# Создание непривилегированного пользователя
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Установка только необходимых пакетов
RUN apk add --no-cache dumb-init curl

# Копирование production зависимостей
COPY --from=production-deps --chown=nextjs:nodejs /app/node_modules ./node_modules

# Копирование только необходимых файлов
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static/
COPY --from=production-deps --chown=nextjs:nodejs /app/package.json ./package.json

# Настройка безопасности
USER nextjs

# Метаданные образа
LABEL maintainer="team@company.com" \
    version="1.0" \
    description="Production Next.js application with Bun"

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Экспорт порта
EXPOSE 3000

# Переменные окружения
ENV PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    NODE_OPTIONS="--max-old-space-size=512"

# Точка входа с dumb-init для правильной обработки сигналов
ENTRYPOINT ["dumb-init", "--"]

# Команда запуска
CMD ["node", "server.js"] 