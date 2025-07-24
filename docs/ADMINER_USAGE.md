# 🗄️ Adminer - Управление базой данных

## 📋 Описание

Adminer - это легкий веб-интерфейс для управления базами данных. Добавлен в production конфигурацию для удобного просмотра и управления PostgreSQL базой данных.

## 🚀 Запуск Adminer

### Включение Adminer

```bash
# Запуск всех сервисов + Adminer
docker-compose -f docker-compose.prod.ip.yml --profile admin up -d

# Или только Adminer (если остальные сервисы уже запущены)
docker-compose -f docker-compose.prod.ip.yml --profile admin up adminer -d
```

### Остановка Adminer

```bash
# Остановка только Adminer
docker-compose -f docker-compose.prod.ip.yml stop adminer

# Остановка всех сервисов
docker-compose -f docker-compose.prod.ip.yml down
```

## 🌐 Доступ к Adminer

### URL

```
http://YOUR_SERVER_IP:8080
```

### Параметры подключения

- **Система**: PostgreSQL
- **Сервер**: `postgres` (автоматически заполнено)
- **Пользователь**: `${DB_USER}` (из .env.prod)
- **Пароль**: `${DB_PASSWORD}` (из .env.prod)
- **База данных**: `${DB_NAME}` (из .env.prod)

## 🔧 Настройки Adminer

### Переменные окружения

```yaml
environment:
  - ADMINER_DEFAULT_SERVER=postgres # Автоматическое подключение к PostgreSQL
  - ADMINER_DESIGN=pepa-linha-dark # Темная тема
  - ADMINER_PLUGINS=login-servers # Плагин для сохранения серверов
```

### Безопасность

- **Порт**: 8080 (можно изменить при необходимости)
- **Непривилегированный пользователь**: 1000:1000
- **Read-only файловая система**
- **Ограничения ресурсов**: 0.25 CPU, 128MB RAM

## 📊 Возможности Adminer

### Основные функции

- ✅ **Просмотр таблиц** - Структура и данные
- ✅ **SQL запросы** - Выполнение произвольных запросов
- ✅ **Экспорт данных** - CSV, SQL, JSON форматы
- ✅ **Импорт данных** - Загрузка файлов
- ✅ **Управление схемой** - Создание/изменение таблиц
- ✅ **Пользователи** - Управление правами доступа

### Дополнительные возможности

- 🔍 **Поиск** - Поиск по таблицам и данным
- 📈 **Статистика** - Информация о базе данных
- 🔧 **Настройки** - Конфигурация интерфейса
- 🌙 **Темная тема** - Удобный интерфейс

## 🛡️ Безопасность

### Рекомендации

1. **Ограничьте доступ** - Используйте firewall для порта 8080
2. **Сильные пароли** - Убедитесь в надежности паролей БД
3. **Регулярные обновления** - Обновляйте Adminer до последней версии
4. **Логирование** - Мониторьте доступы к Adminer

### Настройка firewall (опционально)

```bash
# Разрешить доступ только с определенных IP
sudo ufw allow from YOUR_IP to any port 8080

# Или полностью закрыть порт (использовать только через VPN)
sudo ufw deny 8080
```

## 🔍 Мониторинг

### Проверка статуса

```bash
# Статус Adminer
docker-compose -f docker-compose.prod.ip.yml ps adminer

# Логи Adminer
docker-compose -f docker-compose.prod.ip.yml logs adminer

# Health check
docker-compose -f docker-compose.prod.ip.yml exec adminer wget -q --spider http://localhost:8080
```

### Health Check

```yaml
healthcheck:
  test:
    ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8080"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 📝 Примеры использования

### Просмотр таблиц

1. Откройте Adminer в браузере
2. Войдите с учетными данными БД
3. Выберите базу данных
4. Просматривайте таблицы в левой панели

### Выполнение SQL запросов

1. Нажмите "SQL" в верхнем меню
2. Введите SQL запрос
3. Нажмите "Execute" для выполнения

### Экспорт данных

1. Выберите таблицу
2. Нажмите "Export" в верхнем меню
3. Выберите формат (CSV, SQL, JSON)
4. Скачайте файл

## 🚨 Важные замечания

### Профиль admin

- Adminer запускается только с профилем `admin`
- Это позволяет контролировать, когда Adminer доступен
- В обычном режиме Adminer не запускается

### Производительность

- Adminer использует минимальные ресурсы
- Не влияет на производительность основного приложения
- Можно остановить при необходимости

### Резервное копирование

- Adminer не влияет на backup процессы
- Все backup скрипты работают независимо
- Рекомендуется использовать Adminer только для просмотра

## 🔧 Troubleshooting

### Проблемы подключения

```bash
# Проверка сети
docker-compose -f docker-compose.prod.ip.yml exec adminer ping postgres

# Проверка портов
docker-compose -f docker-compose.prod.ip.yml exec adminer netstat -tlnp

# Проверка логов
docker-compose -f docker-compose.prod.ip.yml logs adminer
```

### Проблемы с правами доступа

```bash
# Проверка пользователя
docker-compose -f docker-compose.prod.ip.yml exec adminer id

# Проверка прав на файлы
docker-compose -f docker-compose.prod.ip.yml exec adminer ls -la /var/www/html
```

## 📚 Полезные ссылки

- [Adminer Documentation](https://www.adminer.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Profiles](https://docs.docker.com/compose/profiles/)

---

**Удобного управления базой данных! 🗄️**
