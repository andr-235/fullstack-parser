#!/bin/bash

echo "Starting Docker containers..."

# Останавливаем все контейнеры
docker-compose -f docker-compose.prod.yml down

# Запускаем базовые сервисы
echo "Starting postgres and redis..."
docker-compose -f docker-compose.prod.yml up -d postgres redis

# Ждем готовности postgres
echo "Waiting for postgres..."
sleep 10

# Запускаем API
echo "Starting API..."
docker-compose -f docker-compose.prod.yml up -d api

# Ждем готовности API
echo "Waiting for API..."
sleep 10

# Запускаем frontend
echo "Starting frontend..."
docker-compose -f docker-compose.prod.yml up -d frontend

# Ждем готовности frontend
echo "Waiting for frontend..."
sleep 10

# Запускаем остальные сервисы
echo "Starting remaining services..."
docker-compose -f docker-compose.prod.yml up -d celery-worker celery-beat flower nginx

echo "All services started!"
docker-compose -f docker-compose.prod.yml ps
