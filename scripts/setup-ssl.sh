#!/bin/bash

# =============================================================================
# SSL SETUP SCRIPT FOR parser.mysite.ru
# =============================================================================
# Автоматическая настройка SSL сертификата Let's Encrypt

set -e

DOMAIN="parser.mysite.ru"
EMAIL="andreyvins2015@yandex.ru"  # Замените на ваш email
NGINX_CONF="/etc/nginx/nginx.conf"
CERTBOT_PATH="/usr/bin/certbot"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    exit 1
}

# Проверка прав root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Этот скрипт должен быть запущен с правами root"
    fi
}

# Проверка зависимостей
check_dependencies() {
    log "Проверка зависимостей..."
    
    # Проверка certbot
    if ! command -v certbot &> /dev/null; then
        log "Установка certbot..."
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Проверка nginx
    if ! command -v nginx &> /dev/null; then
        error "Nginx не установлен"
    fi
    
    # Проверка docker
    if ! command -v docker &> /dev/null; then
        warn "Docker не найден, но может быть не нужен для standalone режима"
    fi
}

# Проверка доступности домена
check_domain() {
    log "Проверка доступности домена $DOMAIN..."
    
    # Проверка DNS
    if ! nslookup $DOMAIN &> /dev/null; then
        error "Домен $DOMAIN недоступен. Проверьте DNS настройки."
    fi
    
    # Проверка HTTP доступности
    if ! curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" | grep -q "200\|301\|302"; then
        warn "Домен $DOMAIN не отвечает на HTTP. Убедитесь что сервер запущен."
    fi
}

# Создание временной конфигурации для certbot
create_temp_nginx_conf() {
    log "Создание временной конфигурации Nginx для certbot..."
    
    cat > /tmp/nginx-certbot.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
}

# Получение SSL сертификата
get_ssl_certificate() {
    log "Получение SSL сертификата для $DOMAIN..."
    
    # Создание директории для ACME challenge
    mkdir -p /var/www/certbot
    
    # Получение сертификата
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --domains $DOMAIN \
        --non-interactive \
        --force-renewal
    
    if [ $? -eq 0 ]; then
        log "SSL сертификат успешно получен!"
    else
        error "Ошибка при получении SSL сертификата"
    fi
}

# Настройка автообновления сертификата
setup_auto_renewal() {
    log "Настройка автообновления сертификата..."
    
    # Создание скрипта обновления
    cat > /usr/local/bin/renew-ssl.sh << 'EOF'
#!/bin/bash
certbot renew --quiet --post-hook "systemctl reload nginx"
EOF
    
    chmod +x /usr/local/bin/renew-ssl.sh
    
    # Добавление в crontab (обновление каждый день в 3:00)
    (crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/renew-ssl.sh") | crontab -
    
    log "Автообновление настроено (каждый день в 3:00)"
}

# Проверка конфигурации Nginx
test_nginx_config() {
    log "Проверка конфигурации Nginx..."
    
    if nginx -t; then
        log "Конфигурация Nginx корректна"
    else
        error "Ошибка в конфигурации Nginx"
    fi
}

# Перезапуск Nginx
reload_nginx() {
    log "Перезагрузка Nginx..."
    
    if systemctl reload nginx; then
        log "Nginx успешно перезагружен"
    else
        error "Ошибка при перезагрузке Nginx"
    fi
}

# Проверка SSL сертификата
verify_ssl() {
    log "Проверка SSL сертификата..."
    
    # Проверка срока действия
    local expiry_date=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/cert.pem -noout -enddate | cut -d= -f2)
    log "Сертификат действителен до: $expiry_date"
    
    # Проверка доступности HTTPS
    if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" | grep -q "200\|301\|302"; then
        log "HTTPS доступен для домена $DOMAIN"
    else
        warn "HTTPS недоступен. Проверьте конфигурацию."
    fi
}

# Основная функция
main() {
    log "Начало настройки SSL для домена $DOMAIN"
    
    check_root
    check_dependencies
    check_domain
    create_temp_nginx_conf
    get_ssl_certificate
    setup_auto_renewal
    test_nginx_config
    reload_nginx
    verify_ssl
    
    log "Настройка SSL завершена успешно!"
    log "Домен $DOMAIN теперь доступен по HTTPS"
    log "Сертификат будет автоматически обновляться"
}

# Запуск основной функции
main "$@" 