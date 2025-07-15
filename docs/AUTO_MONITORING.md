# Система автоматического мониторинга групп ВК

## Обзор

Система автоматического мониторинга позволяет непрерывно отслеживать все активные группы ВК на предмет новых комментариев с ключевыми словами. Вместо ручного запуска парсинга для каждой группы, система автоматически:

- Запускает мониторинг по расписанию
- Обрабатывает группы в порядке приоритета
- Сохраняет статистику мониторинга
- Уведомляет об ошибках

## Архитектура

### Компоненты

1. **MonitoringService** - основной сервис мониторинга
2. **SchedulerService** - планировщик задач
3. **Arq Tasks** - фоновые задачи для парсинга
4. **API Endpoints** - управление мониторингом

### Поток данных

```
SchedulerService → Arq Queue → run_monitoring_cycle → MonitoringService → ParserService
```

## Конфигурация

### Переменные окружения

```bash
# Интервал запуска планировщика (секунды)
MONITORING_SCHEDULER_INTERVAL_SECONDS=300

# Максимум одновременных групп
MONITORING_MAX_CONCURRENT_GROUPS=10

# Задержка между группами (секунды)
MONITORING_GROUP_DELAY_SECONDS=1

# Автозапуск планировщика
MONITORING_AUTO_START_SCHEDULER=false
```

### Настройки группы

Каждая группа может иметь индивидуальные настройки мониторинга:

- `auto_monitoring_enabled` - включен ли мониторинг
- `monitoring_interval_minutes` - интервал мониторинга (1-1440 минут)
- `monitoring_priority` - приоритет (1-10, где 10 - высший)
- `next_monitoring_at` - время следующего мониторинга

## API Endpoints

### Статистика мониторинга

```http
GET /api/v1/monitoring/stats
```

Ответ:

```json
{
  "total_groups": 100,
  "active_groups": 80,
  "monitored_groups": 25,
  "ready_for_monitoring": 5,
  "next_monitoring_at": "2025-01-15T10:30:00Z"
}
```

### Статус планировщика

```http
GET /api/v1/monitoring/scheduler/status
```

Ответ:

```json
{
  "is_running": true,
  "monitoring_interval_seconds": 300,
  "redis_connected": true,
  "last_check": "2025-01-15T10:25:00Z"
}
```

### Управление планировщиком

```http
POST /api/v1/monitoring/scheduler/start?interval_seconds=300
POST /api/v1/monitoring/scheduler/stop
POST /api/v1/monitoring/run-cycle
```

### Управление мониторингом группы

```http
POST /api/v1/monitoring/groups/{group_id}/enable
Content-Type: application/json

{
  "interval_minutes": 60,
  "priority": 5
}
```

```http
POST /api/v1/monitoring/groups/{group_id}/disable
GET /api/v1/monitoring/groups/{group_id}/status
```

## Использование

### 1. Включение мониторинга для группы

```python
import requests

# Включить мониторинг группы с интервалом 30 минут и приоритетом 8
response = requests.post(
    "http://localhost:8000/api/v1/monitoring/groups/1/enable",
    json={
        "interval_minutes": 30,
        "priority": 8
    }
)
```

### 2. Запуск планировщика

```python
# Запустить планировщик с интервалом 5 минут
response = requests.post(
    "http://localhost:8000/api/v1/monitoring/scheduler/start",
    params={"interval_seconds": 300}
)
```

### 3. Ручной запуск цикла мониторинга

```python
# Запустить цикл мониторинга вручную
response = requests.post("http://localhost:8000/api/v1/monitoring/run-cycle")
```

## Мониторинг и логирование

### Логи

Система ведет подробные логи всех операций:

```
[INFO] Запуск цикла автоматического мониторинга
[INFO] Найдено групп для мониторинга count=5
[INFO] Запуск мониторинга группы group_id=1 group_name="РИА Новости"
[INFO] Мониторинг группы успешно запущен group_id=1 task_id=monitor_1_1705312500
[INFO] Цикл мониторинга завершён total_groups=5 successful_runs=5 failed_runs=0
```

### Метрики

Система собирает следующие метрики:

- Количество групп в мониторинге
- Время выполнения циклов
- Успешные/неудачные запуски
- Ошибки мониторинга

## Оптимизация производительности

### Ограничения

1. **Задержка между группами** - предотвращает перегрузку VK API
2. **Максимум одновременных групп** - ограничивает нагрузку на систему
3. **Приоритизация** - важные группы обрабатываются первыми

### Масштабирование

Система поддерживает масштабирование:

- Множественные Arq workers
- Распределенное хранение в Redis
- Асинхронная обработка

## Безопасность

### Ограничения доступа

- API endpoints требуют аутентификации
- Валидация параметров конфигурации
- Логирование всех операций

### Обработка ошибок

- Graceful degradation при ошибках VK API
- Повторные попытки для временных сбоев
- Сохранение ошибок в базе данных

## Развертывание

### Docker Compose

```yaml
services:
  arq-worker:
    build: ./backend
    command: arq app.workers.arq_worker.WorkerSettings
    environment:
      - MONITORING_AUTO_START_SCHEDULER=true
      - MONITORING_SCHEDULER_INTERVAL_SECONDS=300
```

### Отдельный планировщик

```bash
# Запуск планировщика как отдельный процесс
python -m app.workers.monitoring_scheduler
```

## Troubleshooting

### Частые проблемы

1. **Планировщик не запускается**

   - Проверьте подключение к Redis
   - Убедитесь, что Arq worker запущен

2. **Группы не мониторятся**

   - Проверьте `auto_monitoring_enabled` для групп
   - Убедитесь, что группы активны

3. **Ошибки VK API**
   - Проверьте токен доступа
   - Убедитесь в лимитах API

### Диагностика

```bash
# Проверить статус планировщика
curl http://localhost:8000/api/v1/monitoring/scheduler/status

# Посмотреть статистику
curl http://localhost:8000/api/v1/monitoring/stats

# Проверить логи
docker logs backend-app
```
