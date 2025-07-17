# =============================================================================
# Multi-stage Dockerfile for Next.js 15 Frontend Application
# =============================================================================

# ----------- Stage 1: Install dependencies (with cache) -----------
FROM node:20-alpine AS deps
# Устанавливаем pnpm глобально
RUN npm install -g pnpm@10.12.4
WORKDIR /app
# Копируем только package.json и lock-файл для кеширования зависимостей
COPY package.json pnpm-lock.yaml ./
# Устанавливаем только prod и build зависимости (dev не нужны для рантайма)
RUN pnpm install --frozen-lockfile

# ----------- Stage 2: Build application -----------
FROM node:20-alpine AS builder
RUN npm install -g pnpm@10.12.4
WORKDIR /app
# Копируем установленные зависимости
COPY --from=deps /app/node_modules ./node_modules
# Копируем исходники
COPY . .
# Отключаем телеметрию и явно указываем production
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production
# Собираем приложение
RUN pnpm build

# ----------- Stage 3: Production image -----------
FROM node:20-alpine AS runner
# Создаём непривилегированного пользователя
RUN addgroup -S nextjs && adduser -S nextjs -G nextjs
WORKDIR /app
# Устанавливаем dumb-init для корректного завершения процессов
RUN apk add --no-cache dumb-init
# Копируем необходимые артефакты для запуска
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
# Копируем .env.production если нужен (раскомментируй если используешь)
# COPY .env.production .
# Меняем владельца файлов на непривилегированного пользователя
RUN chown -R nextjs:nextjs .
USER nextjs
# Экспонируем стандартный порт Next.js
EXPOSE 3000
# Важные переменные окружения
ENV PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1
# Запускаем через dumb-init для корректного завершения
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"] 