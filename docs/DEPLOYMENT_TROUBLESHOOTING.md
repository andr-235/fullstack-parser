# Руководство по устранению неполадок при деплое

## Проблема: Таймаут при сборке Docker образов

### Симптомы
- Ошибка `Run Command Timeout` при сборке
- Зависание на этапе `pnpm install --frozen-lockfile`
- Процесс завершается с exit code 1

### Причины
1. **Медленное интернет-соединение** - загрузка npm пакетов занимает слишком много времени
2. **Недостаточно ресурсов** - сервер не справляется с нагрузкой при сборке
3. **Проблемы с кэшем** - повреждённый кэш pnpm или npm
4. **Таймауты в CI/CD** - ограничения по времени выполнения в системе сборки

### Решения

#### 1. Использование скрипта с retry логикой
```bash
# Деплой всех сервисов с автоматическими повторами
./scripts/deploy-with-retry.sh

# Деплой только frontend
./scripts/deploy-with-retry.sh frontend
```

#### 2. Альтернативный Dockerfile с npm
Если pnpm продолжает вызывать проблемы, используйте альтернативный Dockerfile:

```bash
# Временно переименуйте файлы
mv frontend/Dockerfile frontend/Dockerfile.pnpm
mv frontend/Dockerfile.npm frontend/Dockerfile

# Выполните деплой
docker-compose -f docker-compose.prod.ip.yml up -d --build frontend

# Верните обратно
mv frontend/Dockerfile frontend/Dockerfile.npm
mv frontend/Dockerfile.pnpm frontend/Dockerfile
```

#### 3. Ручная очистка и пересборка
```bash
# Остановить все контейнеры
docker-compose -f docker-compose.prod.ip.yml down

# Очистить все образы и кэш
docker system prune -a -f
docker builder prune -a -f

# Очистить кэш npm/pnpm локально
rm -rf frontend/node_modules
rm -rf frontend/.next
rm -rf ~/.npm
rm -rf ~/.pnpm-store

# Пересобрать с нуля
docker-compose -f docker-compose.prod.ip.yml up -d --build
```

#### 4. Увеличение ресурсов для Docker
```bash
# Проверить текущие лимиты
docker system df

# Увеличить доступную память для Docker (если возможно)
# В /etc/docker/daemon.json:
{
  "default-shm-size": "2G",
  "storage-driver": "overlay2"
}
```

#### 5. Использование локального registry
```bash
# Создать локальный registry для кэширования образов
docker run -d -p 5000:5000 --name registry registry:2

# Настроить docker-compose для использования локального registry
# В docker-compose.prod.ip.yml добавить:
# image: localhost:5000/fullstack-frontend:latest
```

### Профилактика

#### 1. Мониторинг ресурсов
```bash
# Мониторинг использования ресурсов во время сборки
docker stats

# Проверка свободного места
df -h
```

#### 2. Оптимизация Dockerfile
- Используйте многоэтапную сборку
- Копируйте только необходимые файлы
- Используйте .dockerignore для исключения ненужных файлов

#### 3. Настройка CI/CD
- Увеличьте таймауты в настройках CI/CD
- Используйте кэширование слоёв Docker
- Настройте параллельную сборку сервисов

### Логи и диагностика

#### Просмотр логов сборки
```bash
# Подробные логи сборки
docker-compose -f docker-compose.prod.ip.yml build --progress=plain frontend

# Логи запущенного контейнера
docker-compose -f docker-compose.prod.ip.yml logs -f frontend
```

#### Проверка здоровья сервисов
```bash
# Статус всех сервисов
docker-compose -f docker-compose.prod.ip.yml ps

# Проверка здоровья конкретного сервиса
docker inspect fullstack_frontend_prod | grep Health -A 10
```

### Экстренные меры

#### Быстрый деплой без пересборки
```bash
# Использовать готовые образы из registry
docker-compose -f docker-compose.prod.ip.yml pull
docker-compose -f docker-compose.prod.ip.yml up -d
```

#### Откат к предыдущей версии
```bash
# Откат к предыдущему образу
docker-compose -f docker-compose.prod.ip.yml down
docker tag fullstack_frontend_prod:previous fullstack_frontend_prod:latest
docker-compose -f docker-compose.prod.ip.yml up -d
```

### Контакты для поддержки
При возникновении проблем, которые не решаются данными методами:
1. Проверьте логи в `/var/log/docker/`
2. Соберите информацию о системе: `docker system info`
3. Обратитесь к команде разработки с полным описанием проблемы
