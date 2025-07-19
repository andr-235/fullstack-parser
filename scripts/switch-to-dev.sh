#!/bin/bash

# =============================================================================
# SWITCH TO DEVELOPMENT MODE
# =============================================================================
# Скрипт для переключения проекта в режим разработки

set -e

echo "🔄 Переключение в режим разработки..."

# Проверяем наличие .env.dev
if [ ! -f ".env.dev" ]; then
    echo "❌ Файл .env.dev не найден!"
    echo "Создайте файл .env.dev на основе env.example"
    exit 1
fi

# Останавливаем текущие контейнеры
echo "🛑 Останавливаем текущие контейнеры..."
docker-compose down 2>/dev/null || true

# Удаляем старые контейнеры и volumes (опционально)
if [ "$1" = "--clean" ]; then
    echo "🧹 Очищаем старые контейнеры и volumes..."
    docker-compose down -v 2>/dev/null || true
    docker system prune -f
fi

# Запускаем в режиме разработки
echo "🚀 Запускаем в режиме разработки..."
docker-compose -f docker-compose.dev.yml up -d

# Ждем запуска сервисов
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Проверяем статус
echo "✅ Проверяем статус сервисов..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "🎉 Проект переключен в режим разработки!"
echo ""
echo "📱 Доступные адреса:"
echo "   - Приложение: http://localhost"
echo "   - API документация: http://localhost/api/docs"
echo "   - Health check: http://localhost/health"
echo ""
echo "📋 Полезные команды:"
echo "   - Логи: docker-compose -f docker-compose.dev.yml logs -f"
echo "   - Остановка: docker-compose -f docker-compose.dev.yml down"
echo "   - Перезапуск: docker-compose -f docker-compose.dev.yml restart" 