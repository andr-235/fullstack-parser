# 🚀 Настройка Production Сервера 192.168.88.12

Данное руководство поможет вам настроить fullstack приложение на production сервере по адресу **192.168.88.12**.

## 📋 Подготовка

### Системные требования
- **ОС**: Debian 12 или Ubuntu 20.04+
- **RAM**: Минимум 4GB, рекомендуется 8GB+
- **Диск**: Минимум 20GB свободного места
- **CPU**: 2 ядра (рекомендуется 4+)

### Сетевые требования
- Открытые порты: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Доступ к интернету для загрузки Docker образов
- SSH доступ к серверу

## 🔧 Пошаговая настройка

### Шаг 1: Подключение к серверу

```bash
# Подключитесь к серверу по SSH
ssh root@192.168.88.12

# Или если используете другого пользователя:
ssh username@192.168.88.12
```

### Шаг 2: Первичная настройка сервера

```bash
# Загрузите проект на сервер
git clone https://github.com/your-username/fullstack-parser.git /opt/app
cd /opt/app

# Запустите скрипт настройки сервера (требует root права)
sudo ./scripts/setup-server.sh 192.168.88.12 admin@192.168.88.12
```

Скрипт автоматически выполнит:
- ✅ Обновление системы
- ✅ Создание пользователя приложения
- ✅ Настройку UFW firewall
- ✅ Конфигурацию Fail2Ban
- ✅ Установку Docker и Docker Compose

### Шаг 3: Настройка переменных окружения

Создайте файл `.env.prod` с production конфигурацией:

```bash
# Создайте production env файл
cp env.example .env.prod
nano .env.prod
```

**Обязательно измените следующие параметры:**

```bash
# Environment
ENV=production

# Database
DB_NAME=vk_parser_prod
DB_USER=postgres
DB_PASSWORD=StrongPassword123!  # Замените на сильный пароль

# Security (ОБЯЗАТЕЛЬНО ПОМЕНЯЙТЕ!)
SECRET_KEY=your-super-strong-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Server configuration
SERVER_IP=192.168.88.12
CORS_ORIGINS=https://192.168.88.12,http://192.168.88.12

# Frontend URLs
NEXT_PUBLIC_API_URL=https://192.168.88.12/api
NEXT_PUBLIC_APP_URL=https://192.168.88.12
FRONTEND_URL=https://192.168.88.12

# VK API (настройте согласно вашему приложению)
VK_ACCESS_TOKEN=your-vk-access-token
VK_API_VERSION=5.131
VK_APP_ID=your-vk-app-id

# Logging
LOG_LEVEL=INFO
DEBUG=False
RELOAD=False
```

### Шаг 4: Создание SSL сертификатов

```bash
# Создайте self-signed SSL сертификаты для IP адреса
./scripts/create-ssl-certs.sh
```

Скрипт создаст:
- 📄 `nginx/ssl/cert.pem` - SSL сертификат
- 🔐 `nginx/ssl/key.pem` - Приватный ключ

### Шаг 5: Первый деплой

```bash
# Запустите первый деплой приложения
./scripts/deploy-ip.sh main

# Или с полной пересборкой образов:
./scripts/deploy-ip.sh main --force
```

Скрипт выполнит:
- 🏗️ Сборку Docker образов
- 🗄️ Настройку базы данных
- 🚀 Запуск всех сервисов
- ✅ Проверку работоспособности

## 🌐 Доступ к приложению

После успешного деплоя приложение будет доступно по адресам:

- **Основное приложение**: https://192.168.88.12
- **API документация**: https://192.168.88.12/api/docs
- **Health check**: https://192.168.88.12/health

⚠️ **Предупреждение**: Браузер покажет предупреждение о безопасности из-за self-signed сертификата. Нажмите "Продолжить" или добавьте сертификат в доверенные.

### Доступ к фронтенду через nginx по IP

После успешного деплоя фронтенд приложения (Next.js) доступен через nginx по IP-адресу сервера.

- **В браузере:**
  - Откройте:
    `https://192.168.88.12/`
  - При self-signed сертификате подтвердите исключение безопасности.

- **Через curl:**
  - Для теста (игнорируя self-signed сертификат):
    ```bash
    curl -k https://192.168.88.12/
    ```

- **Проксирование:**
  - Все запросы на `/` (кроме `/api/`, `/ws/`, `/health`) идут на фронтенд (Next.js).
  - API: `https://192.168.88.12/api/`
  - WebSocket: `https://192.168.88.12/ws/`

- **Healthcheck фронта:**
  - Проверить доступность фронта:
    ```bash
    curl -k https://192.168.88.12/
    ```

- **Внутренняя сеть:**
  - Если вы в одной сети с сервером — используйте IP напрямую.
  - Если снаружи — настройте проброс портов/файрволл.

- **Ошибки:**
  - Если фронт не открывается — проверьте логи nginx и контейнера frontend.

> **Важно:**
> Всё, что идёт на `https://192.168.88.12/` — это фронтенд, а всё, что на `https://192.168.88.12/api/` — backend.

## 🔍 Мониторинг и логи

### Проверка статуса сервисов

```bash
# Статус всех контейнеров
docker-compose -f docker-compose.prod.ip.yml ps

# Логи конкретного сервиса
docker-compose -f docker-compose.prod.ip.yml logs backend
docker-compose -f docker-compose.prod.ip.yml logs frontend
docker-compose -f docker-compose.prod.ip.yml logs nginx

# Логи в реальном времени
docker-compose -f docker-compose.prod.ip.yml logs -f
```

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Использование дискового пространства
df -h
docker system df
```

## 📦 Обновление приложения

### Обычное обновление

```bash
cd /opt/app
git pull origin main
./scripts/deploy-ip.sh main
```

### Обновление с полной пересборкой

```bash
cd /opt/app
git pull origin main
./scripts/deploy-ip.sh main --force
```

## 🛠️ Устранение неполадок

### Проблемы с SSL

```bash
# Пересоздать SSL сертификаты
./scripts/create-ssl-certs.sh

# Перезапустить nginx
docker-compose -f docker-compose.prod.ip.yml restart nginx
```

### Проблемы с базой данных

```bash
# Просмотр логов PostgreSQL
docker-compose -f docker-compose.prod.ip.yml logs postgres

# Подключение к базе данных
docker-compose -f docker-compose.prod.ip.yml exec postgres psql -U postgres -d vk_parser_prod
```

### Проблемы с сетью

```bash
# Проверка Docker сетей
docker network ls
docker network inspect fullstack-parser_app-network

# Перезапуск всех сервисов
docker-compose -f docker-compose.prod.ip.yml down
docker-compose -f docker-compose.prod.ip.yml up -d
```

### Очистка ресурсов

```bash
# Удаление неиспользуемых образов и контейнеров
docker system prune -af

# Удаление неиспользуемых volumes (ОСТОРОЖНО!)
docker volume prune
```

## 💾 Резервное копирование

### Создание бэкапа

```bash
# Ручное создание бэкапа
docker-compose -f docker-compose.prod.ip.yml run --rm backup

# Проверка бэкапов
ls -la backup/
```

### Восстановление из бэкапа

```bash
# Остановить приложение
docker-compose -f docker-compose.prod.ip.yml down

# Восстановить из бэкапа
gunzip -c backup/backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose -f docker-compose.prod.ip.yml run --rm -T postgres \
  psql -U postgres -d vk_parser_prod

# Запустить приложение
docker-compose -f docker-compose.prod.ip.yml up -d
```

## 🔒 Безопасность

### Рекомендации по безопасности

1. **Регулярно обновляйте систему**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Мониторьте логи безопасности**:
   ```bash
   sudo tail -f /var/log/auth.log
   sudo fail2ban-client status
   ```

3. **Проверяйте открытые порты**:
   ```bash
   sudo ufw status
   sudo netstat -tlnp
   ```

4. **Регулярно меняйте пароли** и секретные ключи

### Настройка автоматических обновлений

```bash
# Включить автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

## 📊 Производительность

### Оптимизация для production

1. **Мониторинг ресурсов**:
   ```bash
   # Установка htop для мониторинга
   sudo apt install htop
   htop
   ```

2. **Настройка логротации**:
   ```bash
   # Создание конфигурации logrotate
   sudo tee /etc/logrotate.d/docker-compose << EOF
   /opt/app/nginx/logs/*.log {
       daily
       missingok
       rotate 14
       compress
       notifempty
       create 0644 root root
   }
   EOF
   ```

3. **Настройка автозапуска**:
   ```bash
   # Создание systemd сервиса
   sudo tee /etc/systemd/system/fullstack-app.service << EOF
   [Unit]
   Description=Fullstack Application
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/opt/app
   ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.ip.yml up -d
   ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.ip.yml down
   TimeoutStartSec=0

   [Install]
   WantedBy=multi-user.target
   EOF

   sudo systemctl enable fullstack-app.service
   ```

## 🆘 Техническая поддержка

При возникновении проблем:

1. **Проверьте логи**: `docker-compose -f docker-compose.prod.ip.yml logs`
2. **Проверьте статус сервисов**: `docker-compose -f docker-compose.prod.ip.yml ps`
3. **Проверьте ресурсы системы**: `htop`, `df -h`
4. **Проверьте сетевое соединение**: `curl -k https://192.168.88.12/health`

---

## ✅ Чек-лист успешного деплоя

- [ ] Сервер обновлен и настроен
- [ ] Docker и Docker Compose установлены
- [ ] Файл `.env.prod` создан и настроен
- [ ] SSL сертификаты созданы
- [ ] Приложение успешно развернуто
- [ ] Все сервисы запущены и работают
- [ ] Приложение доступно по https://192.168.88.12
- [ ] API документация доступна
- [ ] Настроен мониторинг и логирование
- [ ] Настроено резервное копирование

🎉 **Поздравляем! Ваше приложение успешно развернуто в production!**
