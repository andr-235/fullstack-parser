# Multi-stage Dockerfile for Next.js 15 Frontend Application with Bun
FROM oven/bun:1.2.21-alpine AS deps

RUN apk add --no-cache libc6-compat
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

WORKDIR /app

COPY package.json bun.lock ./
ENV BUN_INSTALL_CACHE_DIR=/tmp/bun-cache

RUN --mount=type=cache,target=/tmp/bun-cache \
    bun install

FROM oven/bun:1.2.21-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/bun.lock ./bun.lock

COPY . .

RUN mkdir -p ./public

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    DOCKER=true \
    CI=true

RUN --mount=type=cache,target=/app/.next/cache \
    bun run build

FROM node:20-alpine AS runner
WORKDIR /app

RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
RUN apk add --no-cache dumb-init curl

COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static/
COPY --from=deps --chown=nextjs:nodejs /app/package.json ./package.json

USER nextjs

EXPOSE 3000

ENV PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"] 