FROM oven/bun:1 as builder

ARG VITE_API_BASE_URL
ARG NODE_ENV=production
ENV NODE_ENV=production
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost/api}

WORKDIR /app

COPY frontend/package*.json .

RUN bun install --frozen-lockfile

COPY frontend/ .

RUN bun run build

# Используем Bun для раздачи статики
FROM oven/bun:1

WORKDIR /app

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["bunx", "serve", "dist", "-p", "3000"]