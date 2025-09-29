# План анализа и рефакторинга директории repositories

## Текущее состояние

### Файлы в директории:
- `dbRepo.ts` - основной репозиторий для работы с задачами, постами, комментариями
- `groupsRepo.ts` - репозиторий для работы с группами

### Использование:
- `dbRepo.ts` используется в: vkCollectWorker, taskService, taskResultsController
- `groupsRepo.ts` используется в: groupsService

## Выявленные проблемы

### 1. Критические проблемы архитектуры

#### 1.1 Нарушение принципа единственной ответственности
- `dbRepo.ts` управляет сразу 4 сущностями: tasks, posts, comments, groups
- Файл содержит 470+ строк кода
- Смешивает различные уровни абстракции

#### 1.2 Дублирование функционала
- Метод `getGroupsWithVkDataByTaskId` дублируется в обоих файлах (строки 428-465 в dbRepo, 443-472 в groupsRepo)
- Одинаковая логика обработки ошибок повторяется во всех методах

#### 1.3 Временные/некорректные типы
```typescript
// В dbRepo.ts (строки 5-10)
type tasks = any;
type posts = any;
type comments = any;
```
- Используются `any` типы вместо типов из Prisma
- Это нарушает типобезопасность TypeScript

### 2. Проблемы с хардкодом

#### 2.1 Хардкод статусов и значений по умолчанию
```typescript
// Строка 63-70 в dbRepo.ts
type: taskData.type || 'fetch_comments',
status: taskData.status || 'pending',
priority: taskData.priority || 0,
createdBy: taskData.createdBy || 'system',
```

#### 2.2 Хардкод дат
```typescript
// Повсеместное использование
createdAt: new Date(),
updatedAt: new Date()
```

#### 2.3 Хардкод имен полей базы данных
```typescript
// Строка 299 в dbRepo.ts
comments_comments_post_idToposts: true // некорректное имя связи
```

### 3. Проблемы структуры кода

#### 3.1 Повторяющийся код обработки ошибок
- В каждом методе дублируется одинаковая логика try-catch
- Отсутствует унифицированный подход к логированию ошибок

#### 3.2 Смешивание уровней абстракции
- В `groupsRepo.ts` парсинг параметров происходит в репозитории (строки 160-161)
- Это должно происходить на уровне контроллера или middleware

#### 3.3 Отсутствие базового класса
- Нет общего интерфейса для репозиториев
- Каждый репозиторий реализует свою логику

## План рефакторинга

### Этап 1: Анализ зависимостей
- [x] Проанализированы импорты и использование репозиториев
- [ ] Определить какие методы действительно используются
- [ ] Выявить неиспользуемые методы для удаления

### Этап 2: Создание базовой архитектуры

#### 2.1 Создать базовый класс репозитория
```typescript
// Новый файл: baseRepository.ts
abstract class BaseRepository {
  protected handleError(error: unknown, context: string, metadata?: any): never;
  protected validateExists<T>(entity: T | null, entityName: string, id: any): T;
  protected createTimestamps(): { createdAt: Date; updatedAt: Date };
}
```

#### 2.2 Создать константы для статусов
```typescript
// Новый файл: constants/index.ts
export const TASK_STATUSES = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const;

export const TASK_TYPES = {
  FETCH_COMMENTS: 'fetch_comments',
  PROCESS_GROUPS: 'process_groups',
  ANALYZE_POSTS: 'analyze_posts'
} as const;

export const GROUP_STATUSES = {
  VALID: 'valid',
  INVALID: 'invalid',
  DUPLICATE: 'duplicate'
} as const;
```

#### 2.3 Улучшить типизацию
```typescript
// Использовать правильные типы из Prisma
import { tasks, posts, comments, groups, Prisma } from '@prisma/client';

// Создать специфичные типы для операций
type TaskWithRelations = tasks & {
  posts: (posts & { comments: comments[] })[];
};
```

### Этап 3: Разделение ответственности

#### 3.1 Разбить dbRepo.ts на специализированные репозитории:
- `taskRepository.ts` - управление задачами
- `postRepository.ts` - управление постами
- `commentRepository.ts` - управление комментариями
- Переработать `groupsRepository.ts`

#### 3.2 Создать агрегирующий сервис (если нужен)
```typescript
// aggregateRepository.ts - для сложных операций
class AggregateRepository {
  constructor(
    private taskRepo: TaskRepository,
    private postRepo: PostRepository,
    private commentRepo: CommentRepository,
    private groupRepo: GroupsRepository
  ) {}

  async getTaskResults(taskId: number) {
    // Комбинирует данные из разных репозиториев
  }
}
```

### Этап 4: Устранение дублирования

#### 4.1 Удалить дублированные методы
- Удалить `getGroupsWithVkDataByTaskId` из `dbRepo.ts`
- Объединить логику схожих методов

#### 4.2 Создать общие утилиты
```typescript
// utils/repositoryUtils.ts
export class RepositoryUtils {
  static buildPaginationResult<T>(items: T[], total: number, limit: number, offset: number);
  static buildWhereClause(filters: Record<string, any>): Prisma.WhereInput;
  static parseNumericParam(value: any, defaultValue: number): number;
}
```

### Этап 5: Замена хардкода на библиотеки

#### 5.1 Использовать библиотеку для работы с датами
```bash
npm install date-fns
```
```typescript
import { format, addDays, isValid } from 'date-fns';
import { ru } from 'date-fns/locale';
```

#### 5.2 Использовать библиотеку для валидации
```bash
npm install zod
```
```typescript
import { z } from 'zod';

const CreateTaskSchema = z.object({
  type: z.enum(['fetch_comments', 'process_groups', 'analyze_posts']),
  priority: z.number().min(0).default(0),
  groups: z.array(z.any()).default([]),
  // ...
});
```

#### 5.3 Использовать HTTP status codes константы
```bash
npm install http-status-codes
```
```typescript
import { StatusCodes } from 'http-status-codes';
```

### Этап 6: Оптимизация производительности

#### 6.1 Добавить индексы в Prisma schema
```prisma
// Для часто используемых запросов
@@index([task_id, status])
@@index([vk_id])
@@index([created_at])
```

#### 6.2 Оптимизировать запросы
- Использовать `select` вместо получения всех полей
- Оптимизировать включения (includes)
- Добавить батчинг для массовых операций

### Этап 7: Улучшение обработки ошибок

#### 7.1 Создать специализированные исключения
```typescript
// errors/repositoryErrors.ts
export class EntityNotFoundError extends Error {
  constructor(entityName: string, id: any) {
    super(`${entityName} with id ${id} not found`);
    this.name = 'EntityNotFoundError';
  }
}

export class ValidationError extends Error {
  constructor(message: string, field?: string) {
    super(message);
    this.name = 'ValidationError';
  }
}
```

#### 7.2 Стандартизировать логирование
```typescript
// utils/logger.ts расширить
class RepositoryLogger {
  static logOperation(operation: string, entity: string, metadata?: any);
  static logError(error: Error, operation: string, metadata?: any);
}
```

## Что нужно удалить

### 1. Неиспользуемые методы (требует дополнительного анализа)
- Методы, которые не вызываются из services/controllers
- Методы-дубликаты

### 2. Временные типы
```typescript
// Удалить эти строки из dbRepo.ts:
type tasks = any;
type posts = any;
type comments = any;
```

### 3. Хардкод значения
- Магические числа и строки
- Повторяющиеся значения по умолчанию
- Inline SQL или Prisma запросы без констант

### 4. Избыточный код
- Дублированные методы обработки ошибок
- Повторяющиеся проверки существования
- Одинаковая логика валидации

## План замены хардкода на библиотеки

### 1. Даты и время
**Текущий хардкод:**
```typescript
createdAt: new Date(),
updatedAt: new Date()
```

**Замена:**
```typescript
import { addHours, format, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';

// В утилите
class DateUtils {
  static now(): Date { return new Date(); }
  static formatForDb(date: Date): Date { return date; }
  static addHours(date: Date, hours: number): Date { return addHours(date, hours); }
}
```

### 2. Валидация данных
**Текущий хардкод:**
```typescript
if (!task) {
  throw new Error(`Task with id ${taskId} not found`);
}
```

**Замена:**
```typescript
import { z } from 'zod';

const TaskIdSchema = z.number().positive();
const validateTaskId = (id: any) => TaskIdSchema.parse(id);
```

### 3. HTTP статусы и коды
**Текущий хардкод:**
```typescript
status: taskData.status || 'pending'
```

**Замена:**
```typescript
import { StatusCodes } from 'http-status-codes';
import { TASK_STATUSES } from '@/constants';

status: taskData.status || TASK_STATUSES.PENDING
```

### 4. Конфигурация пагинации
**Текущий хардкод:**
```typescript
limit = 20,
offset = 0
```

**Замена:**
```typescript
import { PAGINATION_DEFAULTS } from '@/constants';

limit = PAGINATION_DEFAULTS.LIMIT,
offset = PAGINATION_DEFAULTS.OFFSET
```

## Этапы выполнения

### Приоритет 1 (Критично)
1. Создать константы для статусов и типов
2. Исправить типизацию (убрать any типы)
3. Удалить дублированные методы
4. Создать базовый класс репозитория

### Приоритет 2 (Важно)
1. Разделить dbRepo на специализированные репозитории
2. Стандартизировать обработку ошибок
3. Добавить валидацию с zod
4. Оптимизировать запросы к БД

### Приоритет 3 (Желательно)
1. Добавить индексы в БД
2. Создать утилиты для общих операций
3. Улучшить логирование
4. Добавить метрики производительности

## Ожидаемые результаты

После рефакторинга получим:
- ✅ Четкое разделение ответственности
- ✅ Устранение дублирования кода
- ✅ Улучшенную типобезопасность
- ✅ Стандартизированную обработку ошибок
- ✅ Лучшую читаемость и поддерживаемость
- ✅ Оптимизированную производительность
- ✅ Соответствие принципам SOLID

## Риски и митигация

### Риски:
1. **Поломка существующих интеграций** - изменение интерфейсов репозиториев
2. **Увеличение сложности** - больше файлов для поддержки
3. **Временные затраты** - необходимо обновить все зависимые сервисы

### Митигация:
1. Сохранять обратную совместимость через deprecated методы
2. Поэтапное выполнение с тестированием каждого этапа
3. Обновление тестов параллельно с рефакторингом
4. Создание миграционных скриптов

---

**Примечание:** Данный план требует детального тестирования на каждом этапе. Рекомендуется начать с создания констант и улучшения типизации, так как это наименее рискованные изменения.