# =============================================================================
# Multi-stage Dockerfile for Next.js 15 Frontend Application
# =============================================================================

# ----------- Stage 1: Install dependencies (with cache) -----------
FROM node:20-alpine AS deps
RUN npm install -g pnpm@10.12.4
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ----------- Stage 2: Build application -----------
FROM node:20-alpine AS builder
RUN npm install -g pnpm@10.12.4
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    DOCKER=true
RUN pnpm build

# ----------- Stage 3: Production image -----------
FROM node:20-alpine AS runner
RUN addgroup -S nextjs && adduser -S nextjs -G nextjs
WORKDIR /app
RUN apk add --no-cache dumb-init
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static/
USER nextjs
EXPOSE 3000
ENV PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"] 