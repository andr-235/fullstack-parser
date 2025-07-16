#!/bin/bash

# 🧹 Скрипт для очистки Docker образов и кэша
# Использование: ./scripts/docker-cleanup.sh [--aggressive]

set -e

echo "🧹 Начинаем очистку Docker..."

# Проверяем аргументы
AGGRESSIVE=false
if [[ "$1" == "--aggressive" ]]; then
    AGGRESSIVE=true
    echo "⚠️ Режим агрессивной очистки включен"
fi

# Останавливаем неиспользуемые контейнеры
echo "🛑 Остановка неиспользуемых контейнеров..."
docker container prune -f || true

# Удаляем неиспользуемые образы
echo "🗑️ Удаление неиспользуемых образов..."
if [[ "$AGGRESSIVE" == "true" ]]; then
    docker image prune -a -f || true
else
    docker image prune -f || true
fi

# Удаляем неиспользуемые volumes
echo "🗑️ Удаление неиспользуемых volumes..."
docker volume prune -f || true

# Удаляем неиспользуемые сети
echo "🗑️ Удаление неиспользуемых сетей..."
docker network prune -f || true

# Очищаем build cache
echo "🗑️ Очистка build cache..."
docker builder prune -f || true

# Полная очистка системы (если агрессивный режим)
if [[ "$AGGRESSIVE" == "true" ]]; then
    echo "🧹 Полная очистка системы..."
    docker system prune -a -f || true
fi

# Показываем статистику
echo "📊 Статистика после очистки:"
docker system df

echo "✅ Очистка Docker завершена!"
