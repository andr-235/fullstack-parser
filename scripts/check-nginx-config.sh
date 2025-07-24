#!/bin/bash

# =============================================================================
# NGINX CONFIGURATION CHECK SCRIPT
# =============================================================================
# Скрипт для проверки конфигурации Nginx с self-signed сертификатом

set -e

echo "🔍 Проверка конфигурации Nginx..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Проверка наличия конфигурационного файла
if [ -f "nginx/nginx.prod.ip.conf" ]; then
    print_status "OK" "Конфигурационный файл найден"
else
    print_status "ERROR" "Конфигурационный файл не найден"
    exit 1
fi

# Проверка SSL сертификатов
if [ -f "nginx/ssl/selfsigned.crt" ] && [ -f "nginx/ssl/selfsigned.key" ]; then
    print_status "OK" "Self-signed SSL сертификаты найдены"
    
    # Проверка прав доступа к ключу
    if [ "$(stat -c %a nginx/ssl/selfsigned.key)" = "600" ]; then
        print_status "OK" "Права доступа к SSL ключу корректны (600)"
    else
        print_status "WARNING" "Права доступа к SSL ключу должны быть 600"
        chmod 600 nginx/ssl/selfsigned.key
    fi
else
    print_status "ERROR" "SSL сертификаты не найдены"
    exit 1
fi

# Проверка синтаксиса конфигурации
echo "🔧 Проверка синтаксиса конфигурации..."
if nginx -t -c "$(pwd)/nginx/nginx.prod.ip.conf" 2>/dev/null; then
    print_status "OK" "Синтаксис конфигурации корректен"
else
    print_status "ERROR" "Ошибка в синтаксисе конфигурации"
    nginx -t -c "$(pwd)/nginx/nginx.prod.ip.conf"
    exit 1
fi

# Проверка SSL сертификата
echo "🔐 Проверка SSL сертификата..."
if openssl x509 -in nginx/ssl/selfsigned.crt -text -noout >/dev/null 2>&1; then
    print_status "OK" "SSL сертификат валиден"
    
    # Проверка даты истечения
    expiry_date=$(openssl x509 -in nginx/ssl/selfsigned.crt -noout -enddate | cut -d= -f2)
    echo "📅 Дата истечения сертификата: $expiry_date"
else
    print_status "ERROR" "SSL сертификат поврежден"
    exit 1
fi

# Проверка SSL ключа
echo "🔑 Проверка SSL ключа..."
if openssl rsa -in nginx/ssl/selfsigned.key -check -noout >/dev/null 2>&1; then
    print_status "OK" "SSL ключ валиден"
else
    print_status "ERROR" "SSL ключ поврежден"
    exit 1
fi

# Проверка соответствия сертификата и ключа
echo "🔗 Проверка соответствия сертификата и ключа..."
cert_modulus=$(openssl x509 -in nginx/ssl/selfsigned.crt -noout -modulus | openssl md5)
key_modulus=$(openssl rsa -in nginx/ssl/selfsigned.key -noout -modulus | openssl md5)

if [ "$cert_modulus" = "$key_modulus" ]; then
    print_status "OK" "Сертификат и ключ соответствуют"
else
    print_status "ERROR" "Сертификат и ключ не соответствуют"
    exit 1
fi

# Проверка домена в сертификате
echo "🌐 Проверка домена в сертификате..."
cert_cn=$(openssl x509 -in nginx/ssl/selfsigned.crt -noout -subject | sed -n 's/.*CN = \(.*\)/\1/p')
if [ "$cert_cn" = "parser.mysite.ru" ]; then
    print_status "OK" "Домен в сертификате корректен: $cert_cn"
else
    print_status "WARNING" "Домен в сертификате: $cert_cn (ожидался: parser.mysite.ru)"
fi

# Проверка портов
echo "🔌 Проверка портов..."
if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    print_status "WARNING" "Порт 80 уже занят"
else
    print_status "OK" "Порт 80 свободен"
fi

if netstat -tlnp 2>/dev/null | grep -q ":443 "; then
    print_status "WARNING" "Порт 443 уже занят"
else
    print_status "OK" "Порт 443 свободен"
fi

echo ""
echo "🎉 Проверка завершена успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Скопируйте конфигурацию: sudo cp nginx/nginx.prod.ip.conf /etc/nginx/sites-available/parser.mysite.ru"
echo "2. Активируйте сайт: sudo ln -s /etc/nginx/sites-available/parser.mysite.ru /etc/nginx/sites-enabled/"
echo "3. Скопируйте SSL сертификаты: sudo cp -r nginx/ssl /etc/nginx/"
echo "4. Проверьте конфигурацию: sudo nginx -t"
echo "5. Перезапустите Nginx: sudo systemctl reload nginx"
echo ""
echo "⚠️  Внимание: Self-signed сертификат вызовет предупреждение в браузере!"
echo "   Для продакшена рекомендуется использовать Let's Encrypt сертификаты." 