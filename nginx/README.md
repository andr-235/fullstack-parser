# Nginx HTTPS Configuration для parser.mysite.ru

## Обзор

Этот репозиторий содержит оптимизированную конфигурацию Nginx для домена `parser.mysite.ru` с поддержкой HTTPS и современными настройками безопасности.

## Основные особенности

- ✅ **HTTPS с Let's Encrypt** - автоматическое получение и обновление SSL сертификатов
- ✅ **HTTP/2 поддержка** - улучшенная производительность
- ✅ **Современные SSL настройки** - TLS 1.2/1.3 с безопасными шифрами
- ✅ **Заголовки безопасности** - HSTS, CSP, X-Frame-Options и др.
- ✅ **Rate limiting** - защита от DDoS атак
- ✅ **Gzip сжатие** - оптимизация передачи данных
- ✅ **Кеширование статических файлов** - улучшенная производительность
- ✅ **WebSocket поддержка** - для real-time функций
- ✅ **Автоматические редиректы** - HTTP → HTTPS, IP → домен

## Структура файлов

```
nginx/
├── nginx.prod.ip.conf          # Основная конфигурация Nginx
├── README.md                   # Эта документация
└── ssl/                        # SSL сертификаты (если используются self-signed)
    ├── selfsigned.crt
    └── selfsigned.key

scripts/
├── setup-ssl.sh               # Скрипт настройки SSL сертификата
└── check-nginx-config.sh      # Скрипт проверки конфигурации
```

## Быстрая настройка

### 1. Предварительные требования

- Домен `parser.mysite.ru` настроен и указывает на ваш сервер
- Nginx установлен и запущен
- Порты 80 и 443 открыты в файрволе
- Docker Compose с сервисами `frontend` и `backend`

### 2. Копирование конфигурации

```bash
# Копируем конфигурацию
sudo cp nginx/nginx.prod.ip.conf /etc/nginx/sites-available/parser.mysite.ru
sudo ln -s /etc/nginx/sites-available/parser.mysite.ru /etc/nginx/sites-enabled/

# Удаляем дефолтную конфигурацию
sudo rm -f /etc/nginx/sites-enabled/default
```

### 3. Получение SSL сертификата

```bash
# Запускаем скрипт настройки SSL
sudo ./scripts/setup-ssl.sh
```

**Примечание:** Перед запуском измените email в скрипте `setup-ssl.sh` на ваш.

### 4. Проверка конфигурации

```bash
# Проверяем конфигурацию
sudo ./scripts/check-nginx-config.sh
```

### 5. Перезапуск Nginx

```bash
sudo systemctl reload nginx
```

## Детальная настройка

### SSL сертификаты

Конфигурация настроена для работы с Let's Encrypt сертификатами:

```nginx
ssl_certificate /etc/letsencrypt/live/parser.mysite.ru/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/parser.mysite.ru/privkey.pem;
```

Если Let's Encrypt недоступен, раскомментируйте строки с self-signed сертификатом:

```nginx
# ssl_certificate /etc/nginx/ssl/selfsigned.crt;
# ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
```

### Настройки безопасности

#### SSL/TLS настройки

- **Протоколы:** TLS 1.2, TLS 1.3
- **Шифры:** Современные ECDHE шифры с ChaCha20-Poly1305
- **OCSP Stapling:** Включен для улучшения производительности
- **HSTS:** Включен с preload

#### Заголовки безопасности

- `Strict-Transport-Security` - принудительное HTTPS
- `X-Frame-Options` - защита от clickjacking
- `X-Content-Type-Options` - защита от MIME sniffing
- `X-XSS-Protection` - защита от XSS атак
- `Content-Security-Policy` - политика безопасности контента
- `Referrer-Policy` - контроль referrer информации
- `Permissions-Policy` - ограничение API браузера

### Rate Limiting

Настроены зоны ограничения запросов:

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=static:10m rate=30r/s;
```

- **API:** 10 запросов/сек (burst: 20)
- **Auth:** 5 запросов/сек (burst: 10)
- **Static:** 30 запросов/сек (burst: 50)

### Кеширование

Статические файлы Next.js кешируются агрессивно:

```nginx
location /_next/static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
}
```

### WebSocket поддержка

Настроена поддержка WebSocket для FastAPI:

```nginx
location /ws/ {
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
}
```

## Мониторинг и обслуживание

### Автоматическое обновление сертификатов

Скрипт `setup-ssl.sh` настраивает автоматическое обновление сертификатов через cron:

```bash
# Проверка cron задач
crontab -l

# Ручное обновление
sudo certbot renew --dry-run
```

### Проверка статуса

```bash
# Статус Nginx
sudo systemctl status nginx

# Проверка конфигурации
sudo nginx -t

# Проверка SSL сертификата
sudo openssl x509 -in /etc/letsencrypt/live/parser.mysite.ru/cert.pem -noout -dates

# Проверка портов
sudo netstat -tlnp | grep :443
```

### Логи

```bash
# Логи доступа
sudo tail -f /var/log/nginx/access.log

# Логи ошибок
sudo tail -f /var/log/nginx/error.log

# Логи SSL
sudo journalctl -u nginx -f
```

## Устранение неполадок

### Проблема: SSL сертификат не обновляется

```bash
# Проверка прав доступа
sudo ls -la /etc/letsencrypt/live/parser.mysite.ru/

# Ручное обновление
sudo certbot renew --force-renewal

# Проверка cron
sudo crontab -l
```

### Проблема: Nginx не запускается

```bash
# Проверка синтаксиса
sudo nginx -t

# Проверка конфликтов портов
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Проверка прав доступа к сертификатам
sudo nginx -T | grep ssl_certificate
```

### Проблема: Домен не резолвится

```bash
# Проверка DNS
nslookup parser.mysite.ru

# Проверка с разных DNS серверов
dig @8.8.8.8 parser.mysite.ru
dig @1.1.1.1 parser.mysite.ru
```

### Проблема: HTTPS недоступен

```bash
# Проверка SSL соединения
openssl s_client -connect parser.mysite.ru:443 -servername parser.mysite.ru

# Проверка заголовков
curl -I https://parser.mysite.ru

# Проверка сертификата
echo | openssl s_client -servername parser.mysite.ru -connect parser.mysite.ru:443 2>/dev/null | openssl x509 -noout -text
```

## Производительность

### Оптимизация

- **Worker processes:** Автоматическое определение
- **Worker connections:** 4096 на процесс
- **Keepalive:** 65 секунд
- **Gzip:** Уровень 6 с минимальным размером 1000 байт
- **Proxy buffering:** Оптимизированные буферы

### Мониторинг производительности

```bash
# Статус Nginx
sudo nginx -V

# Статистика соединений
ss -tuln | grep :443

# Использование памяти
ps aux | grep nginx
```

## Безопасность

### Рекомендации

1. **Регулярно обновляйте Nginx** до последней стабильной версии
2. **Мониторьте логи** на предмет подозрительной активности
3. **Настройте fail2ban** для защиты от брутфорс атак
4. **Используйте сильные пароли** для всех сервисов
5. **Регулярно проверяйте SSL сертификаты** на истечение

### Дополнительные меры безопасности

```bash
# Установка fail2ban
sudo apt-get install fail2ban

# Настройка UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Поддержка

При возникновении проблем:

1. Проверьте логи Nginx: `/var/log/nginx/error.log`
2. Запустите скрипт проверки: `./scripts/check-nginx-config.sh`
3. Проверьте статус сервисов: `systemctl status nginx`
4. Убедитесь в корректности DNS настроек

## Лицензия

Эта конфигурация предоставляется "как есть" без каких-либо гарантий.
