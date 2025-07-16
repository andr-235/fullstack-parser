# 🔧 Устранение проблем с деплоем

## Проблема: "Error denied" при загрузке Docker образов

### Описание проблемы
При деплое на продакшн возникает ошибка:
```
backend Error denied
arq-worker Interrupted
Error response from daemon: denied
```

### Причина
Ошибка возникает из-за отсутствия аутентификации в GitHub Container Registry (GHCR) на продакшн сервере. Образы `ghcr.io/andr-235/fullstack-backend:latest` и `ghcr.io/andr-235/fullstack-arq-worker:latest` являются приватными и требуют авторизации.

### Решение

#### 1. Автоматическое решение (CI/CD)
В GitHub Actions workflow `.github/workflows/deploy-production.yml` добавлен автоматический логин в GHCR:

```yaml
- name: 🚀 Deploy to Production
  uses: appleboy/ssh-action@v1
  with:
    script: |
      echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ secrets.GHCR_USERNAME }} --password-stdin
      docker-compose -f docker-compose.prod.ip.yml pull
      docker-compose -f docker-compose.prod.ip.yml up -d --build
```

#### 2. Ручное решение
Если нужно выполнить деплой вручную:

1. **Экспортируйте переменные окружения:**
   ```bash
   export GHCR_USERNAME=your-github-username
   export GHCR_TOKEN=your-github-personal-access-token
   ```

2. **Используйте скрипт деплоя:**
   ```bash
   ./scripts/deploy-production.sh
   ```

3. **Или выполните команды вручную:**
   ```bash
   # Логин в GHCR
   echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin

   # Загрузка образов
   docker-compose -f docker-compose.prod.ip.yml pull

   # Запуск сервисов
   docker-compose -f docker-compose.prod.ip.yml up -d --build
   ```

### Настройка GitHub Secrets

Для автоматического деплоя необходимо настроить следующие secrets в GitHub:

1. **GHCR_USERNAME** - ваш GitHub username
2. **GHCR_TOKEN** - GitHub Personal Access Token с правами `read:packages`

#### Создание Personal Access Token:
1. Перейдите в GitHub Settings → Developer settings → Personal access tokens
2. Создайте новый token с правами `read:packages`
3. Добавьте token в GitHub Secrets как `GHCR_TOKEN`

### Проверка статуса

После деплоя проверьте статус сервисов:

```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.ip.yml ps

# Детальная информация
docker-compose -f docker-compose.prod.ip.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Логи сервисов
docker-compose -f docker-compose.prod.ip.yml logs backend
docker-compose -f docker-compose.prod.ip.yml logs arq-worker
```

### Дополнительные исправления

#### Удаление устаревшего атрибута version
В `docker-compose.prod.ip.yml` удален устаревший атрибут `version` для избежания предупреждений.

#### Улучшенное логирование
Добавлены информативные сообщения в процессе деплоя для лучшей диагностики.

### Профилактика

1. **Регулярно проверяйте токены** - GitHub Personal Access Tokens имеют срок действия
2. **Мониторинг логов** - настройте алерты на ошибки деплоя
3. **Тестирование** - используйте staging окружение для тестирования деплоя
4. **Backup стратегия** - всегда имейте план отката на предыдущую версию
