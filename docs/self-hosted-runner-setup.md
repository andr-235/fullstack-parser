# Self-hosted Runner Setup для adm79

## Текущая конфигурация

- **Пользователь**: `adm79`
- **Проект**: `/home/adm79/fullstack-parser`
- **Runner**: Уже настроен на сервере
- **Backend**: Express.js на порту 3000

## Структура проекта

```bash
/home/adm79/
├── fullstack-parser/          # Основной проект
│   ├── backend/              # Express.js backend
│   ├── frontend/             # Vue.js frontend
│   ├── scripts/              # Deployment скрипты
│   ├── docker-compose.yml    # Docker конфигурация
│   ├── docker-compose.prod.yml
│   └── .env                  # Environment variables
├── backups/                  # Database backups
└── logs/                     # Deployment logs
```

## Workflow конфигурация

### 1. Staging деплой (автоматический)
- Запускается при push в `main`
- Использует `runs-on: [self-hosted, linux, x64]`
- Путь проекта: `/home/adm79/fullstack-parser`
- Проверяет Express.js на `http://localhost:3000`

### 2. Production деплой (ручной)
- Запускается через GitHub Actions UI
- Создает backup перед деплоем
- Использует production конфигурацию
- Comprehensive health checks

## Команды для управления

### Быстрый деплой
```bash
cd /home/adm79/fullstack-parser
./scripts/quick-deploy-adm79.sh deploy
```

### Проверка статуса
```bash
./scripts/quick-deploy-adm79.sh status
```

### Просмотр логов
```bash
./scripts/quick-deploy-adm79.sh logs
```

### Перезапуск сервисов
```bash
./scripts/quick-deploy-adm79.sh restart
```

### Создание backup
```bash
./scripts/quick-deploy-adm79.sh backup
```

## Health Check endpoints

- **Backend**: `http://localhost:3000`
- **API Health**: `http://localhost:3000/api/health` (если реализован)
- **Frontend**: `http://localhost` (если настроен nginx)

## Логи и мониторинг

### Deployment логи
```bash
tail -f /home/adm79/logs/deploy.log
tail -f /home/adm79/logs/quick-deploy.log
tail -f /home/adm79/logs/rollback.log
```

### Docker логи
```bash
cd /home/adm79/fullstack-parser
docker-compose logs -f api      # Express.js backend
docker-compose logs -f postgres # Database
docker-compose logs -f redis    # Cache
```

### Системные логи
```bash
journalctl -u actions.runner.* -f  # GitHub Actions runner
```

## Директории и файлы

### Создание необходимых директорий
```bash
mkdir -p /home/adm79/backups
mkdir -p /home/adm79/logs
chmod +x /home/adm79/fullstack-parser/scripts/*.sh
```

### Права доступа
```bash
# Проверка прав пользователя adm79
groups adm79

# Должен быть в группах: adm79, docker
# Если нет в docker группе:
sudo usermod -aG docker adm79
```

## Environment Variables

### .env файл для production
```bash
cd /home/adm79/fullstack-parser

# Создание .env из примера
cp env.example .env

# Редактирование production настроек
nano .env
```

### Основные переменные:
```env
# Database
POSTGRES_DB=vk_parser
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password

# Application
NODE_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# VK API
VK_ACCESS_TOKEN=your-vk-token

# Logging
LOG_LEVEL=info
```

## Troubleshooting

### 1. Runner не запускается
```bash
# Проверка статуса runner
cd /home/adm79/actions-runner
./run.sh

# Перезапуск runner
sudo systemctl restart actions.runner.*
```

### 2. Docker permission denied
```bash
# Добавить пользователя в группу docker
sudo usermod -aG docker adm79
newgrp docker

# Проверить права
docker ps
```

### 3. Проект не найден
```bash
# Проверить существование директории
ls -la /home/adm79/
cd /home/adm79/fullstack-parser
pwd
```

### 4. Express.js не отвечает
```bash
# Проверить процессы
docker-compose ps

# Проверить логи
docker-compose logs api

# Проверить порты
netstat -tlnp | grep 3000
```

### 5. Database проблемы
```bash
# Проверить PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# Подключиться к БД
docker-compose exec postgres psql -U postgres -d vk_parser
```

## Мониторинг ресурсов

### Использование диска
```bash
df -h /home/adm79/
du -sh /home/adm79/fullstack-parser/
```

### Docker ресурсы
```bash
docker system df
docker stats
```

### Очистка
```bash
# Очистка Docker
docker system prune -f
docker image prune -f

# Очистка старых backups (старше 7 дней)
find /home/adm79/backups -name "*.sql.gz" -mtime +7 -delete

# Очистка старых логов (старше 30 дней)
find /home/adm79/logs -name "*.log" -mtime +30 -delete
```

## Backup и восстановление

### Автоматические backups
- Создаются перед каждым деплоем
- Хранятся в `/home/adm79/backups/`
- Формат: `db_backup_YYYYMMDD_HHMMSS.sql.gz`

### Ручное создание backup
```bash
cd /home/adm79/fullstack-parser
./scripts/deploy-express.sh backup
```

### Восстановление из backup
```bash
# Просмотр доступных backup
./scripts/rollback.sh list-backups

# Восстановление конкретного backup
./scripts/rollback.sh database /home/adm79/backups/db_backup_20241225_120000.sql.gz
```

## Полезные команды

### Проверка всего окружения
```bash
echo "User: $(whoami)"
echo "Groups: $(groups)"
echo "Docker: $(docker --version)"
echo "Node.js: $(node --version)"
echo "NPM: $(npm --version)"
echo "Git: $(git --version)"
echo "Project exists: $(test -d /home/adm79/fullstack-parser && echo 'YES' || echo 'NO')"
echo "Runner status: $(systemctl is-active actions.runner.* 2>/dev/null || echo 'Not running')"
```

### Быстрая диагностика
```bash
cd /home/adm79/fullstack-parser
./scripts/quick-deploy-adm79.sh status
```

## Security заметки

- Runner запускается под пользователем `adm79`
- Нет прямого доступа к root
- Docker контейнеры изолированы
- Логи доступны только для пользователя `adm79`
- Backup файлы защищены правами доступа

## Контакты и поддержка

При проблемах с deployment:
1. Проверить логи: `tail -f /home/adm79/logs/*.log`
2. Проверить статус: `./scripts/quick-deploy-adm79.sh status`
3. Проверить GitHub Actions workflow в репозитории