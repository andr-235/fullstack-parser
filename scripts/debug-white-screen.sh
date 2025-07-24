#!/bin/bash

echo "=== Диагностика белого экрана ==="
echo

echo "1. Проверка статуса контейнеров:"
docker compose ps
echo

echo "2. Проверка логов nginx:"
docker compose logs nginx --tail=10
echo

echo "3. Проверка логов frontend:"
docker compose logs frontend --tail=10
echo

echo "4. Проверка логов backend:"
docker compose logs backend --tail=10
echo

echo "5. Проверка health check nginx:"
curl -k -s -o /dev/null -w "%{http_code}" https://localhost/health
echo " - HTTP статус health check"

echo "6. Проверка API backend:"
curl -k -s -o /dev/null -w "%{http_code}" https://localhost/api/v1/health/
echo " - HTTP статус API health"

echo "7. Проверка frontend (dashboard):"
curl -k -s -o /dev/null -w "%{http_code}" https://localhost/dashboard
echo " - HTTP статус dashboard"

echo "8. Проверка переменных окружения frontend:"
docker compose exec frontend env | grep -E "(NEXT_PUBLIC_|API_)" | head -5
echo

echo "9. Проверка сетевых соединений:"
docker compose exec frontend netstat -tuln | grep -E "(3000|8000)" || echo "netstat недоступен"
echo

echo "=== Диагностика завершена ===" 