# Development stage
FROM node:18-slim AS development
WORKDIR /usr/src/app
COPY package*.json ./

# Оптимизация apt с быстрыми репозиториями и таймаутами
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    apt-get update -o Acquire::http::Timeout=10 -o Acquire::http::Pipeline-Depth=0 && \
    apt-get install -y --no-install-recommends openssl && \
    rm -rf /var/lib/apt/lists/*

RUN npm ci
COPY . .
USER node

# Build stage
FROM node:18-slim AS build
WORKDIR /usr/src/app
COPY package*.json ./

# Оптимизация apt с быстрыми репозиториями и таймаутами
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    apt-get update -o Acquire::http::Timeout=10 -o Acquire::http::Pipeline-Depth=0 && \
    apt-get install -y --no-install-recommends openssl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=development /usr/src/app/node_modules ./node_modules
COPY . .
RUN npm run build
ENV NODE_ENV production
RUN npm ci --only=production && npm cache clean --force
USER node

# Production stage
FROM node:18-slim AS production
WORKDIR /usr/src/app

# Устанавливаем OpenSSL и wget для Prisma и health check с оптимизацией
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    apt-get update -o Acquire::http::Timeout=10 -o Acquire::http::Pipeline-Depth=0 && \
    apt-get install -y --no-install-recommends openssl wget && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/src/app/node_modules ./node_modules
COPY --from=build /usr/src/app/dist ./dist
CMD ["node", "dist/src/main.js"]