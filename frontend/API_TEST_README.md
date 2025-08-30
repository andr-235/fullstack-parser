# 🧪 API Тестирование

## Проблема

Были ошибки 404 при запросах к API:

```
GET http://localhost/api/v1//api/v1/stats/global 404 (Not Found)
GET http://localhost/api/v1/groups?active_only=true 404 (Not Found)
```

**Причина:** Дублирование `/api/v1/` в URL из-за неправильной environment переменной `NEXT_PUBLIC_API_URL=http://localhost/api/v1/`

## Решение

1. **Исправлена .env.local** - убрана `NEXT_PUBLIC_API_URL` для использования относительных URL в Docker
2. **Отключено проксирование в Next.js** - все запросы проходят через Nginx reverse proxy
3. **Обновлена nginx конфигурация** - проксирование `/api/v1/*` → `http://backend:8000/api/v1/*`
4. **Унифицированы запросы** - все хуки используют apiClient с относительными URL
5. **Добавлены заглушки** - для нереализованных endpoints (комментарии)
6. **Создан аватар администратора** - добавлен `admin.svg` вместо отсутствующего `admin.jpg`

## Как проверить

### 1. Запустить тестовый скрипт

```bash
cd /opt/app/frontend
node test-api.js
```

### 2. Проверить работу в браузере

Откройте http://localhost и проверьте консоль - ошибок 404 быть не должно.

### 3. Ручная проверка API

```bash
# Health check
curl http://localhost/api/v1/health/

# Получение групп
curl http://localhost/api/v1/groups

# Получение ключевых слов
curl http://localhost/api/v1/keywords

# Комментарии
curl http://localhost/api/v1/comments?size=1

# Статистика
curl http://localhost/api/v1/stats/global
curl http://localhost/api/v1/stats/dashboard
```

## Результаты тестирования

✅ **Health check: OK**
✅ **Группы получены: 1993 элементов**
✅ **Ключевые слова получены: 0 элементов**
✅ **Глобальная статистика: OK**
✅ **Статистика дашборда: OK**
⚠️ **Получение комментариев: STUB** (endpoint не реализован на backend)

## Архитектура (Docker)

- **Nginx** (контейнер) проксирует `/api/v1/*` → `http://backend:8000/api/v1/*`
- **Frontend** (Next.js контейнер) делает относительные запросы к `/api/v1/*`
- **Backend** (FastAPI контейнер) обрабатывает запросы на порту 8000
- **apiClient** использует baseURL = '' для относительных URL
- **Next.js** работает только как frontend без серверной части

## Перезапуск после изменений

Если изменили `.env.local` или конфигурацию, нужно перезапустить Docker контейнеры:

```bash
# Перезапуск frontend контейнера
docker-compose restart frontend

# Или полный перезапуск всех сервисов
docker-compose down && docker-compose up -d
```

## Если все еще есть ошибки

1. Убедитесь, что запущены все сервисы:
   ```bash
   docker-compose ps
   ```
2. Проверьте логи:
   ```bash
   docker-compose logs nginx
   docker-compose logs backend
   docker-compose logs frontend
   ```
3. Проверьте конфигурацию Nginx:
   ```bash
   docker-compose exec nginx nginx -T
   ```
