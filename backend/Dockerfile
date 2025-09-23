# Multi-stage build for Go application (api or worker)

# Builder stage
FROM golang:1.25.1-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build argument for target (default: api)
ARG TARGET=api

# Build the binary
RUN go build -o /app/${TARGET} cmd/${TARGET}/main.go

# Runtime stage
FROM alpine:latest

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/${TARGET} /app/${TARGET}

# Run the binary
CMD ["/app/${TARGET}"]