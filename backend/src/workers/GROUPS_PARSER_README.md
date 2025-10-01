# GroupsParseWorker - Документация

## Обзор

**GroupsParseWorker** - специализированный BullMQ worker для обработки задач парсинга групп VK через VK-IO API.

## Основные возможности

✅ **Универсальная обработка идентификаторов**
- Поддержка VK ID (числовые: `12345678`)
- Поддержка screen_name (строковые: `"apiclub"`)
- Смешанные массивы (`[12345, "apiclub", 67890]`)
- VK-IO автоматически определяет тип

✅ **Батч-обработка**
- Оптимизация VK API запросов (100 ID за запрос)
- Безопасные задержки между батчами (400ms)
- Сохранение в БД батчами (50 групп)

✅ **Детальный Progress Tracking**
- Процент выполнения (0-100%)
- Этапы: `init` → `fetching` → `saving` → `done`
- Детальная статистика: `total`, `processed`, `valid`, `invalid`, `duplicate`
- Синхронизация с Task Service

✅ **Graceful Error Handling**
- Продолжение работы при ошибках отдельных групп
- Сбор всех ошибок в массив
- Job успешен если хотя бы 1 группа сохранена
- Критические ошибки прерывают job

✅ **Проверка дубликатов**
- Автоматическая проверка через `groupsRepo.groupExistsByVkId()`
- Подсчет дубликатов в статистике
- Дубликаты не сохраняются повторно

## Архитектура

### Входные данные (Job Data)

```typescript
{
  taskId: number,
  type: 'process_groups',
  metadata: {
    groupIdentifiers: string[],  // ["12345", "apiclub", "67890"]
    source: 'file' | 'manual',
    originalFileName?: string
  }
}
```

### Выходные данные (Job Result)

```typescript
{
  success: boolean,
  taskId: number,
  stats: {
    total: 150,      // Всего идентификаторов
    valid: 140,      // Найдено валидных групп
    invalid: 5,      // Недоступные/несуществующие
    duplicate: 5,    // Уже есть в БД
    saved: 140       // Успешно сохранено
  },
  errors: [
    {
      identifier: "12345",
      error: "Group not found or inaccessible",
      timestamp: Date
    }
  ],
  processingTimeMs: 45230
}
```

### Progress Data

```typescript
{
  percentage: 45,  // 0-100%
  stage: 'fetching',
  currentBatch: 2,
  totalBatches: 5,
  stats: {
    total: 150,
    processed: 75,
    valid: 70,
    invalid: 3,
    duplicate: 2
  }
}
```

## Workflow

### Этап 1: Инициализация (0%)
1. Получение job data с массивом идентификаторов
2. Валидация входных данных
3. Обновление статуса задачи: `processing`
4. Инициализация счетчиков статистики

### Этап 2: Получение информации через VK-IO (0-70%)
1. **Разбивка на батчи по 100 ID**
2. **Для каждого батча:**
   ```typescript
   const groupsInfo = await vkIoService.getGroupsInfo(batchIdentifiers)
   ```
   - VK-IO автоматически обрабатывает VK ID и screen_name
   - Возвращает полную информацию: `id`, `name`, `screen_name`, `photo_50`, `members_count`, `is_closed`, `description`
3. **Проверка дубликатов:**
   ```typescript
   const isDuplicate = await groupsRepo.groupExistsByVkId(group.id)
   ```
4. **Обновление статистики:**
   - Валидные группы → в массив для сохранения
   - Дубликаты → stats.duplicate++
   - Невалидные (не вернулись из API) → в errors[]
5. **Progress update** после каждого батча
6. **Задержка 400ms** между батчами

### Этап 3: Сохранение в БД (70-95%)
1. **Подготовка данных для БД:**
   ```typescript
   {
     vk_id: group.id,
     name: group.name,
     screen_name: group.screen_name,
     photo_50: group.photo_50,
     members_count: group.members_count,
     is_closed: group.is_closed,
     description: group.description,
     status: 'valid',
     task_id: taskId
   }
   ```
2. **Сохранение батчами по 50 групп:**
   ```typescript
   await groupsRepo.createGroups(groupsData, taskId)
   ```
   - Upsert логика (обновление существующих)
   - Транзакционное сохранение
3. **Progress update** после каждого батча

### Этап 4: Финализация (95-100%)
1. Подсчет финальной статистики
2. Определение успешности (`success = saved > 0`)
3. Обновление задачи:
   - Успех: `taskService.completeTask(taskId, metadata)`
   - Ошибка: `taskService.failTask(taskId, error)`
4. Progress: 100%

## Конфигурация

### Батч-обработка (BATCH_CONFIG)

```typescript
{
  VK_API_BATCH_SIZE: 100,     // Размер батча для VK API
  DB_SAVE_BATCH_SIZE: 50,     // Размер батча для БД
  BATCH_DELAY_MS: 400,        // Задержка между VK API запросами
  PROGRESS_UPDATE_INTERVAL: 10 // Обновлять каждые N групп
}
```

### BullMQ Worker Config

```typescript
WORKER_CONFIGS[QUEUE_NAMES.PROCESS_GROUPS] = {
  concurrency: 2,              // 2 одновременных job'а
  limiter: {
    max: 10,                   // Максимум 10 jobs
    duration: 60000            // За 60 секунд
  },
  stalledInterval: 30000,      // 30 секунд
  maxStalledCount: 1
}
```

## Использование

### Запуск worker'а

```typescript
import { groupsParseWorker } from '@/workers';

// Автоматический старт при импорте (singleton)
// или явный запуск:
await groupsParseWorker.start();
```

### Создание job'а

```typescript
import { queueService } from '@/services/queueService';

const job = await queueService.addProcessGroupsJob({
  type: 'process_groups',
  metadata: {
    groupIdentifiers: ['12345', 'apiclub', '67890'],
    source: 'file',
    originalFileName: 'groups.txt'
  }
}, taskId);
```

### Остановка worker'а

```typescript
await groupsParseWorker.stop();
```

### Получение статуса

```typescript
const status = groupsParseWorker.getStatus();
// {
//   isRunning: true,
//   isPaused: false,
//   concurrency: 2,
//   queueName: 'process-groups'
// }
```

## Интеграция с сервисами

### VK-IO Service

**Метод:** `vkIoService.getGroupsInfo(identifiers)`

- **Вход:** `Array<number | string>` - смешанный массив VK ID и screen_name
- **Выход:** `ProcessedGroup[]` - массив с полной информацией
- **Автоматически:**
  - Определяет тип идентификатора
  - Конвертирует в формат VK API
  - Делает `groups.getById` запрос
  - Обрабатывает rate limiting
  - Retry при ошибках

### Groups Repository

**Методы:**
- `createGroups(groupsData, taskId)` - upsert групп в БД
- `groupExistsByVkId(vkId)` - проверка дубликата

**Транзакции:** Все сохранения транзакционные

### Task Service

**Методы:**
- `getTaskById(taskId)` - получение задачи
- `updateTaskStatus(taskId, status, startedAt)` - обновление статуса
- `updateTaskProgress(taskId, progress, metadata)` - прогресс
- `completeTask(taskId, metadata)` - успешное завершение
- `failTask(taskId, error)` - ошибка

## Обработка ошибок

### Типы ошибок

1. **Группа не найдена** - VK ID не существует
   - Действие: Добавить в `errors[]`, продолжить
   - Статистика: `invalid++`

2. **Screen name неверный** - не группа или не существует
   - Действие: Добавить в `errors[]`, продолжить
   - Статистика: `invalid++`

3. **Группа недоступна** - закрыта/удалена/заблокирована
   - Действие: Добавить в `errors[]`, продолжить
   - Статистика: `invalid++`

4. **Дубликат в БД** - группа уже существует
   - Действие: Пропустить сохранение
   - Статистика: `duplicate++`

5. **VK API ошибка** - rate limit, invalid token
   - Действие: Worker retry через BullMQ (3 попытки)
   - Exponential backoff

6. **БД ошибка** - connection lost
   - Действие: Worker retry через BullMQ
   - Fail job если критическая

### Стратегия успешности

- ✅ **Job успешен** если `stats.saved > 0`
- ❌ **Job failed** если критическая ошибка (нет токена, БД недоступна)
- ⚠️ **Частичный успех** возможен (некоторые группы сохранены, некоторые нет)

## Логирование

### INFO уровень

```typescript
logger.info('Groups parse job started', { jobId, taskId, totalIdentifiers });
logger.info('Batch processed', { batch, totalBatches, validInBatch });
logger.info('Groups parse job completed', { stats, processingTime });
```

### WARN уровень

```typescript
logger.warn('Failed to update job progress', { jobId, error });
```

### ERROR уровень

```typescript
logger.error('Error processing batch', { batch, error });
logger.error('Groups parse job failed', { jobId, taskId, error });
```

### DEBUG уровень

```typescript
logger.debug('Group is duplicate', { vkId, name });
logger.debug('Groups parse job progress', { percentage, stage });
```

## Frontend интеграция

Frontend компонент `GroupsUpload.vue` уже готов для работы с worker'ом:

### Отображение прогресса

```vue
<v-progress-linear
  :model-value="getProgressPercentage()"
  :color="getProgressColor(status)"
/>

<span>
  {{ uploadTask.progress.processed || 0 }}/{{ uploadTask.progress.total || 0 }}
  ({{ getProgressPercentage() }}%)
</span>
```

### Адаптивный polling

```javascript
const polling = useAdaptivePolling(
  computed(() => String(uploadTask.value.taskId || '')),
  'general'
)

await polling.startPolling(async () => {
  const response = await groupsApi.getTaskStatus(taskId)
  updateTaskStatus(response.data.data)
  return { status, progress, errors, ...data }
})
```

### Отображение ошибок

```vue
<v-list-item v-for="(error, index) in uploadTask.errors">
  <v-list-item-title>{{ error.message || error }}</v-list-item-title>
  <v-list-item-subtitle>Строка: {{ error.line }}</v-list-item-subtitle>
</v-list-item>
```

## Примеры использования

### Пример 1: Обработка файла с VK ID

```typescript
// Входные данные
{
  groupIdentifiers: ['12345678', '87654321', '11111111'],
  source: 'file',
  originalFileName: 'groups.txt'
}

// Результат
{
  success: true,
  stats: {
    total: 3,
    valid: 2,      // Две группы найдены
    invalid: 1,    // Одна не существует
    duplicate: 0,
    saved: 2
  },
  errors: [
    {
      identifier: '11111111',
      error: 'Group not found or inaccessible'
    }
  ]
}
```

### Пример 2: Смешанные идентификаторы

```typescript
// Входные данные
{
  groupIdentifiers: ['12345', 'apiclub', '67890', 'devclub'],
  source: 'manual'
}

// VK-IO автоматически обработает все типы
// Результат
{
  success: true,
  stats: {
    total: 4,
    valid: 3,      // apiclub, devclub и 67890 найдены
    invalid: 1,    // 12345 не существует
    duplicate: 0,
    saved: 3
  }
}
```

### Пример 3: Обработка дубликатов

```typescript
// В БД уже есть группы с VK ID: 12345, 67890

// Входные данные
{
  groupIdentifiers: ['12345', '67890', '11111'],
  source: 'file'
}

// Результат
{
  success: true,
  stats: {
    total: 3,
    valid: 3,      // Все группы существуют
    invalid: 0,
    duplicate: 2,  // 12345 и 67890 уже в БД
    saved: 1       // Только 11111 сохранена
  }
}
```

## Мониторинг и отладка

### События worker'а

```typescript
worker.on('ready', () => { ... });         // Worker готов
worker.on('completed', (job, result) => { ... }); // Job завершен
worker.on('failed', (job, error) => { ... });     // Job failed
worker.on('progress', (job, progress) => { ... }); // Progress update
worker.on('error', (error) => { ... });    // Worker ошибка
worker.on('stalled', (jobId) => { ... });  // Job завис
worker.on('drained', () => { ... });       // Очередь пуста
```

### Health check

```typescript
const status = groupsParseWorker.getStatus();
console.log('Worker status:', status);
// {
//   isRunning: true,
//   isPaused: false,
//   concurrency: 2,
//   queueName: 'process-groups'
// }
```

### Метрики производительности

- **Processing time:** `result.processingTimeMs`
- **Throughput:** `stats.saved / (processingTimeMs / 1000)` групп/сек
- **Error rate:** `errors.length / stats.total * 100%`
- **Duplicate rate:** `stats.duplicate / stats.total * 100%`

## Рекомендации

### Оптимизация производительности

1. **Батч-размеры:**
   - VK API: 100 ID (баланс между скоростью и надежностью)
   - БД: 50 групп (оптимально для транзакций)

2. **Rate limiting:**
   - Задержка 400ms между VK API запросами
   - BullMQ limiter: 10 jobs/минуту

3. **Concurrency:**
   - Worker: 2 одновременных job'а
   - Не перегружать VK API

### Обработка больших объемов

Для обработки 1000+ групп:
1. Файл разбивается на части автоматически
2. Батч-обработка оптимизирована
3. Progress tracking позволяет отслеживать прогресс
4. При ошибках - продолжение обработки

### Troubleshooting

**Проблема:** Worker не запускается
```bash
# Проверить Redis соединение
docker-compose logs redis

# Проверить логи worker'а
tail -f logs/worker.log | grep GroupsParseWorker
```

**Проблема:** Все группы в invalid
```bash
# Проверить VK токен
echo $VK_ACCESS_TOKEN

# Проверить логи VK-IO
tail -f logs/app.log | grep VkIoService
```

**Проблема:** Дубликаты не определяются
```bash
# Проверить БД
docker-compose exec postgres psql -U postgres -d vk_analyzer
SELECT COUNT(*) FROM groups;
```

## Changelog

### v1.0.0 (2025-01-XX)
- ✅ Первая рабочая версия
- ✅ Поддержка VK ID и screen_name через VK-IO
- ✅ Батч-обработка
- ✅ Progress tracking
- ✅ Проверка дубликатов
- ✅ Graceful error handling
- ✅ Полная интеграция с существующей инфраструктурой
