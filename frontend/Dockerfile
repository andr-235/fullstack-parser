# Этап 1: Установка зависимостей и сборка
FROM node:20-alpine AS builder
WORKDIR /app
# Устанавливаем ENV, чтобы next.config.js включил 'output: standalone'
ENV DOCKER=true

# Устанавливаем pnpm
RUN npm install -g pnpm

# Копируем package.json и pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Устанавливаем все зависимости (включая dev)
RUN pnpm install --frozen-lockfile

# Копируем исходники
COPY . .

# Собираем проект. `output: 'standalone'` в next.config.js создаст папку .next/standalone
RUN pnpm build

# Этап 2: Production-образ
FROM node:20-alpine AS runner
WORKDIR /app

# Устанавливаем wget для healthcheck
RUN apk add --no-cache wget

# Создаем пользователя без root прав
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Копируем standalone-вывод, статику и публичные файлы из сборщика
# Эта конфигурация использует 'output: standalone' из Next.js для создания
# минимального, оптимизированного production-образа.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

# Запускаем приложение через server.js из standalone-сборки
CMD ["node", "server.js"] 