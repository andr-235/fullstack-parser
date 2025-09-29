# VkCollectWorker

VkCollectWorker - класс для обработки задач сбора комментариев из VK с использованием BullMQ.

## Особенности

- **Строгая типизация TypeScript** - полная типобезопасность
- **Интеграция с существующими сервисами** - использует taskService, vkService, vkIoService, dbRepo
- **Proper error handling** - детализированная обработка ошибок с retry логикой
- **Progress tracking** - отслеживание прогресса с детализированными метриками
- **Rate limiting** - защита VK API от превышения лимитов
- **Structured logging** - структурированное логирование для мониторинга

## Использование

```typescript
import vkCollectWorker, { VkCollectWorker } from '@/workers/vkCollectWorker';

// Использование singleton экземпляра
await vkCollectWorker.start();

// Создание нового экземпляра с кастомной конфигурацией
const customWorker = new VkCollectWorker({
  concurrency: 2,
  limiter: {
    max: 5,
    duration: 60000
  }
});
```

## Архитектура

### Основные методы

- `processJob()` - основной метод обработки VK collect job'а
- `processGroup()` - обработка отдельной VK группы
- `updateJobProgress()` - обновление прогресса с детализированной информацией
- `setupEventHandlers()` - настройка обработчиков событий worker'а

### Типы данных

- `VkCollectJobData` - входные данные для job'а
- `VkCollectJobResult` - результат выполнения job'а
- `VkCollectJobProgress` - информация о прогрессе

### События

Worker генерирует следующие события:
- `ready` - worker готов к работе
- `completed` - job завершен успешно
- `failed` - job завершен с ошибкой
- `progress` - обновление прогресса
- `error` - ошибка worker'а
- `stalled` - job завис
- `drained` - очередь пуста

## Конфигурация

Worker использует конфигурацию из `@/config/queue`:

```typescript
const workerConfig = WORKER_CONFIGS[QUEUE_NAMES.VK_COLLECT];
// {
//   concurrency: 1,        // Только один VK job одновременно
//   stalledInterval: 30000, // 30 секунд
//   maxStalledCount: 1,
//   limiter: {
//     max: 3,               // Консервативный rate limit для VK API
//     duration: 60000
//   }
// }
```

## Интеграция

Worker интегрируется с:

1. **TaskService** - обновление статуса задач
2. **VkIoService** - получение данных из VK через vk-io
3. **DbRepo** - сохранение данных в базу
4. **Logger** - структурированное логирование

## Обработка ошибок

- Retry логика с exponential backoff
- Graceful handling ошибок VK API
- Продолжение обработки других групп при ошибках
- Детализированное логирование всех ошибок

## Мониторинг

Worker предоставляет метрики для мониторинга:

```typescript
const status = worker.getWorkerStatus();
// {
//   isRunning: boolean,
//   isPaused: boolean,
//   concurrency: number,
//   queueName: string
// }
```

## Производительность

- Concurrency control для защиты VK API
- Rate limiting для предотвращения блокировок
- Efficient memory usage с removeOnComplete/removeOnFail
- Progress tracking не блокирует основную обработку