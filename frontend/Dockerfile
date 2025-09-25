FROM oven/bun:1.1.0-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN bun install
COPY . .
RUN bun run build

FROM nginx:alpine as runner
COPY --from=builder /app/dist /usr/share/nginx/html