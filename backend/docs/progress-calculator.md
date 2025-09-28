# ProgressCalculator - Точный Расчет Прогресса

## Обзор

`ProgressCalculator` решает критическую проблему в системе VK Analytics, где старый алгоритм использовал произвольный множитель `* 10`, приводящий к ситуации `processed > total`.

## Проблема

**Старый алгоритм:**
```typescript
// ❌ ПРОБЛЕМА: произвольный множитель
total: Math.max(taskStatus.metrics.posts * 10, taskStatus.metrics.comments)
```

**Проблемы старого подхода:**
- При `comments > posts * 10` мгновенно получаем 100%
- Нет учета фаз обработки (groups → posts → comments)
- Произвольный множитель не отражает реальную сложность
- Прогресс может "прыгать" или зависать

## Решение

**Новый алгоритм с весовой системой:**

### Архитектура

```typescript
// ✅ РЕШЕНИЕ: многофазная система с весами
const PHASE_WEIGHTS = {
  groups: 0.1,      // 10% - получение списка групп
  posts: 0.3,       // 30% - получение постов
  comments: 0.6     // 60% - получение комментариев
}
```

### Ключевые принципы

1. **Процентная система**: `total` всегда = 100
2. **Фазовость**: groups → posts → comments
3. **Весовые коэффициенты**: отражают реальную сложность
4. **Валидация**: предотвращает некорректные данные

## Использование

### Основные методы

```typescript
import { ProgressCalculator } from '@/services/progressCalculator';

// 1. Расчет прогресса
const metrics = ProgressCalculator.createMetricsFromTask(taskStatus);
const progress = ProgressCalculator.calculateProgress(metrics);

// 2. Оценка общего объема
const estimate = ProgressCalculator.estimateTotal(taskData);

// 3. Валидация метрик
const errors = ProgressCalculator.validateMetrics(metrics);
```

### В контроллере

```typescript
const getTask = async (req: Request, res: Response) => {
  const taskStatus = await taskService.getTaskStatus(taskId);

  // Создаем метрики для расчета прогресса
  const metrics = ProgressCalculator.createMetricsFromTask(taskStatus);

  // Рассчитываем точный прогресс
  const progressResult = ProgressCalculator.calculateProgress(metrics);

  res.json({
    success: true,
    data: {
      progress: {
        processed: progressResult.processed,    // 0-100
        total: progressResult.total,           // всегда 100
        percentage: progressResult.percentage, // 0-100
        phase: progressResult.phase,          // 'groups' | 'posts' | 'comments'
        phases: progressResult.phases         // детали по фазам
      }
    }
  });
};
```

## Типы данных

### TaskMetrics

```typescript
interface TaskMetrics {
  groupsTotal: number;           // Общее количество групп
  groupsProcessed: number;       // Обработанные группы
  postsTotal: number;            // Общее количество постов
  postsProcessed: number;        // Обработанные посты
  commentsTotal: number;         // Общее количество комментариев
  commentsProcessed: number;     // Обработанные комментарии
  estimatedCommentsPerPost: number; // Среднее для оценки
}
```

### ProgressResult

```typescript
interface ProgressResult {
  processed: number;             // 0-100 (обработанные единицы)
  total: number;                // всегда 100
  percentage: number;           // 0-100 (процент выполнения)
  phase: 'groups' | 'posts' | 'comments'; // текущая фаза
  phases: {                     // детали по фазам
    groups: { weight: number; progress: number; completed: boolean };
    posts: { weight: number; progress: number; completed: boolean };
    comments: { weight: number; progress: number; completed: boolean };
  };
}
```

## Примеры прогресса

### Фаза Groups (10%)
```
Groups: 5/10 обработано
Progress: 5% (50% * 10%)
Phase: 'groups'
```

### Фаза Posts (30%)
```
Groups: 10/10 ✅ (10%)
Posts: 200/500 обработано
Progress: 22% (10% + 40% * 30%)
Phase: 'posts'
```

### Фаза Comments (60%)
```
Groups: 10/10 ✅ (10%)
Posts: 500/500 ✅ (30%)
Comments: 3750/7500 обработано
Progress: 70% (10% + 30% + 50% * 60%)
Phase: 'comments'
```

## Валидация

```typescript
const errors = ProgressCalculator.validateMetrics(metrics);
// Возможные ошибки:
// - "Groups: processed (10) > total (5)"
// - "Posts: processed (150) > total (100)"
// - "Comments: processed (2000) > total (1500)"
```

## Преимущества

### До (старый алгоритм)
- ❌ Произвольный множитель `* 10`
- ❌ Ситуация `processed > total`
- ❌ Прогресс может "прыгать"
- ❌ Нет учета фаз обработки

### После (новый алгоритм)
- ✅ Научно обоснованная весовая система
- ✅ Прогресс всегда 0-100%
- ✅ Плавное нарастание прогресса
- ✅ Учет всех фаз обработки
- ✅ Валидация и обработка ошибок

## Тестирование

```bash
# Запуск unit тестов
npm test progressCalculator.test.ts

# Запуск интеграционных тестов
npm test progress-calculation.test.ts

# Демонстрация работы
npx ts-node examples/progress-calculator-usage.ts
```

## Конфигурация

Весовые коэффициенты можно настроить в классе:

```typescript
private static readonly PHASE_WEIGHTS = {
  groups: 0.1,      // 10% - можно изменить при необходимости
  posts: 0.3,       // 30%
  comments: 0.6     // 60%
} as const;
```

## Мониторинг

В production логируются предупреждения при обнаружении некорректных метрик:

```typescript
logger.warn('Progress metrics validation warnings', {
  taskId,
  errors: validationErrors,
  metrics,
  id: requestId
});
```