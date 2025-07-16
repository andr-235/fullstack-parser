#!/bin/bash

# 🚀 Скрипт для деплоя на продакшн
# Использование: ./scripts/deploy-production.sh

set -e  # Остановка при ошибке

echo "🚀 Начинаем деплой на продакшн..."

# Проверка наличия переменных окружения
if [ -z "$GHCR_USERNAME" ] || [ -z "$GHCR_TOKEN" ]; then
    echo "❌ Ошибка: Не установлены переменные GHCR_USERNAME или GHCR_TOKEN"
    echo "Установите их в .env.prod или экспортируйте в текущей сессии"
    exit 1
fi

# Очистка старых образов перед деплоем
echo "🧹 Очистка старых образов..."
./scripts/docker-cleanup.sh

# Логин в Container Registry
echo "🔐 Логин в Container Registry..."
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin

# Загрузка образов
echo "📦 Загрузка Docker образов..."
docker-compose -f docker-compose.prod.ip.yml pull

# Запуск сервисов
echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.prod.ip.yml up -d --build

# Очистка после деплоя
echo "🧹 Очистка после деплоя..."
./scripts/docker-cleanup.sh

# Проверка статуса
echo "🔍 Проверка статуса сервисов..."
sleep 10  # Даем время на запуск
docker-compose -f docker-compose.prod.ip.yml ps

echo "✅ Деплой завершен успешно!"
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.prod.ip.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
