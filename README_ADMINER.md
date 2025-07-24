# 🗄️ Adminer - Быстрый старт

## 🚀 Запуск

### Через Makefile (рекомендуется)

```bash
# Запуск Adminer
make adminer

# Или пошагово
make adminer-start

# Остановка
make adminer-stop
```

### Через Docker Compose

```bash
# Запуск с профилем admin
docker-compose -f docker-compose.prod.ip.yml --profile admin up adminer -d

# Остановка
docker-compose -f docker-compose.prod.ip.yml stop adminer
```

## 🌐 Доступ

**URL**: `http://YOUR_SERVER_IP:8080`

### Параметры подключения:

- **Система**: PostgreSQL
- **Сервер**: `postgres`
- **Пользователь**: `${DB_USER}` (из .env.prod)
- **Пароль**: `${DB_PASSWORD}` (из .env.prod)
- **База данных**: `${DB_NAME}` (из .env.prod)

## 📊 Возможности

- ✅ Просмотр таблиц и данных
- ✅ Выполнение SQL запросов
- ✅ Экспорт данных (CSV, SQL, JSON)
- ✅ Импорт данных
- ✅ Управление схемой БД
- ✅ Темная тема

## 🛡️ Безопасность

- Adminer запускается только с профилем `admin`
- Непривилегированный пользователь
- Ограничения ресурсов
- Read-only файловая система

## 📚 Подробная документация

См. [docs/ADMINER_USAGE.md](docs/ADMINER_USAGE.md) для полной документации.

---

**Удобного управления базой данных! 🗄️**
