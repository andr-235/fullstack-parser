# ===========================================
# Build stage - компиляция Go приложения
# ===========================================
FROM golang:1.25.1-alpine AS builder

# Установка необходимых пакетов для сборки
RUN apk add --no-cache git ca-certificates tzdata

# Создание пользователя для безопасности
RUN adduser -D -g '' appuser

# Установка рабочей директории
WORKDIR /build

# Копирование файлов зависимостей для кэширования слоев
COPY go.mod go.sum ./

# Загрузка зависимостей
RUN go mod download && go mod verify

# Копирование исходного кода
COPY . .

# Сборка приложения с оптимизациями
RUN CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    go build \
    -ldflags='-w -s -extldflags "-static"' \
    -a -installsuffix cgo \
    -o main \
    ./cmd/api

# ===========================================
# Test stage - запуск тестов
# ===========================================
FROM builder AS test

# Запуск тестов
RUN go test -v -race -coverprofile=coverage.out ./...

# ===========================================
# Runtime stage - минимальный runtime образ
# ===========================================
FROM alpine:3.21 AS runtime

# Установка необходимых пакетов для runtime
RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    && rm -rf /var/cache/apk/*

# Создание пользователя для безопасности
RUN adduser -D -g '' appuser

# Установка рабочей директории
WORKDIR /app

# Копирование скомпилированного бинарника из build stage
COPY --from=builder /build/main .

# Копирование миграций (если нужны)
COPY --from=builder /build/migrations ./migrations

# Создание директории для логов
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Открытие порта приложения
EXPOSE 8080

# Переменные окружения по умолчанию
ENV GIN_MODE=release
ENV PORT=8080

# Health check для контейнера
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Запуск приложения
CMD ["./main"]
