# Этап 1: Установка зависимостей и сборка
FROM node:20-alpine AS builder
WORKDIR /app

# Устанавливаем pnpm
RUN npm install -g pnpm

# Копируем package.json и pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Устанавливаем все зависимости (включая dev)
RUN pnpm install --frozen-lockfile

# Копируем исходники
COPY . .

# Собираем проект
RUN pnpm build

# Этап 2: Production-образ
FROM node:20-alpine AS runner
WORKDIR /app

# Устанавливаем pnpm
RUN npm install -g pnpm

# Создаем пользователя без root прав
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Копируем только необходимые файлы
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3000

CMD ["node_modules/.bin/next", "start"] 