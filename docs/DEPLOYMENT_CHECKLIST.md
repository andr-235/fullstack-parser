# ✅ Чек-лист настройки деплоя

## 🔧 GitHub Secrets (обязательные)

### ✅ Уже настроены автоматически:

- `GITHUB_TOKEN` - автоматически предоставляется GitHub

### ⚠️ Нужно настроить вручную:

| Secret                | Статус | Описание                              | Значение                                  |
| --------------------- | ------ | ------------------------------------- | ----------------------------------------- |
| `PRODUCTION_APP_DIR`  | ❓     | Путь к папке с приложением на сервере | `/opt/app`                                |
| `HEALTH_CHECK_URL`    | ❓     | URL для проверки работоспособности    | `https://parser.mysite.ru/api/v1/health/` |
| `NEXT_PUBLIC_API_URL` | ❓     | URL API для frontend                  | `https://parser.mysite.ru`                |
| `SLACK_WEBHOOK`       | ❓     | Webhook для уведомлений в Slack       | `https://hooks.slack.com/...`             |

## 🖥️ Сервер (проверить)

### ✅ Docker и Docker Compose

```bash
# Проверка Docker
docker --version
docker compose --version

# Проверка прав
docker ps
```

### ✅ Структура папок

```bash
# Проверка папки приложения
ls -la /opt/app/

# Проверка docker-compose файла
ls -la /opt/app/docker-compose.prod.ip.yml
```

### ✅ Переменные окружения

```bash
# Проверка .env.prod
ls -la /opt/app/.env.prod
```

## 🔄 GitHub Actions Runner

### ✅ Runner настроен

```bash
# Проверка статуса runner
sudo systemctl status actions.runner.*
```

### ✅ Runner может выполнять команды

- ✅ Docker доступен
- ✅ SSH доступ к серверу
- ✅ Права на папку `/opt/app`

## 🚀 Тестовый деплой

### 1. Проверить secrets

Перейти в GitHub → Settings → Secrets and variables → Actions

### 2. Запустить тестовый деплой

1. Перейти в Actions → 🚀 Продвинутый CI/CD
2. Нажать "Run workflow"
3. Выбрать ветку `main`
4. Запустить

### 3. Проверить результат

```bash
# На сервере
docker ps
curl https://parser.mysite.ru/api/v1/health/
```

## 🛠️ Команды для проверки

### Проверка Docker контейнеров

```bash
# Статус контейнеров
docker ps -a

# Логи контейнеров
docker logs fullstack_prod_backend
docker logs fullstack_prod_frontend
docker logs fullstack_prod_nginx
```

### Проверка сети

```bash
# Проверка портов
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :8000
```

### Проверка логов

```bash
# Логи приложения
tail -f /opt/app/backend/logs/app.log
tail -f /opt/app/nginx/logs/access.log
tail -f /opt/app/nginx/logs/error.log
```

## 🚨 Возможные проблемы

### 1. Ошибка доступа к registry

```bash
# Проверить токен
echo $GITHUB_TOKEN
```

### 2. Ошибка подключения к серверу

```bash
# Проверить SSH
ssh localhost
```

### 3. Ошибка Docker

```bash
# Очистка Docker
docker system prune -a
docker volume prune
```

## 📊 Мониторинг

### Health Check endpoints

- Frontend: `https://parser.mysite.ru`
- Backend API: `https://parser.mysite.ru/api/v1/health/`
- Nginx: `https://parser.mysite.ru`

### Логи GitHub Actions

- Перейти в Actions → выбрать workflow → View logs

## 🎯 Следующие шаги

1. ✅ Настроить GitHub Secrets
2. ✅ Проверить сервер
3. ✅ Запустить тестовый деплой
4. ✅ Проверить работоспособность
5. ✅ Настроить мониторинг

---

**Готов к деплою! 🚀**
