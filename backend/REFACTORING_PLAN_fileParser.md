# План рефакторинга fileParser.ts (Обновленный)

## Дата обновления: 2025-09-30

---

## 🎯 Цель рефакторинга

Улучшить архитектуру `fileParser.ts` с учетом **существующей инфраструктуры utils** проекта, сделать код более тестируемым и расширяемым, применяя **практичный подход** без избыточной инженерии.

---

## 📊 Анализ текущей экосистемы utils

### Существующие утилиты в проекте

#### 1. **logger.ts** (102 строки) ✅
```typescript
// Хорошо спроектированный Winston logger
class AppLogger implements Logger {
  info(message: string, meta?: any): void
  error(message: string, error?: Error | any, meta?: any): void
  warn(message: string, meta?: any): void
  debug(message: string, meta?: any): void
}
```
**Оценка**: Отличная реализация, использовать как есть
**Интеграция**: fileParser должен использовать этот logger

#### 2. **errors.ts** (485 строк) ✅
```typescript
// Полная иерархия кастомных ошибок
class BaseAppError extends Error
class ValidationError extends BaseAppError
class VkApiError extends BaseAppError
class TaskError extends BaseAppError
class DatabaseError extends BaseAppError
class NotFoundError extends BaseAppError
// + утилиты ErrorUtils
```
**Оценка**: Профессиональная система ошибок с ErrorCodes
**Интеграция**: fileParser должен использовать ValidationError вместо собственной GroupParseError

#### 3. **vkValidator.ts** (279 строк) ✅
```typescript
// VK API валидатор с rate limiting и батч-обработкой
class VKValidator {
  validateGroups(groups: ProcessedGroup[]): Promise<ValidationResult>
  validateBatch(batch: ProcessedGroup[]): Promise<BatchResult>
  checkApiHealth(): Promise<boolean>
  getRateLimitInfo(): RateLimitInfo
}
```
**Оценка**: Хороший класс с DI через constructor options
**Интеграция**: Может работать с результатами fileParser

#### 4. **dbMonitor.ts** (557 строк) ✅
```typescript
// PostgreSQL/Prisma мониторинг и оптимизация
class DatabaseMonitor {
  getPoolStats(): Promise<PoolStats>
  getSlowQueries(limit: number): Promise<SlowQuery[]>
  getIndexUsage(tableName?: string): Promise<IndexUsage[]>
  healthCheck(): Promise<HealthCheck>
  runBenchmark(): Promise<Benchmark>
}
```
**Оценка**: Отличный инструмент для мониторинга
**Интеграция**: Не связан напрямую с fileParser

#### 5. **fileParser.ts** (439 строк) ⚠️
```typescript
// Статический класс для парсинга TXT файлов с VK группами
class FileParser {
  static async parseGroupsFile(filePath, encoding)
  static parseGroupLine(line, lineNumber)
  // + 12 приватных статических методов
}
```
**Оценка**: Хороший код, но требует улучшений
**Проблемы**: Статические методы, нет DI, hardcoded логика парсинга

---

## 🔍 Анализ fileParser.ts

### Положительные стороны ✅
- Хорошая модульность методов
- Подробная JSDoc документация
- Использование констант
- Обработка множества форматов
- Логирование результатов

### Проблемные зоны ❌
- **Все методы статические** → сложно тестировать с моками
- **Hardcoded последовательность парсинга** → нельзя расширить/изменить
- **Собственная GroupParseError** → есть ValidationError из errors.ts
- **Смешение ответственностей** → парсинг + валидация + построение URL
- **Нет интеграции** с существующими errors и logger типами

---

## 🎨 Упрощенная архитектура рефакторинга

### Основные принципы
1. **Использовать существующие утилиты** (logger, errors) — не дублировать код
2. **Паттерн Strategy** для парсинга — гибкость без усложнения
3. **Dependency Injection** через constructor — тестируемость
4. **Backward compatibility** — старый API продолжает работать
5. **Прагматичный подход** — улучшаем то, что действительно важно

---

## 🛠 План рефакторинга (2 фазы вместо 3)

### Фаза 1: Критичные улучшения (Must Have)
**Цель**: Улучшить архитектуру и интеграцию с существующими utils

#### 1.1. Интеграция с существующей системой ошибок ✅
**Проблема**: Собственная `GroupParseError`, когда есть `ValidationError`

**Решение**:
```typescript
// УДАЛИТЬ
class GroupParseError extends Error { ... }

// ИСПОЛЬЗОВАТЬ
import { ValidationError } from '@/utils/errors';

// В коде парсера
if (!isValid) {
  throw new ValidationError('Invalid group format')
    .addFieldError('line', 'Invalid VK group format', line, 'GROUP_FORMAT');
}
```

**Преимущества**:
- Единообразие ошибок в проекте
- Автоматическая интеграция с error middleware
- Структурированные ошибки валидации

**Оценка времени**: 2-3 часа

---

#### 1.2. Паттерн Strategy для парсинга форматов ✅
**Проблема**: Hardcoded последовательность проверок форматов

**Решение**: Цепочка парсеров с приоритетами

```typescript
// strategies/GroupParsingStrategy.ts
export interface GroupParsingStrategy {
  readonly name: string;
  readonly priority: number;
  readonly description: string;

  canParse(line: string): boolean;
  parse(line: string): { id: number | null; name: string | null } | null;
}

// strategies/UrlClubStrategy.ts
export class UrlClubStrategy implements GroupParsingStrategy {
  name = 'url_club';
  priority = 1;
  description = 'https://vk.com/club<ID>';

  canParse(line: string): boolean {
    return /^https:\/\/vk\.com\/club\d+$/i.test(line);
  }

  parse(line: string) {
    const match = line.match(/^https:\/\/vk\.com\/club(\d+)$/i);
    if (match) {
      const id = parseInt(match[1], 10);
      return id > 0 ? { id, name: null } : null;
    }
    return null;
  }
}

// Аналогично: UrlScreenNameStrategy, NegativeIdStrategy,
//             PositiveIdStrategy, ScreenNameStrategy

// GroupLineParser.ts
export class GroupLineParser {
  private strategies: GroupParsingStrategy[];

  constructor(strategies: GroupParsingStrategy[] = defaultStrategies) {
    this.strategies = strategies.sort((a, b) => a.priority - b.priority);
  }

  parse(line: string, lineNumber: number): { id: number | null; name: string | null } {
    for (const strategy of this.strategies) {
      if (strategy.canParse(line)) {
        const result = strategy.parse(line);
        if (result) return result;
      }
    }

    // Используем ValidationError вместо GroupParseError
    throw new ValidationError('Invalid group format')
      .addFieldError(
        `line_${lineNumber}`,
        'Line does not match any supported VK group format',
        line,
        'GROUP_FORMAT'
      );
  }

  // Позволяет добавлять кастомные стратегии
  addStrategy(strategy: GroupParsingStrategy): void {
    this.strategies.push(strategy);
    this.strategies.sort((a, b) => a.priority - b.priority);
  }
}
```

**Преимущества**:
- Легко добавлять новые форматы
- Каждая стратегия тестируется отдельно
- Можно изменить порядок парсинга
- Явная документация форматов

**Оценка времени**: 4-6 часов

---

#### 1.3. Dependency Injection для тестируемости ✅
**Проблема**: Статический класс с hardcoded зависимостями

**Решение**: Instance методы с DI

```typescript
// FileParser.ts (новый)
import logger from '@/utils/logger';
import { Logger } from '@/types/common';
import { ValidationError } from '@/utils/errors';

export interface FileParserConfig {
  maxFileSizeMb: number;
  allowedExtensions: readonly string[];
  encoding: BufferEncoding;
  sampleGroupsCount: number;
  vkBaseUrl: string;
}

export const defaultConfig: FileParserConfig = {
  maxFileSizeMb: 10,
  allowedExtensions: ['.txt'] as const,
  encoding: 'utf-8',
  sampleGroupsCount: 5,
  vkBaseUrl: 'https://vk.com'
};

export class FileParser {
  private config: FileParserConfig;
  private logger: Logger;
  private lineParser: GroupLineParser;

  constructor(
    config: Partial<FileParserConfig> = {},
    logger: Logger = defaultLogger,
    lineParser?: GroupLineParser
  ) {
    this.config = { ...defaultConfig, ...config };
    this.logger = logger;
    this.lineParser = lineParser || new GroupLineParser();
  }

  async parseGroupsFile(
    filePath: string,
    encoding?: BufferEncoding
  ): Promise<FileParseResult> {
    const fileEncoding = encoding || this.config.encoding;

    try {
      const content = await fs.promises.readFile(filePath, fileEncoding);
      const lines = content.split('\n');

      // ... логика парсинга с использованием this.lineParser и this.logger
    } catch (error) {
      this.logger.error('Failed to parse file', error, { filePath });
      throw error;
    }
  }

  // ... остальные методы как instance методы
}

// FileParserFactory.ts
export class FileParserFactory {
  static create(config?: Partial<FileParserConfig>): FileParser {
    return new FileParser(config);
  }

  static createForTesting(
    config?: Partial<FileParserConfig>,
    mockLogger?: Logger,
    mockLineParser?: GroupLineParser
  ): FileParser {
    return new FileParser(config, mockLogger, mockLineParser);
  }
}
```

**Преимущества**:
- Легко мокать зависимости в тестах
- Гибкая конфигурация
- Изолированные unit-тесты

**Оценка времени**: 3-4 часа

---

#### 1.4. Backward Compatibility Wrapper ✅
**Проблема**: Существующий код использует статические методы

**Решение**: Deprecated wrapper для старого API

```typescript
// fileParser.ts (старый файл - compatibility layer)
import { FileParser as NewFileParser, FileParserFactory } from './fileParser/FileParser';
import { FileParseResult, ValidationResult } from '@/types/common';

/**
 * @deprecated Используйте FileParserFactory.create() вместо статических методов
 * Этот класс сохранен для обратной совместимости и будет удален в v2.0.0
 */
class FileParser {
  private static instance = FileParserFactory.create();

  /**
   * @deprecated Use FileParserFactory.create().parseGroupsFile()
   */
  static async parseGroupsFile(
    filePath: string,
    encoding: BufferEncoding = 'utf-8'
  ): Promise<FileParseResult> {
    return FileParser.instance.parseGroupsFile(filePath, encoding);
  }

  /**
   * @deprecated Use FileParserFactory.create().validateFile()
   */
  static async validateFile(filePath: string): Promise<ValidationResult> {
    return FileParser.instance.validateFile(filePath);
  }

  // ... остальные методы с @deprecated
}

export default FileParser;

// Экспортируем новый API тоже
export { FileParserFactory, NewFileParser as FileParserClass };
```

**Преимущества**:
- Существующий код продолжает работать
- Мягкая миграция на новый API
- Четкие deprecation warnings

**Оценка времени**: 2-3 часа

---

#### 1.5. Unit-тесты для стратегий парсинга ✅
**Цель**: Тестовое покрытие ≥80%

```typescript
// tests/unit/fileParser/strategies/UrlClubStrategy.test.ts
import { UrlClubStrategy } from '@/utils/fileParser/strategies/UrlClubStrategy';

describe('UrlClubStrategy', () => {
  let strategy: UrlClubStrategy;

  beforeEach(() => {
    strategy = new UrlClubStrategy();
  });

  describe('canParse()', () => {
    it('should return true for valid club URL', () => {
      expect(strategy.canParse('https://vk.com/club123')).toBe(true);
      expect(strategy.canParse('https://VK.COM/CLUB456')).toBe(true);
    });

    it('should return false for screen_name URL', () => {
      expect(strategy.canParse('https://vk.com/durov')).toBe(false);
    });

    it('should return false for invalid format', () => {
      expect(strategy.canParse('123')).toBe(false);
      expect(strategy.canParse('club123')).toBe(false);
    });
  });

  describe('parse()', () => {
    it('should extract group ID from club URL', () => {
      const result = strategy.parse('https://vk.com/club123');
      expect(result).toEqual({ id: 123, name: null });
    });

    it('should return null for invalid club URL', () => {
      const result = strategy.parse('https://vk.com/club0');
      expect(result).toBeNull();
    });
  });
});

// Аналогичные тесты для остальных 4 стратегий
```

**Тесты для**:
- ✅ UrlClubStrategy
- ✅ UrlScreenNameStrategy
- ✅ NegativeIdStrategy
- ✅ PositiveIdStrategy
- ✅ ScreenNameStrategy
- ✅ GroupLineParser (integration)
- ✅ FileParser (с моками)

**Оценка времени**: 6-8 часов

---

**Итого Фаза 1**: 17-24 часа (~3 дня)

---

### Фаза 2: Улучшения качества кода (Should Have)
**Цель**: Типизация, метаданные, оптимизация

#### 2.1. Строгая типизация и метаданные ✅

**Обновить типы** в `@/types/common.ts`:

```typescript
// Расширяем ParseError
export interface ParseError {
  line: number;
  content: string;
  error: string;
  expectedFormat?: string;
  groupId?: number;
  strategyName?: string; // Какая стратегия пыталась парсить
}

// Расширяем FileParseResult с метаданными
export interface FileParseResult {
  groups: ProcessedGroup[];
  errors: string[]; // Оставляем для совместимости
  totalProcessed: number;
  metadata?: {
    parseTimeMs: number;
    successRate: number;
    duplicatesFound: number;
    emptyLinesSkipped: number;
    strategiesUsed: Record<string, number>; // Сколько раз каждая стратегия сработала
  };
}
```

**Оценка времени**: 2-3 часа

---

#### 2.2. Метрики производительности ✅

```typescript
// FileParser.ts
export class FileParser {
  private metrics = {
    startTime: 0,
    strategiesUsed: new Map<string, number>()
  };

  async parseGroupsFile(filePath: string): Promise<FileParseResult> {
    this.metrics.startTime = Date.now();
    this.metrics.strategiesUsed.clear();

    // ... парсинг

    const parseTimeMs = Date.now() - this.metrics.startTime;

    this.logger.info('File parsing completed', {
      parseTimeMs,
      throughput: `${(totalLines / (parseTimeMs / 1000)).toFixed(2)} lines/sec`,
      successRate: `${((groups.length / totalLines) * 100).toFixed(2)}%`,
      strategiesUsed: Object.fromEntries(this.metrics.strategiesUsed)
    });

    return {
      groups,
      errors,
      totalProcessed: totalLines,
      metadata: {
        parseTimeMs,
        successRate: groups.length / totalLines,
        duplicatesFound: duplicateCount,
        emptyLinesSkipped: emptyLineCount,
        strategiesUsed: Object.fromEntries(this.metrics.strategiesUsed)
      }
    };
  }

  // В GroupLineParser.parse() учитываем какая стратегия сработала
  private trackStrategyUsage(strategyName: string): void {
    const current = this.metrics.strategiesUsed.get(strategyName) || 0;
    this.metrics.strategiesUsed.set(strategyName, current + 1);
  }
}
```

**Преимущества**:
- Видим производительность парсинга
- Понимаем какие форматы наиболее популярны
- Данные для оптимизации

**Оценка времени**: 2-3 часа

---

#### 2.3. Документация и примеры ✅

**Создать**: `backend/src/utils/fileParser/README.md`

```markdown
# FileParser - Парсер файлов с VK группами

## Использование

### Базовое использование (новый API)
\`\`\`typescript
import { FileParserFactory } from '@/utils/fileParser';

const parser = FileParserFactory.create();
const result = await parser.parseGroupsFile('./groups.txt');

console.log(`Parsed ${result.groups.length} groups`);
console.log(`Errors: ${result.errors.length}`);
\`\`\`

### С кастомной конфигурацией
\`\`\`typescript
const parser = FileParserFactory.create({
  maxFileSizeMb: 20,
  encoding: 'windows-1251',
  sampleGroupsCount: 10
});
\`\`\`

### С кастомной стратегией парсинга
\`\`\`typescript
import { GroupParsingStrategy } from '@/utils/fileParser/strategies';

class CustomFormat implements GroupParsingStrategy {
  name = 'custom';
  priority = 0;
  description = '@username';

  canParse(line: string): boolean {
    return line.startsWith('@');
  }

  parse(line: string) {
    return { id: null, name: line.slice(1) };
  }
}

const parser = FileParserFactory.create();
const lineParser = parser.getLineParser();
lineParser.addStrategy(new CustomFormat());
\`\`\`

### Миграция со старого API
\`\`\`typescript
// Старый API (deprecated, но работает)
import FileParser from '@/utils/fileParser';
const result = await FileParser.parseGroupsFile('./groups.txt');

// Новый API (рекомендуется)
import { FileParserFactory } from '@/utils/fileParser';
const parser = FileParserFactory.create();
const result = await parser.parseGroupsFile('./groups.txt');
\`\`\`

## Поддерживаемые форматы

| Формат | Пример | Приоритет |
|--------|--------|-----------|
| Club URL | `https://vk.com/club123` | 1 |
| Screen name URL | `https://vk.com/durov` | 2 |
| Negative ID | `-123` | 3 |
| Positive ID | `123` | 4 |
| Screen name | `durov` or `club123` | 5 |

## Тестирование

\`\`\`bash
npm test fileParser
\`\`\`
```

**Оценка времени**: 2-3 часа

---

**Итого Фаза 2**: 6-9 часов (~1 день)

---

## 📁 Итоговая структура

```
backend/src/utils/
├── fileParser/
│   ├── index.ts                      # Главный экспорт
│   ├── FileParser.ts                 # Основной класс
│   ├── FileParserFactory.ts          # Фабрика
│   ├── GroupLineParser.ts            # Парсер строк
│   ├── strategies/
│   │   ├── GroupParsingStrategy.ts   # Интерфейс
│   │   ├── UrlClubStrategy.ts
│   │   ├── UrlScreenNameStrategy.ts
│   │   ├── NegativeIdStrategy.ts
│   │   ├── PositiveIdStrategy.ts
│   │   └── ScreenNameStrategy.ts
│   ├── constants.ts                  # Константы
│   └── README.md                     # Документация
├── fileParser.ts                     # Backward compatibility wrapper (deprecated)
├── logger.ts                         # ✅ Используем как есть
├── errors.ts                         # ✅ Используем как есть (интегрируем с ValidationError)
├── vkValidator.ts                    # ✅ Используем как есть
└── dbMonitor.ts                      # ✅ Не связан с fileParser

backend/tests/unit/fileParser/
├── strategies/
│   ├── UrlClubStrategy.test.ts
│   ├── UrlScreenNameStrategy.test.ts
│   ├── NegativeIdStrategy.test.ts
│   ├── PositiveIdStrategy.test.ts
│   └── ScreenNameStrategy.test.ts
├── GroupLineParser.test.ts
└── FileParser.test.ts
```

---

## 🔗 Интеграция с существующими утилитами

### ✅ logger.ts
```typescript
import logger from '@/utils/logger';

// FileParser использует существующий logger
class FileParser {
  constructor(private logger: Logger = logger) {}
}
```

### ✅ errors.ts
```typescript
import { ValidationError } from '@/utils/errors';

// Заменяем GroupParseError на ValidationError
throw new ValidationError('Invalid group format')
  .addFieldError('line', message, value);
```

### ✅ vkValidator.ts
```typescript
// vkValidator работает с результатами fileParser
const parseResult = await fileParser.parseGroupsFile('./groups.txt');
const validationResult = await vkValidator.validateGroups(parseResult.groups);
```

### ✅ dbMonitor.ts
Не требует интеграции с fileParser (независимая утилита для мониторинга БД)

---

## 📋 Чеклист выполнения

### Фаза 1: Критичные улучшения
- [ ] Удалить `GroupParseError`, использовать `ValidationError` из errors.ts
- [ ] Создать интерфейс `GroupParsingStrategy`
- [ ] Реализовать 5 стратегий парсинга
- [ ] Создать `GroupLineParser` с поддержкой стратегий
- [ ] Рефакторить `FileParser` с DI (constructor injection)
- [ ] Создать `FileParserFactory`
- [ ] Backward compatibility wrapper (fileParser.ts с @deprecated)
- [ ] Unit-тесты для всех стратегий (coverage ≥80%)
- [ ] Unit-тесты для `GroupLineParser`
- [ ] Integration тесты для `FileParser`
- [ ] Обновить импорты в коде, который использует fileParser

### Фаза 2: Улучшения качества
- [ ] Расширить типы с метаданными (ParseError, FileParseResult)
- [ ] Добавить метрики производительности
- [ ] Структурированное логирование с использованием logger
- [ ] Создать README.md с примерами
- [ ] Обновить JSDoc документацию

### Финализация
- [ ] Запустить все тесты: `npm test`
- [ ] Проверить TypeScript компиляцию: `npx tsc --noEmit`
- [ ] Проверить ESLint: `npx eslint backend/src/utils/fileParser`
- [ ] Code review
- [ ] Коммит изменений

---

## 🎯 Ключевые отличия от предыдущего плана

### ❌ Убрано (избыточная инженерия)
1. **FileReader, GroupUrlBuilder, DuplicateChecker** — не нужны отдельные классы
2. **FileParserLogger** — используем существующий logger.ts
3. **Hierarchy ошибок (FileParserError, FileValidationError)** — используем ValidationError
4. **Stream-based parser, Batch parser** — преждевременная оптимизация
5. **FileParserConfigBuilder** — достаточно partial config в конструкторе
6. **Result type** — не нужен для TypeScript с try/catch

### ✅ Добавлено (практичные улучшения)
1. **Интеграция с errors.ts** — единообразие в проекте
2. **Интеграция с logger.ts** — используем существующую инфраструктуру
3. **Упрощенная структура** — только Strategy pattern + DI
4. **Реалистичные оценки** — 23-33 часа вместо 55-76 часов

---

## ⏱ Оценка времени

### Детальная разбивка

| Задача | Фаза | Оценка |
|--------|------|--------|
| Интеграция с ValidationError | 1 | 2-3 ч |
| Strategy pattern + 5 стратегий | 1 | 4-6 ч |
| Dependency Injection | 1 | 3-4 ч |
| Backward compatibility | 1 | 2-3 ч |
| Unit-тесты (5 стратегий + parser) | 1 | 6-8 ч |
| **Итого Фаза 1** | | **17-24 ч** |
| Типизация и метаданные | 2 | 2-3 ч |
| Метрики производительности | 2 | 2-3 ч |
| Документация и примеры | 2 | 2-3 ч |
| **Итого Фаза 2** | | **6-9 ч** |
| **ВСЕГО** | | **23-33 ч (~3-4 дня)** |

---

## 🚀 Метрики успеха

### Качество кода
- ✅ Test coverage ≥ 80%
- ✅ Все публичные методы имеют JSDoc
- ✅ TypeScript strict mode без ошибок
- ✅ ESLint без предупреждений
- ✅ Интеграция с существующими utils (logger, errors)

### Архитектура
- ✅ Strategy pattern для расширяемости
- ✅ Dependency Injection для тестируемости
- ✅ Backward compatibility сохранена
- ✅ Единообразие с остальным кодом проекта

### Производительность
- ✅ Парсинг 10MB файла < 5 секунд
- ✅ Метрики для мониторинга

---

## 🎓 Выводы

### Что было переосмыслено
1. **Не создавать новые utils** если есть существующие (logger, errors)
2. **Не переусложнять** — Strategy pattern достаточно для гибкости
3. **Фокус на интеграции** с существующей архитектурой проекта
4. **Реалистичные оценки** времени на основе практики

### Преимущества упрощенного подхода
1. **Меньше кода** — проще поддерживать
2. **Быстрее реализовать** — 23-33ч вместо 55-76ч
3. **Лучшая интеграция** с существующим кодом
4. **Такая же расширяемость** благодаря Strategy pattern

---

**Автор плана**: Claude Code
**Дата**: 2025-09-30
**Версия**: 2.0 (Упрощенная и интегрированная)