# 🔍 Мониторинг и Диагностика Fullstack Приложения

## Обзор

Этот документ описывает систему мониторинга и диагностики для fullstack приложения, включая фронтенд, бэкенд, базу данных и вспомогательные сервисы.

## 🚨 Быстрая Диагностика

### Проверка статуса всех контейнеров

```bash
./scripts/monitor.sh
```

### Проверка логов конкретного контейнера

```bash
# Фронтенд
docker logs fullstack_prod_frontend --tail 100

# Бэкенд
docker logs fullstack_prod_backend --tail 100

# ARQ Worker
docker logs fullstack_prod_arq_worker --tail 100

# Nginx
docker exec fullstack_prod_nginx tail -50 /var/log/nginx/error.log
```

### Проверка ресурсов

```bash
docker stats --no-stream
```

## 📊 Health Checks

### Endpoints

- **Nginx**: `http://localhost/health`
- **Frontend**: `https://localhost/health/frontend`
- **Backend**: `https://localhost/health/backend`

### Проверка через curl

```bash
# Nginx
curl -f http://localhost/health

# Frontend (с игнорированием SSL)
curl -f -k https://localhost/health/frontend

# Backend (с игнорированием SSL)
curl -f -k https://localhost/health/backend
```

## 🔧 Частые Проблемы и Решения

### 1. ARQ Worker использует 100% CPU

**Симптомы:**

- Высокое потребление CPU worker'ом
- Медленная работа приложения
- Возможные таймауты

**Решение:**

```bash
# Перезапуск с новыми ограничениями ресурсов
docker-compose -f docker-compose.prod.ip.yml up -d arq_worker

# Проверка ограничений
docker stats fullstack_prod_arq_worker
```

**Профилактика:**

- Установлены лимиты CPU и памяти в docker-compose
- Настроены переменные окружения ARQ для оптимизации

### 2. Фронтенд недоступен

**Симптомы:**

- 502/503 ошибки
- Пустые страницы
- Health check не проходит

**Диагностика:**

```bash
# Проверка статуса контейнера
docker ps | grep frontend

# Проверка логов
docker logs fullstack_prod_frontend

# Проверка сетевого взаимодействия
docker exec fullstack_prod_frontend curl -f http://backend:8000/api/v1/health/
```

**Решение:**

```bash
# Перезапуск фронтенда
docker-compose -f docker-compose.prod.ip.yml restart frontend

# Пересборка при необходимости
docker-compose -f docker-compose.prod.ip.yml up -d --build frontend
```

### 3. Проблемы с Nginx

**Симптомы:**

- Предупреждения о deprecated директивах
- Ошибки проксирования
- SSL проблемы

**Решение:**

```bash
# Перезапуск nginx
docker-compose -f docker-compose.prod.ip.yml restart nginx

# Проверка конфигурации
docker exec fullstack_prod_nginx nginx -t
```

### 4. Проблемы с базой данных

**Симптомы:**

- Ошибки подключения
- Медленные запросы
- Health check не проходит

**Диагностика:**

```bash
# Проверка статуса PostgreSQL
docker exec fullstack_prod_postgres pg_isready -U postgres

# Проверка логов
docker logs fullstack_prod_postgres --tail 50
```

## 📈 Мониторинг Производительности

### Ключевые метрики

1. **CPU Usage**

   - Фронтенд: < 10%
   - Бэкенд: < 30%
   - ARQ Worker: < 50%
   - База данных: < 20%

2. **Memory Usage**

   - Фронтенд: < 100MB
   - Бэкенд: < 500MB
   - ARQ Worker: < 512MB
   - База данных: < 200MB

3. **Restart Count**
   - Все контейнеры должны иметь 0 перезапусков

### Автоматический мониторинг

Скрипт `./scripts/monitor.sh` проверяет:

- Статус всех контейнеров
- Health checks
- Использование ресурсов
- Количество перезапусков
- Дисковое пространство
- Ошибки в логах

## 🛠️ Утилиты для Диагностики

### Мониторинг в реальном времени

```bash
# Просмотр логов всех контейнеров
docker-compose -f docker-compose.prod.ip.yml logs -f

# Мониторинг ресурсов
watch -n 5 'docker stats --no-stream'
```

### Анализ логов

```bash
# Поиск ошибок в логах фронтенда
docker logs fullstack_prod_frontend 2>&1 | grep -i error

# Поиск ошибок в логах nginx
docker exec fullstack_prod_nginx grep -i error /var/log/nginx/error.log
```

## 🔄 Процедуры Восстановления

### Полный перезапуск системы

```bash
# Остановка всех сервисов
docker-compose -f docker-compose.prod.ip.yml down

# Очистка неиспользуемых ресурсов
docker system prune -f

# Запуск с пересборкой
docker-compose -f docker-compose.prod.ip.yml up -d --build
```

### Восстановление после сбоя

```bash
# Проверка состояния
./scripts/monitor.sh

# Перезапуск проблемного сервиса
docker-compose -f docker-compose.prod.ip.yml restart <service_name>

# Проверка после восстановления
./scripts/monitor.sh
```

## 📝 Логирование

### Логи приложения

- **Фронтенд**: `docker logs fullstack_prod_frontend`
- **Бэкенд**: `docker logs fullstack_prod_backend`
- **ARQ Worker**: `docker logs fullstack_prod_arq_worker`

### Логи веб-сервера

- **Access logs**: `docker exec fullstack_prod_nginx tail -f /var/log/nginx/access.log`
- **Error logs**: `docker exec fullstack_prod_nginx tail -f /var/log/nginx/error.log`

### Логи мониторинга

- **Monitor logs**: `/opt/app/logs/monitor.log`

## 🚀 Рекомендации по Оптимизации

1. **Регулярный мониторинг**

   - Запускайте `./scripts/monitor.sh` каждые 15 минут
   - Настройте cron job для автоматического мониторинга

2. **Логирование**

   - Регулярно проверяйте логи на наличие ошибок
   - Настройте ротацию логов для экономии места

3. **Резервное копирование**

   - Регулярно создавайте бэкапы базы данных
   - Сохраняйте конфигурационные файлы

4. **Обновления**
   - Регулярно обновляйте образы контейнеров
   - Тестируйте обновления в dev-окружении

## 📞 Контакты для Поддержки

При возникновении критических проблем:

1. Запустите полную диагностику: `./scripts/monitor.sh`
2. Соберите логи всех сервисов
3. Обратитесь к команде разработки с полной информацией о проблеме
