# =============================================================================
# Optimized Multi-stage Dockerfile for Next.js 15 Frontend Application
# =============================================================================

# ----------- Stage 1: Dependencies (with enhanced caching) -----------
FROM node:20-alpine AS deps

# Установка системных зависимостей
RUN apk add --no-cache libc6-compat

# Создание непривилегированного пользователя
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

WORKDIR /app

# Копирование файлов зависимостей для кеширования
COPY package.json pnpm-lock.yaml* ./
COPY yarn.lock* ./

# Установка pnpm и зависимостей с кешированием
RUN npm install -g pnpm@10.12.4 && \
    pnpm install --frozen-lockfile --prod=false && \
    pnpm store prune

# ----------- Stage 2: Builder (optimized build) -----------
FROM node:20-alpine AS builder
WORKDIR /app

# Установка pnpm в builder stage
RUN npm install -g pnpm@10.12.4

# Копирование зависимостей
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /root/.local/share/pnpm/store /root/.local/share/pnpm/store

# Копирование исходного кода
COPY . .

# Настройка переменных окружения для сборки
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    DOCKER=true \
    CI=true

# Сборка приложения с кешированием
RUN --mount=type=cache,target=/app/.next/cache \
    pnpm build

# ----------- Stage 3: Production (minimal runtime) -----------
FROM node:20-alpine AS runner
WORKDIR /app

# Создание непривилегированного пользователя
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Установка только необходимых пакетов
RUN apk add --no-cache dumb-init curl && \
    npm install -g pnpm@10.12.4

# Копирование только необходимых файлов
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static/
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

# Настройка безопасности
USER nextjs

# Метаданные образа
LABEL maintainer="team@company.com" \
      version="1.0" \
      description="Production Next.js application"

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