# План рефакторинга утилит Backend

**Дата создания**: 2025-09-30
**Статус**: Готов к реализации
**Приоритет**: Средний

---

## Обзор

Анализ показал, что 4 утилиты backend требуют различных уровней рефакторинга:

| Утилита | Действие | Приоритет | Сложность |
|---------|----------|-----------|-----------|
| `logger.ts` | ✅ Рефакторинг | Высокий | Низкая |
| `errors.ts` | ✅ Оставить | - | - |
| `vkValidator.ts` | ✅ Оставить + минорные улучшения | Низкий | Низкая |
| `dbMonitor.ts` | ⚠️ Оставить + документация | Низкий | - |

---

## 1. Рефакторинг logger.ts

### Текущие проблемы

1. **Избыточная обертка AppLogger** - дублирует функциональность Winston без добавления ценности
2. **Ограниченная типизация** - методы имеют разные сигнатуры (error принимает Error, остальные нет)
3. **Жесткая конфигурация путей** - hardcoded пути к log файлам
4. **Отсутствие context enrichment** - нет requestId, userId и других мета-данных

### Стратегия рефакторинга

**Вариант 1: Упростить обертку (Рекомендуется)**
- Убрать класс AppLogger
- Создать фабрику для создания Winston logger с правильной конфигурацией
- Добавить типизированные helper функции для структурированного логирования
- Сохранить обратную совместимость

**Вариант 2: Миграция на Pino**
- Полная замена Winston на Pino (быстрее в 2-5x)
- Лучшая производительность для high-load сценариев
- Требует изменения всех импортов (22 файла)

### Рекомендация: Вариант 1

**Преимущества**:
- Минимальные изменения в кодовой базе
- Обратная совместимость
- Сохранение знакомого API

**Недостатки**:
- Не даст прироста производительности

---

## 2. План действий по logger.ts

### Шаг 1: Создать новую структуру logger

**Файл**: `backend/src/utils/logger.ts`

**Изменения**:

```typescript
/**
 * Новая структура:
 * 1. Убрать класс AppLogger
 * 2. Создать createLogger() фабрику
 * 3. Экспортировать singleton instance
 * 4. Добавить typed helpers для context enrichment
 */

// Интерфейсы
interface LoggerContext {
  requestId?: string;
  userId?: string;
  taskId?: string;
  [key: string]: any;
}

interface LoggerOptions {
  level?: LogLevel;
  service?: string;
  environment?: Environment;
  logDir?: string;
}

// Фабрика для создания logger
function createLogger(options?: LoggerOptions): winston.Logger

// Singleton instance (default export)
const logger = createLogger()

// Helper функции
function withContext(logger: winston.Logger, context: LoggerContext): winston.Logger
function formatError(error: Error): object

// Экспорты
export default logger
export { createLogger, withContext, formatError }
export type { LoggerContext, LoggerOptions }
```

### Шаг 2: Конфигурация

**Изменить**:
- ✅ Использовать env переменные для путей к логам
- ✅ Добавить поддержку log rotation через winston-daily-rotate-file
- ✅ Настроить structured logging format

**Добавить в .env**:
```bash
LOG_LEVEL=info
LOG_DIR=backend/logs
LOG_MAX_SIZE=5m
LOG_MAX_FILES=5
```

### Шаг 3: Обратная совместимость

**Гарантии**:
- Сохранить те же методы: `info()`, `error()`, `warn()`, `debug()`
- Сохранить экспорт `export default logger`
- Все 22 файла продолжат работать без изменений

**Опциональные улучшения** (для новых мест):
```typescript
// Старый способ (продолжит работать)
logger.info('User created', { userId: 123 })

// Новый способ (опционально)
const ctxLogger = withContext(logger, { requestId: '123', userId: 'user-1' })
ctxLogger.info('User action', { action: 'created' })
```

### Шаг 4: Тестирование

**Требуется**:
1. Unit тесты для createLogger()
2. Проверка обратной совместимости
3. Интеграционные тесты с реальными запросами
4. Проверка rotation логов

---

## 3. errors.ts - Оставить без изменений

### Решение: ✅ Оставить как есть

**Обоснование**:
- Отлично спроектированная система ошибок
- Полная типизация TypeScript
- Интеграция с Joi, Prisma, VK API
- Request context tracking (requestId, userId)
- Stack trace capture
- Операционные vs программные ошибки

**Сильные стороны**:
1. BaseAppError с полным контекстом
2. Специализированные ошибки (ValidationError, VkApiError, TaskError, DatabaseError)
3. Фабричные методы (fromJoi, fromPrisma, fromVkResponse)
4. ErrorUtils для унификации обработки
5. Цепочка причин (cause)

**Минорные улучшения** (опционально, low priority):
- Добавить JSDoc комментарии к классам
- Создать unit тесты для ErrorUtils
- Добавить примеры использования в комментариях

---

## 4. vkValidator.ts - Минорные улучшения

### Решение: ✅ Оставить + небольшие улучшения

**Обоснование**:
- Специфичная бизнес-логика VK групп
- Правильная обработка rate limiting
- Batch processing
- Логика резолвинга (положительные ID пропускаются)

### Минорные улучшения (опционально)

**Изменение 1**: Использовать библиотеку p-limit для batch processing
```typescript
// Вместо ручного батчинга использовать:
import pLimit from 'p-limit'

const limit = pLimit(this.rateLimit)
const promises = batches.map(batch => limit(() => this.validateBatch(batch)))
```

**Изменение 2**: Добавить retry logic для failed batches
```typescript
// Использовать axios-retry (уже в dependencies)
import axiosRetry from 'axios-retry'

axiosRetry(axios, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    return error.response?.status === 500 || error.code === 'ECONNRESET'
  }
})
```

**Изменение 3**: Улучшить типизацию ValidationResult
```typescript
// Добавить статистику
interface ValidationResult {
  validGroups: ProcessedGroup[];
  invalidGroups: ProcessedGroup[];
  errors: ValidationError[];
  statistics: {
    total: number;
    valid: number;
    invalid: number;
    resolved: number; // положительные ID, пропущенные валидацию
    batchesProcessed: number;
    duration: number; // ms
  };
}
```

---

## 5. dbMonitor.ts - Оставить + улучшить документацию

### Решение: ✅ Оставить как есть

**Обоснование**:
- Уникальная утилита мониторинга PostgreSQL
- Нет готовых аналогов с такой глубиной анализа
- Ценно для production monitoring
- Хорошо интегрирована с Prisma

**Улучшения** (опционально):

### Изменение 1: Добавить endpoint для мониторинга

**Файл**: `backend/src/routes/monitoring.ts` (новый)

```typescript
import { Router } from 'express';
import { DatabaseMonitor } from '@/utils/dbMonitor';
import prisma from '@/config/prisma';

const router = Router();
const dbMonitor = new DatabaseMonitor(prisma);

// GET /api/monitoring/health
router.get('/health', async (req, res) => {
  const health = await dbMonitor.healthCheck();
  res.json(health);
});

// GET /api/monitoring/stats
router.get('/stats', async (req, res) => {
  const [poolStats, tableSizes, recommendations] = await Promise.all([
    dbMonitor.getPoolStats(),
    dbMonitor.getTableSizes(),
    dbMonitor.getOptimizationRecommendations()
  ]);

  res.json({ poolStats, tableSizes, recommendations });
});

export default router;
```

### Изменение 2: Добавить cron job для периодического мониторинга

**Опционально**: Использовать BullMQ для регулярного сбора метрик

---

## 6. Порядок реализации

### Фаза 1: logger.ts (Приоритет: Высокий)

**Время**: 2-3 часа

**Шаги**:
1. ✅ Создать новую версию logger.ts с фабрикой
2. ✅ Добавить env переменные для конфигурации
3. ✅ Написать unit тесты
4. ✅ Протестировать обратную совместимость
5. ✅ Обновить CLAUDE.md с новыми рекомендациями
6. ✅ Запустить полный test suite
7. ✅ Сделать коммит

**Риски**: Низкие (сохраняется обратная совместимость)

### Фаза 2: vkValidator.ts улучшения (Приоритет: Низкий)

**Время**: 1 час

**Шаги**:
1. ✅ Добавить p-limit (опционально)
2. ✅ Настроить axios-retry
3. ✅ Добавить statistics в ValidationResult
4. ✅ Обновить тесты
5. ✅ Сделать коммит

**Риски**: Низкие (только добавление функциональности)

### Фаза 3: dbMonitor.ts улучшения (Приоритет: Очень низкий)

**Время**: 1-2 часа

**Шаги**:
1. ✅ Создать endpoint для мониторинга
2. ✅ Добавить в router
3. ✅ Добавить документацию по использованию
4. ✅ Сделать коммит

**Риски**: Нет (только новая функциональность)

---

## 7. Зависимости и библиотеки

### Текущие (используются)
- ✅ winston: 3.17.0
- ✅ axios-retry: 4.5.0
- ✅ @prisma/client: 6.16.2

### Требуются дополнительно (опционально)

**Для logger.ts**:
```bash
npm install winston-daily-rotate-file
```

**Для vkValidator.ts**:
```bash
npm install p-limit
npm install -D @types/p-limit
```

---

## 8. Тестирование

### logger.ts тесты

**Файл**: `backend/tests/unit/utils/logger.test.ts`

**Тест-кейсы**:
1. Создание logger через фабрику
2. Логирование на разных уровнях
3. Context enrichment через withContext()
4. File transport в production
5. Отсутствие file transport в test mode
6. Форматирование ошибок

### vkValidator.ts тесты

**Файл**: `backend/tests/unit/utils/vkValidator.test.ts`

**Добавить**:
1. Retry logic для failed requests
2. Statistics в ValidationResult
3. p-limit batch processing

---

## 9. Документация

### Обновить CLAUDE.md

**Секция "Important Files"**:
```markdown
#### Backend Files (TypeScript)

**Утилиты**:
- `backend/src/utils/logger.ts` - Winston logger с context enrichment и structured logging
- `backend/src/utils/errors.ts` - Типизированная система ошибок с полным контекстом
- `backend/src/utils/vkValidator.ts` - Валидация VK групп через API с rate limiting
- `backend/src/utils/dbMonitor.ts` - Мониторинг производительности PostgreSQL

**Использование logger**:
```typescript
// Базовое логирование
import logger from '@/utils/logger';
logger.info('Message', { meta: 'data' });

// С контекстом
import { withContext } from '@/utils/logger';
const ctxLogger = withContext(logger, { requestId: req.id });
ctxLogger.info('User action');
```
```

### Создать README для utils

**Файл**: `backend/src/utils/README.md` (новый)

**Содержание**:
- Описание каждой утилиты
- Примеры использования
- API reference
- Best practices

---

## 10. Rollback план

### Если что-то пойдет не так

**logger.ts**:
```bash
# Откатить изменения
git revert <commit-hash>

# Восстановить старую версию
git checkout HEAD~1 -- backend/src/utils/logger.ts
```

**Альтернатива**: Сохранить старую версию как `logger.legacy.ts`

---

## 11. Метрики успеха

### logger.ts рефакторинг

- ✅ Все 22 файла продолжают работать без изменений
- ✅ Тесты проходят (100% coverage для logger)
- ✅ Логи пишутся в правильные файлы
- ✅ Log rotation работает
- ✅ Context enrichment доступен
- ✅ Производительность не снизилась

### vkValidator.ts улучшения

- ✅ Retry logic работает для failed batches
- ✅ Statistics собирается корректно
- ✅ Производительность не снизилась

---

## 12. Checklist перед началом

- [ ] Создать ветку `refactor/backend-utils`
- [ ] Убедиться что все тесты проходят на main
- [ ] Сделать backup базы данных (если нужно)
- [ ] Уведомить команду о рефакторинге
- [ ] Установить дополнительные зависимости

---

## 13. Итоговые рекомендации

### Обязательно сделать

1. ✅ **Рефакторинг logger.ts** - упростить обертку, добавить context enrichment
2. ✅ **Оставить errors.ts** - уже отличная реализация
3. ✅ **Оставить vkValidator.ts** - специфичная бизнес-логика
4. ✅ **Оставить dbMonitor.ts** - уникальный инструмент мониторинга

### Опционально сделать

1. ⚠️ Добавить winston-daily-rotate-file для log rotation
2. ⚠️ Добавить retry logic в vkValidator.ts
3. ⚠️ Создать endpoint для dbMonitor.ts
4. ⚠️ Написать unit тесты для всех утилит
5. ⚠️ Создать README.md для utils директории

### Не делать

1. ❌ Не мигрировать на Pino (слишком много изменений)
2. ❌ Не использовать библиотеки для errors.ts (custom решение лучше)
3. ❌ Не заменять vkValidator.ts на готовое решение (нет аналогов)
4. ❌ Не удалять dbMonitor.ts (ценный инструмент)

---

## 14. Временные оценки

| Задача | Время | Приоритет |
|--------|-------|-----------|
| logger.ts рефакторинг | 2-3 часа | Высокий |
| logger.ts тесты | 1 час | Высокий |
| vkValidator.ts улучшения | 1 час | Низкий |
| dbMonitor.ts endpoint | 1-2 часа | Очень низкий |
| Документация | 1 час | Средний |
| **Итого** | **6-8 часов** | - |

---

## 15. Следующие шаги

После утверждения плана:

1. Создать ветку `refactor/backend-utils`
2. Начать с Фазы 1 (logger.ts)
3. После успешного завершения фазы - сделать commit и PR
4. Перейти к следующим фазам по приоритету
5. Обновить документацию

---

**Составил**: Claude Code
**Версия плана**: 1.0
**Последнее обновление**: 2025-09-30