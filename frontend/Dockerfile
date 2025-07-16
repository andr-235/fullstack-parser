# syntax=docker/dockerfile:1.6

# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Build args
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV DOCKER=true

# Устанавливаем pnpm нужной версии
RUN npm install -g pnpm@10.12.4

# Копируем только package.json и pnpm-lock.yaml для layer caching
COPY package.json pnpm-lock.yaml ./

# Устанавливаем зависимости
RUN pnpm install --frozen-lockfile

# Копируем исходники (исключая тесты, .git и т.д.)
COPY . .

# Собираем проект (standalone)
RUN pnpm build

# Stage 2: Development
FROM node:20-alpine AS dev
WORKDIR /app

RUN npm install -g pnpm@10.12.4

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .

ENV NODE_ENV=development
EXPOSE 3000

CMD ["pnpm", "dev"]

# Stage 3: Production
FROM node:20-alpine3.18 AS production
WORKDIR /app

# Устанавливаем curl только для healthcheck
RUN apk add --no-cache curl

# Создаём non-root пользователя
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# Копируем только необходимые артефакты из builder
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Устанавливаем переменные окружения
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=20s --start-period=60s --retries=3 \
    CMD curl -f --max-time 15 http://localhost:3000 || exit 1

CMD ["node", "server.js"]
