#!/bin/bash

echo "=== Исправление белого экрана ==="
echo

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "1. Проверка текущего состояния..."
./scripts/check-white-screen-causes.sh
echo

echo "2. Очистка кеша браузера (рекомендация для пользователя):"
echo -e "${YELLOW}Выполните в браузере:${NC}"
echo "  - Нажмите Ctrl+Shift+R (жесткая перезагрузка)"
echo "  - Или откройте Developer Tools (F12) → Network → Disable cache"
echo "  - Или очистите кеш в настройках браузера"
echo

echo "3. Проверка консоли браузера (рекомендация для пользователя):"
echo -e "${YELLOW}Откройте Developer Tools (F12) и проверьте:${NC}"
echo "  - Console tab на ошибки JavaScript"
echo "  - Network tab на неудачные запросы (красные)"
echo "  - Application tab → Storage → Clear storage"
echo

echo "4. Проверка SSL сертификата..."
if curl -k -s https://localhost/health > /dev/null; then
    echo -e "${GREEN}✓${NC} SSL соединение работает"
else
    echo -e "${RED}✗${NC} Проблемы с SSL"
fi
echo

echo "5. Проверка API endpoints..."
echo -n "Backend API: "
if curl -k -s https://localhost/api/v1/health/ > /dev/null; then
    echo -e "${GREEN}✓${NC} Работает"
else
    echo -e "${RED}✗${NC} Не отвечает"
fi

echo -n "Frontend: "
if curl -k -s https://localhost/dashboard > /dev/null; then
    echo -e "${GREEN}✓${NC} Работает"
else
    echo -e "${RED}✗${NC} Не отвечает"
fi
echo

echo "6. Перезапуск сервисов для очистки состояния..."
docker compose restart frontend
sleep 5
docker compose restart nginx
sleep 10
echo

echo "7. Финальная проверка..."
docker compose ps --format "table {{.Name}}\t{{.Status}}"
echo

echo "8. Если проблема остается:"
echo -e "${YELLOW}Дополнительные шаги:${NC}"
echo "1. Проверьте логи в реальном времени:"
echo "   docker compose logs -f frontend"
echo "   docker compose logs -f nginx"
echo
echo "2. Проверьте переменные окружения:"
echo "   docker compose exec frontend env | grep NEXT_PUBLIC"
echo
echo "3. Проверьте сетевые соединения:"
echo "   docker compose exec frontend netstat -tuln"
echo
echo "4. Если все еще белый экран, попробуйте:"
echo "   - Открыть сайт в режиме инкогнито"
echo "   - Использовать другой браузер"
echo "   - Проверить настройки прокси/файрвола"
echo

echo -e "${GREEN}=== Исправление завершено ===${NC}"
echo "Теперь откройте https://localhost в браузере"
echo "Если видите белый экран, используйте DebugPanel (кнопка в правом нижнем углу)" 