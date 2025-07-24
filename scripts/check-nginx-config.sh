#!/bin/bash

# =============================================================================
# NGINX CONFIGURATION CHECK SCRIPT
# =============================================================================
# Проверка конфигурации Nginx и SSL сертификата

set -e

DOMAIN="parser.mysite.ru"
NGINX_CONF="/etc/nginx/nginx.conf"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Проверка синтаксиса конфигурации Nginx
check_nginx_syntax() {
    log "Проверка синтаксиса конфигурации Nginx..."
    
    if nginx -t; then
        log "✓ Синтаксис конфигурации Nginx корректен"
        return 0
    else
        error "✗ Ошибка в синтаксисе конфигурации Nginx"
        return 1
    fi
}

# Проверка статуса Nginx
check_nginx_status() {
    log "Проверка статуса Nginx..."
    
    if systemctl is-active --quiet nginx; then
        log "✓ Nginx запущен"
        return 0
    else
        error "✗ Nginx не запущен"
        return 1
    fi
}

# Проверка SSL сертификата
check_ssl_certificate() {
    log "Проверка SSL сертификата для $DOMAIN..."
    
    local cert_path="/etc/letsencrypt/live/$DOMAIN/cert.pem"
    local key_path="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
    
    # Проверка существования файлов
    if [[ ! -f "$cert_path" ]]; then
        error "✗ SSL сертификат не найден: $cert_path"
        return 1
    fi
    
    if [[ ! -f "$key_path" ]]; then
        error "✗ SSL ключ не найден: $key_path"
        return 1
    fi
    
    log "✓ SSL файлы найдены"
    
    # Проверка срока действия сертификата
    local expiry_date=$(openssl x509 -in "$cert_path" -noout -enddate 2>/dev/null | cut -d= -f2)
    if [[ -n "$expiry_date" ]]; then
        local expiry_timestamp=$(date -d "$expiry_date" +%s 2>/dev/null)
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        if [[ $days_until_expiry -gt 30 ]]; then
            log "✓ Сертификат действителен до: $expiry_date (осталось $days_until_expiry дней)"
        elif [[ $days_until_expiry -gt 0 ]]; then
            warn "⚠ Сертификат истекает через $days_until_expiry дней: $expiry_date"
        else
            error "✗ Сертификат истек: $expiry_date"
            return 1
        fi
    else
        warn "⚠ Не удалось получить дату истечения сертификата"
    fi
    
    return 0
}

# Проверка доступности HTTP
check_http_access() {
    log "Проверка HTTP доступности..."
    
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" --connect-timeout 10)
    
    if [[ "$http_status" == "301" || "$http_status" == "302" ]]; then
        log "✓ HTTP редирект работает (статус: $http_status)"
        return 0
    elif [[ "$http_status" == "200" ]]; then
        warn "⚠ HTTP возвращает 200 (должен быть редирект на HTTPS)"
        return 1
    else
        error "✗ HTTP недоступен (статус: $http_status)"
        return 1
    fi
}

# Проверка доступности HTTPS
check_https_access() {
    log "Проверка HTTPS доступности..."
    
    local https_status=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" --connect-timeout 10)
    
    if [[ "$https_status" == "200" ]]; then
        log "✓ HTTPS доступен (статус: $https_status)"
        return 0
    else
        error "✗ HTTPS недоступен (статус: $https_status)"
        return 1
    fi
}

# Проверка SSL соединения
check_ssl_connection() {
    log "Проверка SSL соединения..."
    
    local ssl_info=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null)
    
    if [[ -n "$ssl_info" ]]; then
        log "✓ SSL соединение установлено"
        echo "$ssl_info" | while read line; do
            info "  $line"
        done
        return 0
    else
        error "✗ Не удалось установить SSL соединение"
        return 1
    fi
}

# Проверка заголовков безопасности
check_security_headers() {
    log "Проверка заголовков безопасности..."
    
    local headers=$(curl -s -I "https://$DOMAIN" --connect-timeout 10)
    local missing_headers=()
    
    # Проверка HSTS
    if ! echo "$headers" | grep -q "Strict-Transport-Security"; then
        missing_headers+=("HSTS")
    fi
    
    # Проверка X-Frame-Options
    if ! echo "$headers" | grep -q "X-Frame-Options"; then
        missing_headers+=("X-Frame-Options")
    fi
    
    # Проверка X-Content-Type-Options
    if ! echo "$headers" | grep -q "X-Content-Type-Options"; then
        missing_headers+=("X-Content-Type-Options")
    fi
    
    if [[ ${#missing_headers[@]} -eq 0 ]]; then
        log "✓ Все основные заголовки безопасности присутствуют"
        return 0
    else
        warn "⚠ Отсутствуют заголовки безопасности: ${missing_headers[*]}"
        return 1
    fi
}

# Проверка портов
check_ports() {
    log "Проверка открытых портов..."
    
    local ports=("80" "443")
    
    for port in "${ports[@]}"; do
        if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
            log "✓ Порт $port открыт"
        else
            error "✗ Порт $port не открыт"
        fi
    done
}

# Проверка DNS
check_dns() {
    log "Проверка DNS записи для $DOMAIN..."
    
    local ip=$(nslookup "$DOMAIN" 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    
    if [[ -n "$ip" ]]; then
        log "✓ DNS резолвится в IP: $ip"
        return 0
    else
        error "✗ DNS не резолвится"
        return 1
    fi
}

# Основная функция проверки
main() {
    log "Начало проверки конфигурации Nginx для домена $DOMAIN"
    echo
    
    local errors=0
    
    # Выполнение проверок
    check_dns || ((errors++))
    echo
    
    check_nginx_syntax || ((errors++))
    echo
    
    check_nginx_status || ((errors++))
    echo
    
    check_ports
    echo
    
    check_ssl_certificate || ((errors++))
    echo
    
    check_http_access || ((errors++))
    echo
    
    check_https_access || ((errors++))
    echo
    
    check_ssl_connection || ((errors++))
    echo
    
    check_security_headers || ((errors++))
    echo
    
    # Итоговый результат
    if [[ $errors -eq 0 ]]; then
        log "✓ Все проверки пройдены успешно!"
        log "Домен $DOMAIN настроен корректно для HTTPS"
    else
        error "✗ Найдено $errors ошибок. Проверьте конфигурацию."
        exit 1
    fi
}

# Запуск основной функции
main "$@" 