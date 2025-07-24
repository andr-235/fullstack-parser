#!/bin/bash

# =============================================================================
# SSL CERTIFICATE CHECK SCRIPT
# =============================================================================
# Скрипт для проверки SSL сертификата

set -e

echo "🔐 Проверка SSL сертификата..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Проверка SSL сертификата через OpenSSL
echo "🔍 Проверка SSL соединения..."
if openssl s_client -connect localhost:443 -servername parser.mysite.ru < /dev/null 2>/dev/null | openssl x509 -noout -text > /dev/null 2>&1; then
    print_status "OK" "SSL соединение установлено"
else
    print_status "ERROR" "Не удалось установить SSL соединение"
    exit 1
fi

# Получение информации о сертификате
echo "📋 Информация о сертификате:"
echo ""

# Subject
subject=$(openssl s_client -connect localhost:443 -servername parser.mysite.ru < /dev/null 2>/dev/null | openssl x509 -noout -subject 2>/dev/null)
echo -e "${BLUE}Subject:${NC} $subject"

# Issuer
issuer=$(openssl s_client -connect localhost:443 -servername parser.mysite.ru < /dev/null 2>/dev/null | openssl x509 -noout -issuer 2>/dev/null)
echo -e "${BLUE}Issuer:${NC} $issuer"

# Даты
echo ""
echo -e "${BLUE}Даты действия:${NC}"
openssl s_client -connect localhost:443 -servername parser.mysite.ru < /dev/null 2>/dev/null | openssl x509 -noout -dates 2>/dev/null

# Проверка домена
echo ""
echo "🌐 Проверка домена в сертификате..."
cert_cn=$(openssl s_client -connect localhost:443 -servername parser.mysite.ru < /dev/null 2>/dev/null | openssl x509 -noout -subject 2>/dev/null | sed -n 's/.*CN = \(.*\)/\1/p')
if [ "$cert_cn" = "parser.mysite.ru" ]; then
    print_status "OK" "Домен в сертификате корректен: $cert_cn"
else
    print_status "WARNING" "Домен в сертификате: $cert_cn (ожидался: parser.mysite.ru)"
fi

# Проверка HTTP редиректа
echo ""
echo "🔄 Проверка HTTP редиректа..."
http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
if [ "$http_status" = "301" ] || [ "$http_status" = "302" ]; then
    print_status "OK" "HTTP редирект работает (статус: $http_status)"
else
    print_status "WARNING" "HTTP возвращает статус: $http_status (ожидался 301 или 302)"
fi

# Проверка HTTPS доступности
echo ""
echo "🔒 Проверка HTTPS доступности..."
https_status=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost/ 2>/dev/null)
if [ "$https_status" = "200" ] || [ "$https_status" = "307" ]; then
    print_status "OK" "HTTPS доступен (статус: $https_status)"
else
    print_status "ERROR" "HTTPS недоступен (статус: $https_status)"
fi

# Проверка заголовков безопасности
echo ""
echo "🛡️ Проверка заголовков безопасности..."
headers=$(curl -k -s -I https://localhost/ 2>/dev/null)

# HSTS
if echo "$headers" | grep -q "Strict-Transport-Security"; then
    print_status "OK" "HSTS заголовок присутствует"
else
    print_status "WARNING" "HSTS заголовок отсутствует"
fi

# X-Frame-Options
if echo "$headers" | grep -q "X-Frame-Options"; then
    print_status "OK" "X-Frame-Options заголовок присутствует"
else
    print_status "WARNING" "X-Frame-Options заголовок отсутствует"
fi

# X-Content-Type-Options
if echo "$headers" | grep -q "X-Content-Type-Options"; then
    print_status "OK" "X-Content-Type-Options заголовок присутствует"
else
    print_status "WARNING" "X-Content-Type-Options заголовок отсутствует"
fi

echo ""
echo "🎉 Проверка SSL завершена!"
echo ""
echo "📝 Примечания:"
echo "- Self-signed сертификат вызовет предупреждение в браузере"
echo "- Для продакшена рекомендуется использовать Let's Encrypt"
echo "- Сертификат действителен 365 дней"
echo ""
echo "🔗 Доступные URL:"
echo "- HTTP: http://localhost (редирект на HTTPS)"
echo "- HTTPS: https://localhost (с предупреждением о сертификате)"
echo "- API: https://localhost/api/v1/health/"
echo "- Dashboard: https://localhost/dashboard" 