# 🔧 Устранение проблем деплоя

## Проблемы и решения

### 1. Сиротские контейнеры

**Проблема:** `Found orphan containers ([fullstack_arq_worker_prod])`

**Причина:** Контейнеры, созданные из старых версий docker-compose файлов, которые больше не соответствуют текущей конфигурации.

**Решение:**

```bash
# Автоматическая очистка
./scripts/cleanup-orphans.sh

# Ручная очистка
docker ps -a | grep fullstack
docker stop <container_name>
docker rm <container_name>

# Использование флага --remove-orphans
docker compose -f docker-compose.prod.ip.yml up -d --remove-orphans
```

### 2. Конфликт портов

**Проблема:** `failed to bind host port for 0.0.0.0:80: address already in use`

**Причина:** Системный nginx или другой процесс занимает порт 80.

**Решение:**

```bash
# Проверка занятых портов
sudo netstat -tlnp | grep :80

# Освобождение порта 80
sudo fuser -k 80/tcp
sudo fuser -k 443/tcp

# Ожидание освобождения порта
while sudo netstat -tlnp | grep -q ":80 "; do
    echo "Порт 80 всё ещё занят, ждём..."
    sleep 2
done
```

### 3. Проблемы с зависимостями сервисов

**Проблема:** Контейнеры не запускаются в правильном порядке.

**Решение:**

```yaml
# В docker-compose.yml используйте depends_on с условиями
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

### 4. Проблемы с переменными окружения

**Проблема:** Контейнеры не могут найти .env.prod файл.

**Решение:**

```bash
# Проверка наличия файла
ls -la .env.prod

# Переход в правильную директорию
cd /opt/app

# Проверка переменных
docker compose -f docker-compose.prod.ip.yml config
```

## Команды для диагностики

### Проверка статуса контейнеров

```bash
docker compose -f docker-compose.prod.ip.yml ps
docker compose -f docker-compose.prod.ip.yml logs <service_name>
```

### Проверка сетевых портов

```bash
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### Проверка здоровья приложения

```bash
curl -f -k https://localhost/health
curl -f -k https://localhost/api/v1/health/
```

### Очистка Docker

```bash
docker system prune -f
docker image prune -f
docker volume prune -f
```

## Профилактика проблем

### 1. Регулярная очистка

```bash
# Добавьте в cron
0 2 * * * /opt/app/scripts/cleanup-orphans.sh
```

### 2. Мониторинг портов

```bash
# Скрипт для проверки занятых портов
#!/bin/bash
for port in 80 443 8000 3000; do
    if sudo netstat -tlnp | grep -q ":$port "; then
        echo "Порт $port занят"
    else
        echo "Порт $port свободен"
    fi
done
```

### 3. Резервное копирование

```bash
# Перед деплоем всегда делайте бэкап
docker compose -f docker-compose.prod.ip.yml exec postgres pg_dump -U postgres vk_parser > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Логи и отладка

### Просмотр логов

```bash
# Все сервисы
docker compose -f docker-compose.prod.ip.yml logs

# Конкретный сервис
docker compose -f docker-compose.prod.ip.yml logs nginx --tail=50

# Следить за логами в реальном времени
docker compose -f docker-compose.prod.ip.yml logs -f
```

### Отладка контейнеров

```bash
# Войти в контейнер
docker compose -f docker-compose.prod.ip.yml exec backend bash

# Проверить переменные окружения
docker compose -f docker-compose.prod.ip.yml exec backend env

# Проверить сетевые подключения
docker compose -f docker-compose.prod.ip.yml exec backend netstat -tlnp
```

## Чек-лист перед деплоем

- [ ] Порт 80 свободен
- [ ] Файл .env.prod существует
- [ ] Сиротские контейнеры удалены
- [ ] Достаточно места на диске
- [ ] Docker демон запущен
- [ ] SSL сертификаты на месте
- [ ] Бэкап базы данных создан
