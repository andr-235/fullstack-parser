#!/bin/bash

# 🧹 Cron скрипт для автоматической очистки Docker
# Добавить в crontab: 0 2 * * * /opt/app/scripts/maintenance/docker-cleanup-cron.sh

set -e

LOG_FILE="/var/log/docker-cleanup.log"
APP_DIR="/opt/app"

# Переходим в директорию приложения
cd "$APP_DIR"

# Логируем начало
echo "$(date): 🧹 Начинаем автоматическую очистку Docker" >> "$LOG_FILE"

# Запускаем очистку
if ./scripts/docker-cleanup.sh >> "$LOG_FILE" 2>&1; then
    echo "$(date): ✅ Очистка Docker завершена успешно" >> "$LOG_FILE"
else
    echo "$(date): ❌ Ошибка при очистке Docker" >> "$LOG_FILE"
    exit 1
fi

# Показываем статистику
echo "$(date): 📊 Статистика Docker:" >> "$LOG_FILE"
docker system df >> "$LOG_FILE" 2>&1

echo "$(date): 🎯 Автоматическая очистка завершена" >> "$LOG_FILE"
