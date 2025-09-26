FROM oven/bun:1.1.0-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN bun install
COPY . .
RUN bun run build && [ -d dist ] || (echo "Build failed: dist directory not found" && exit 1)

FROM nginx:alpine as runner
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf