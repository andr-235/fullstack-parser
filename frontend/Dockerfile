# Frontend Dockerfile for pnpm
FROM node:18-alpine AS base

# Install pnpm globally
RUN npm install -g pnpm@10

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Install dependencies with pnpm
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# Development stage for local development
FROM base AS development
WORKDIR /app

# Используем уже установленные зависимости из слоя deps
COPY --from=deps /app/node_modules ./node_modules

# Копируем манифесты (на случай, если локально что-то изменилось; при изменении package.json слой кеша пересоберётся)
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./

# Копируем исходники приложения
COPY . .

# Expose port
EXPOSE 3000

# Start development server with correct host binding for Docker
CMD ["pnpm", "dev"]

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
ARG DOCKER=1
ENV DOCKER=$DOCKER
COPY --from=deps /app/node_modules ./node_modules
RUN mkdir -p public
COPY . .

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED 1

RUN pnpm run build

# Production image, copy all the files and run next
FROM base AS production
WORKDIR /app

ARG DOCKER=1
ENV DOCKER=$DOCKER
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"] 