#!/bin/bash

echo "=== Проверка причин белого экрана ==="
echo

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки статуса
check_status() {
    local service=$1
    local status=$(docker compose ps $service --format "table {{.Status}}" | tail -n 1)
    if [[ $status == *"healthy"* ]]; then
        echo -e "${GREEN}✓${NC} $service: $status"
    elif [[ $status == *"unhealthy"* ]]; then
        echo -e "${RED}✗${NC} $service: $status"
    else
        echo -e "${YELLOW}?${NC} $service: $status"
    fi
}

echo "1. Проверка статуса сервисов:"
check_status nginx
check_status frontend
check_status backend
check_status postgres
check_status redis
echo

echo "2. Проверка доступности сервисов:"
echo -n "Nginx health check: "
nginx_status=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost/health)
if [ "$nginx_status" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTP $nginx_status"
else
    echo -e "${RED}✗${NC} HTTP $nginx_status"
fi

echo -n "Backend API health: "
backend_status=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost/api/v1/health/)
if [ "$backend_status" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTP $backend_status"
else
    echo -e "${RED}✗${NC} HTTP $backend_status"
fi

echo -n "Frontend dashboard: "
frontend_status=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost/dashboard)
if [ "$frontend_status" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTP $frontend_status"
else
    echo -e "${RED}✗${NC} HTTP $frontend_status"
fi
echo

echo "3. Проверка логов на ошибки:"
echo "Nginx ошибки:"
docker compose logs nginx --tail=20 2>&1 | grep -i error || echo "Ошибок не найдено"

echo "Frontend ошибки:"
docker compose logs frontend --tail=20 2>&1 | grep -i error || echo "Ошибок не найдено"

echo "Backend ошибки:"
docker compose logs backend --tail=20 2>&1 | grep -i error || echo "Ошибок не найдено"
echo

echo "4. Проверка переменных окружения:"
echo "Frontend API URL:"
docker compose exec frontend env | grep NEXT_PUBLIC_API_URL || echo "NEXT_PUBLIC_API_URL не найден"

echo "Backend переменные:"
docker compose exec backend env | grep -E "(DATABASE_URL|REDIS_URL)" | head -2 || echo "Переменные БД не найдены"
echo

echo "5. Проверка сетевых соединений:"
echo "Frontend порты:"
docker compose exec frontend netstat -tuln 2>/dev/null | grep -E "(3000|8000)" || echo "netstat недоступен"

echo "Backend порты:"
docker compose exec backend netstat -tuln 2>/dev/null | grep -E "(8000|5432|6379)" || echo "netstat недоступен"
echo

echo "6. Проверка SSL сертификатов:"
if [ -f "nginx/ssl/selfsigned.crt" ]; then
    echo -e "${GREEN}✓${NC} SSL сертификат существует"
    openssl x509 -in nginx/ssl/selfsigned.crt -text -noout 2>/dev/null | grep -E "(Subject:|Not After)" | head -2
else
    echo -e "${RED}✗${NC} SSL сертификат не найден"
fi
echo

echo "7. Проверка конфигурации nginx:"
if docker compose exec nginx nginx -t 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Конфигурация nginx корректна"
else
    echo -e "${RED}✗${NC} Ошибка в конфигурации nginx"
fi
echo

echo "8. Проверка памяти и ресурсов:"
echo "Использование памяти контейнерами:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -6
echo

echo "9. Рекомендации по исправлению:"
echo "Если видите белый экран:"
echo "1. Откройте Developer Tools (F12) и проверьте Console на ошибки"
echo "2. Проверьте Network tab на неудачные запросы"
echo "3. Попробуйте очистить кеш браузера (Ctrl+Shift+R)"
echo "4. Проверьте, что все сервисы имеют статус 'healthy'"
echo "5. Убедитесь, что SSL сертификаты корректны"
echo

echo "=== Проверка завершена ===" 