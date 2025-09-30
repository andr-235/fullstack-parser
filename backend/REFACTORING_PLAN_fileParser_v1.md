# План рефакторинга fileParser.ts

## Дата создания: 2025-09-30

## 1. Анализ текущей архитектуры

### Текущая структура
- **Класс**: `FileParser` - статический класс с 14 методами
- **Размер файла**: ~440 строк кода
- **Ответственность**: Парсинг TXT-файлов с данными групп VK
- **Паттерны**: Single Responsibility для отдельных методов
- **Зависимости**: fs, logger, types

### Положительные стороны
✅ Хорошая модульность методов парсинга
✅ Подробная документация JSDoc
✅ Кастомная ошибка `GroupParseError`
✅ Использование констант вместо магических чисел
✅ Детальное логирование процесса
✅ Валидация файлов перед парсингом
✅ Обработка множества форматов входных данных

### Проблемные зоны
❌ Слишком большой класс (нарушение SRP на уровне класса)
❌ Все методы статические - затрудняет тестирование и расширение
❌ Смешение ответственностей: парсинг + валидация + построение URL + логирование
❌ Дублирование логики проверки форматов
❌ Отсутствие стратегии парсинга (hardcoded последовательность проверок)
❌ Недостаточная типизация (использование `any` в логере)
❌ Отсутствие unit-тестов для отдельных методов парсинга

---

## 2. Предложения по рефакторингу

### 2.1. Разделение ответственностей (КРИТИЧНО)

#### Проблема
Класс `FileParser` делает слишком много:
- Читает файлы
- Валидирует файлы
- Парсит строки
- Проверяет дубликаты
- Строит URL
- Логирует результаты

#### Решение
Разделить на несколько специализированных классов:

```typescript
// 1. FileReader - чтение и валидация файлов
class FileReader {
  async readFile(filePath: string, encoding: BufferEncoding): Promise<string>
  async validateFile(filePath: string): Promise<ValidationResult>
  async isFileAccessible(filePath: string): Promise<boolean>
  async getFileStats(filePath: string): Promise<fs.Stats | null>
}

// 2. GroupLineParser - парсинг отдельных строк
class GroupLineParser {
  parse(line: string, lineNumber: number): ParsedGroup
  // Приватные методы для разных форматов
}

// 3. GroupUrlBuilder - построение URL групп
class GroupUrlBuilder {
  build(id: number | null, name: string | null): string
  cleanGroupName(name: string | null): string
}

// 4. DuplicateChecker - проверка дубликатов
class DuplicateChecker {
  check(id: number | null): boolean
  add(id: number): void
  reset(): void
}

// 5. FileParser - главный оркестратор
class FileParser {
  constructor(
    private reader: FileReader,
    private lineParser: GroupLineParser,
    private urlBuilder: GroupUrlBuilder,
    private duplicateChecker: DuplicateChecker,
    private logger: Logger
  )

  async parseGroupsFile(filePath: string): Promise<FileParseResult>
}
```

**Преимущества:**
- Каждый класс имеет единственную ответственность
- Легче тестировать изолированно
- Проще заменять/расширять отдельные компоненты
- Возможность внедрения зависимостей (Dependency Injection)

---

### 2.2. Паттерн Strategy для парсинга (КРИТИЧНО)

#### Проблема
Методы `parseGroupLine()` имеет hardcoded последовательность проверок:
```typescript
parseUrlClub() -> parseUrlScreenName() -> parseNegativeId() ->
parsePositiveId() -> parseScreenName()
```

Это негибко и трудно расширяемо.

#### Решение
Использовать паттерн Strategy с цепочкой парсеров:

```typescript
// Базовый интерфейс стратегии
interface GroupParsingStrategy {
  canParse(line: string): boolean;
  parse(line: string): Omit<ParsedGroup, 'lineNumber'> | null;
  readonly priority: number;
  readonly formatDescription: string;
}

// Конкретные стратегии
class UrlClubStrategy implements GroupParsingStrategy {
  priority = 1;
  formatDescription = 'https://vk.com/club<ID>';

  canParse(line: string): boolean {
    return /^https:\/\/vk\.com\/club\d+$/i.test(line);
  }

  parse(line: string): Omit<ParsedGroup, 'lineNumber'> | null {
    const match = line.match(/^https:\/\/vk\.com\/club(\d+)$/i);
    if (match) {
      const groupId = parseInt(match[1], 10);
      if (!isNaN(groupId) && groupId > 0) {
        return { id: groupId, name: null };
      }
    }
    return null;
  }
}

class UrlScreenNameStrategy implements GroupParsingStrategy {
  priority = 2;
  formatDescription = 'https://vk.com/<screen_name>';
  // ... реализация
}

class NegativeIdStrategy implements GroupParsingStrategy {
  priority = 3;
  formatDescription = '-<ID>';
  // ... реализация
}

class PositiveIdStrategy implements GroupParsingStrategy {
  priority = 4;
  formatDescription = '<ID>';
  // ... реализация
}

class ScreenNameStrategy implements GroupParsingStrategy {
  priority = 5;
  formatDescription = '<screen_name> or club<ID>';
  // ... реализация
}

// Парсер с использованием стратегий
class GroupLineParser {
  private strategies: GroupParsingStrategy[];

  constructor(strategies?: GroupParsingStrategy[]) {
    this.strategies = strategies || [
      new UrlClubStrategy(),
      new UrlScreenNameStrategy(),
      new NegativeIdStrategy(),
      new PositiveIdStrategy(),
      new ScreenNameStrategy()
    ];

    // Сортируем по приоритету
    this.strategies.sort((a, b) => a.priority - b.priority);
  }

  parse(line: string, lineNumber: number): ParsedGroup {
    for (const strategy of this.strategies) {
      if (strategy.canParse(line)) {
        const result = strategy.parse(line);
        if (result) {
          return { ...result, lineNumber };
        }
      }
    }

    throw new GroupParseError({
      line: lineNumber,
      content: line,
      error: 'Invalid group format',
      expectedFormat: this.strategies.map(s => s.formatDescription).join(', ')
    });
  }

  // Возможность добавить кастомную стратегию
  addStrategy(strategy: GroupParsingStrategy): void {
    this.strategies.push(strategy);
    this.strategies.sort((a, b) => a.priority - b.priority);
  }
}
```

**Преимущества:**
- Легко добавлять новые форматы парсинга
- Каждая стратегия тестируется отдельно
- Можно менять приоритет парсинга
- Явная документация поддерживаемых форматов

---

### 2.3. Улучшение типизации TypeScript (ВАЖНО)

#### Проблема
- Использование `any` в параметрах logger.info/error
- Нет строгой типизации для результатов парсинга
- Отсутствие enum для типов ошибок

#### Решение

```typescript
// 1. Строгая типизация логов
interface LogMetadata {
  filePath?: string;
  totalLines?: number;
  validGroups?: number;
  errors?: number;
  sample?: Array<{ id: number | null; name: string; url: string }>;
  error?: string;
}

// 2. Enum для типов ошибок парсинга
enum ParseErrorType {
  INVALID_FORMAT = 'INVALID_FORMAT',
  DUPLICATE_ID = 'DUPLICATE_ID',
  INVALID_URL = 'INVALID_URL',
  EMPTY_LINE = 'EMPTY_LINE',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  INVALID_EXTENSION = 'INVALID_EXTENSION',
  FILE_NOT_ACCESSIBLE = 'FILE_NOT_ACCESSIBLE'
}

// 3. Расширенный ParseError с типом
interface ParseError {
  type: ParseErrorType;
  line: number;
  content: string;
  error: string;
  expectedFormat?: string;
  groupId?: number;
  metadata?: Record<string, unknown>;
}

// 4. Результат с метаданными
interface FileParseResult {
  groups: ProcessedGroup[];
  errors: ParseError[]; // Не string[], а ParseError[]
  totalProcessed: number;
  metadata: {
    successRate: number; // процент успешно обработанных строк
    duplicatesFound: number;
    emptyLinesSkipped: number;
    parseTimeMs: number;
  };
}

// 5. Типизация конфигурации парсера
interface FileParserConfig {
  maxFileSizeMb: number;
  allowedExtensions: readonly string[];
  encoding: BufferEncoding;
  sampleGroupsCount: number;
  vkBaseUrl: string;
  clubPrefix: string;
}
```

**Преимущества:**
- Полная type-safety
- Автодополнение в IDE
- Ошибки компиляции вместо runtime
- Легче рефакторить

---

### 2.4. Обработка ошибок (ВАЖНО)

#### Проблема
- Смешение разных типов ошибок в одном массиве `errors: string[]`
- Недостаточно информации для отладки
- Нет разделения критичных и некритичных ошибок

#### Решение

```typescript
// 1. Иерархия ошибок
class FileParserError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'FileParserError';
  }
}

class FileValidationError extends FileParserError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 'FILE_VALIDATION_ERROR', details);
    this.name = 'FileValidationError';
  }
}

class GroupParseError extends FileParserError {
  constructor(public readonly parseError: ParseError) {
    super(parseError.error, 'GROUP_PARSE_ERROR', { parseError });
    this.name = 'GroupParseError';
  }
}

// 2. Result type для безопасной обработки
type ParseResult<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

class GroupLineParser {
  parseSafe(line: string, lineNumber: number): ParseResult<ParsedGroup, ParseError> {
    try {
      const result = this.parse(line, lineNumber);
      return { success: true, data: result };
    } catch (error) {
      if (error instanceof GroupParseError) {
        return { success: false, error: error.parseError };
      }
      return {
        success: false,
        error: {
          type: ParseErrorType.INVALID_FORMAT,
          line: lineNumber,
          content: line,
          error: error instanceof Error ? error.message : String(error)
        }
      };
    }
  }
}

// 3. Разделение ошибок по уровням
interface FileParseResult {
  groups: ProcessedGroup[];
  errors: {
    critical: ParseError[]; // Ошибки файла/валидации
    warnings: ParseError[]; // Проблемы парсинга строк
  };
  totalProcessed: number;
  metadata: ParseMetadata;
}
```

**Преимущества:**
- Четкое разделение типов ошибок
- Легче обрабатывать разные ситуации
- Больше контекста для отладки
- Type-safe error handling

---

### 2.5. Оптимизация производительности (ЖЕЛАТЕЛЬНО)

#### Проблема
- Обработка файла построчно в синхронном цикле
- Все строки загружаются в память сразу
- Для больших файлов (близко к 10MB) может быть медленно

#### Решение

```typescript
// 1. Stream-based парсинг для больших файлов
import { createReadStream } from 'fs';
import { createInterface } from 'readline';

class StreamFileParser {
  async parseGroupsFileStream(
    filePath: string,
    onProgress?: (progress: number) => void
  ): Promise<FileParseResult> {
    const fileStream = createReadStream(filePath, { encoding: 'utf-8' });
    const rl = createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    const groups: ProcessedGroup[] = [];
    const errors: ParseError[] = [];
    const duplicateChecker = new DuplicateChecker();
    let lineNumber = 0;
    let totalLines = 0;

    // Получаем размер файла для прогресса
    const stats = await fs.promises.stat(filePath);
    const fileSize = stats.size;
    let processedBytes = 0;

    for await (const line of rl) {
      lineNumber++;
      totalLines++;
      processedBytes += Buffer.byteLength(line, 'utf-8');

      // Вызываем callback прогресса
      if (onProgress && lineNumber % 100 === 0) {
        const progress = Math.min((processedBytes / fileSize) * 100, 100);
        onProgress(progress);
      }

      // Парсим строку
      const cleanLine = this.cleanLine(line, lineNumber, errors);
      if (!cleanLine) continue;

      const parseResult = this.lineParser.parseSafe(cleanLine, lineNumber);
      if (parseResult.success) {
        // ... обработка результата
      } else {
        errors.push(parseResult.error);
      }
    }

    return { groups, errors, totalProcessed: totalLines, metadata: {...} };
  }
}

// 2. Батчевая обработка для параллелизации
class BatchFileParser {
  async parseGroupsFileBatch(
    filePath: string,
    batchSize: number = 1000
  ): Promise<FileParseResult> {
    const content = await fs.promises.readFile(filePath, 'utf-8');
    const lines = content.split('\n');

    const batches: string[][] = [];
    for (let i = 0; i < lines.length; i += batchSize) {
      batches.push(lines.slice(i, i + batchSize));
    }

    // Обрабатываем батчи параллельно
    const results = await Promise.all(
      batches.map((batch, batchIndex) =>
        this.processBatch(batch, batchIndex * batchSize)
      )
    );

    // Объединяем результаты
    return this.mergeResults(results);
  }

  private async processBatch(
    lines: string[],
    startLine: number
  ): Promise<Partial<FileParseResult>> {
    // ... обработка батча
  }
}
```

**Преимущества:**
- Меньше использование памяти
- Возможность отображать прогресс
- Параллельная обработка батчей
- Подходит для файлов любого размера

---

### 2.6. Расширяемость конфигурации (ЖЕЛАТЕЛЬНО)

#### Проблема
- Константы hardcoded в коде
- Нельзя изменить поведение без редактирования кода

#### Решение

```typescript
// 1. Конфигурация через объект
interface FileParserConfig {
  validation: {
    maxFileSizeMb: number;
    allowedExtensions: string[];
  };
  parsing: {
    encoding: BufferEncoding;
    skipEmptyLines: boolean;
    skipComments: boolean;
    commentPrefix: string;
  };
  output: {
    sampleGroupsCount: number;
    includeMetadata: boolean;
  };
  vk: {
    baseUrl: string;
    clubPrefix: string;
    formats: ParsingStrategy[]; // Кастомные стратегии
  };
}

// 2. Builder для конфигурации
class FileParserConfigBuilder {
  private config: Partial<FileParserConfig> = {};

  withMaxFileSize(sizeMb: number): this {
    this.config.validation = {
      ...this.config.validation,
      maxFileSizeMb: sizeMb
    };
    return this;
  }

  withEncoding(encoding: BufferEncoding): this {
    this.config.parsing = {
      ...this.config.parsing,
      encoding
    };
    return this;
  }

  addCustomFormat(strategy: ParsingStrategy): this {
    if (!this.config.vk) {
      this.config.vk = { ...defaultVkConfig };
    }
    this.config.vk.formats.push(strategy);
    return this;
  }

  build(): FileParserConfig {
    return {
      ...defaultConfig,
      ...this.config
    };
  }
}

// 3. Использование
const config = new FileParserConfigBuilder()
  .withMaxFileSize(20)
  .withEncoding('utf-8')
  .addCustomFormat(new CustomVkGroupFormat())
  .build();

const parser = new FileParser(config);
const result = await parser.parseGroupsFile('./groups.txt');
```

**Преимущества:**
- Гибкая конфигурация
- Легко добавлять новые опции
- Удобный API для настройки

---

### 2.7. Тестируемость (КРИТИЧНО)

#### Проблема
- Статические методы - сложно мокать
- Зависимости от fs и logger встроены напрямую
- Нет тестов

#### Решение

```typescript
// 1. Внедрение зависимостей через конструктор
class FileParser {
  constructor(
    private readonly config: FileParserConfig,
    private readonly fileReader: FileReader,
    private readonly lineParser: GroupLineParser,
    private readonly urlBuilder: GroupUrlBuilder,
    private readonly logger: Logger
  ) {}

  async parseGroupsFile(filePath: string): Promise<FileParseResult> {
    // Использование this.fileReader, this.logger и т.д.
  }
}

// 2. Интерфейсы для зависимостей
interface IFileReader {
  readFile(path: string, encoding: BufferEncoding): Promise<string>;
  validateFile(path: string): Promise<ValidationResult>;
}

interface ILogger {
  info(message: string, meta?: LogMetadata): void;
  error(message: string, meta?: LogMetadata): void;
}

// 3. Фабрика для создания FileParser
class FileParserFactory {
  static create(config?: Partial<FileParserConfig>): FileParser {
    const fullConfig = { ...defaultConfig, ...config };

    return new FileParser(
      fullConfig,
      new FileReader(fullConfig.validation),
      new GroupLineParser(fullConfig.vk.formats),
      new GroupUrlBuilder(fullConfig.vk),
      logger // Winston logger
    );
  }

  static createForTesting(
    mocks: {
      fileReader?: IFileReader;
      lineParser?: GroupLineParser;
      logger?: ILogger;
    }
  ): FileParser {
    return new FileParser(
      defaultConfig,
      mocks.fileReader || new FileReader(defaultConfig.validation),
      mocks.lineParser || new GroupLineParser([]),
      new GroupUrlBuilder(defaultConfig.vk),
      mocks.logger || logger
    );
  }
}

// 4. Пример unit-теста
describe('GroupLineParser', () => {
  let parser: GroupLineParser;

  beforeEach(() => {
    parser = new GroupLineParser([
      new UrlClubStrategy(),
      new NegativeIdStrategy(),
      new PositiveIdStrategy()
    ]);
  });

  describe('parse()', () => {
    it('should parse club URL format', () => {
      const result = parser.parse('https://vk.com/club123', 1);

      expect(result).toEqual({
        id: 123,
        name: null,
        lineNumber: 1
      });
    });

    it('should parse negative ID', () => {
      const result = parser.parse('-456', 2);

      expect(result).toEqual({
        id: 456,
        name: null,
        lineNumber: 2
      });
    });

    it('should throw GroupParseError for invalid format', () => {
      expect(() => parser.parse('invalid!!!', 3))
        .toThrow(GroupParseError);
    });
  });
});

// 5. Пример integration теста
describe('FileParser integration', () => {
  let parser: FileParser;
  let mockFileReader: jest.Mocked<IFileReader>;
  let mockLogger: jest.Mocked<ILogger>;

  beforeEach(() => {
    mockFileReader = {
      readFile: jest.fn(),
      validateFile: jest.fn()
    };

    mockLogger = {
      info: jest.fn(),
      error: jest.fn()
    };

    parser = FileParserFactory.createForTesting({
      fileReader: mockFileReader,
      logger: mockLogger
    });
  });

  it('should parse valid groups file', async () => {
    mockFileReader.readFile.mockResolvedValue(
      'https://vk.com/club123\n-456\ndurov'
    );

    const result = await parser.parseGroupsFile('test.txt');

    expect(result.groups).toHaveLength(3);
    expect(result.errors).toHaveLength(0);
    expect(mockLogger.info).toHaveBeenCalled();
  });
});
```

**Преимущества:**
- Легко писать unit-тесты
- Можно мокать зависимости
- Изоляция тестов
- Быстрое выполнение тестов

---

### 2.8. Логирование и мониторинг (ЖЕЛАТЕЛЬНО)

#### Проблема
- Логирование разбросано по коду
- Нет структурированного подхода к метрикам
- Сложно отследить производительность

#### Решение

```typescript
// 1. Dedicated logging service
interface ParsingMetrics {
  startTime: number;
  endTime?: number;
  duration?: number;
  linesProcessed: number;
  linesPerSecond?: number;
  successRate: number;
  errorsByType: Record<ParseErrorType, number>;
}

class FileParserLogger {
  constructor(private logger: ILogger) {}

  logParsingStart(filePath: string, config: FileParserConfig): void {
    this.logger.info('Starting file parsing', {
      filePath,
      config: {
        maxFileSizeMb: config.validation.maxFileSizeMb,
        encoding: config.parsing.encoding
      }
    });
  }

  logParsingComplete(metrics: ParsingMetrics): void {
    this.logger.info('File parsing completed', {
      duration: `${metrics.duration}ms`,
      totalLines: metrics.linesProcessed,
      throughput: `${metrics.linesPerSecond?.toFixed(2)} lines/sec`,
      successRate: `${(metrics.successRate * 100).toFixed(2)}%`,
      errorsByType: metrics.errorsByType
    });
  }

  logParsingError(error: Error, context: Record<string, unknown>): void {
    this.logger.error('File parsing failed', {
      error: error.message,
      stack: error.stack,
      ...context
    });
  }

  logSampleGroups(groups: ProcessedGroup[], limit: number): void {
    const sample = groups.slice(0, limit);
    this.logger.info(`Sample parsed groups (first ${limit})`, {
      sample: sample.map(g => ({
        id: g.id,
        name: g.name,
        url: g.url
      }))
    });
  }
}

// 2. Метрики в FileParser
class FileParser {
  private metrics: ParsingMetrics = {
    startTime: 0,
    linesProcessed: 0,
    successRate: 0,
    errorsByType: {}
  };

  async parseGroupsFile(filePath: string): Promise<FileParseResult> {
    this.metrics.startTime = Date.now();
    this.parserLogger.logParsingStart(filePath, this.config);

    try {
      // ... парсинг файла

      this.calculateMetrics(result);
      this.parserLogger.logParsingComplete(this.metrics);

      return result;
    } catch (error) {
      this.parserLogger.logParsingError(error as Error, { filePath });
      throw error;
    }
  }

  private calculateMetrics(result: FileParseResult): void {
    this.metrics.endTime = Date.now();
    this.metrics.duration = this.metrics.endTime - this.metrics.startTime;
    this.metrics.linesProcessed = result.totalProcessed;
    this.metrics.linesPerSecond =
      this.metrics.linesProcessed / (this.metrics.duration / 1000);
    this.metrics.successRate =
      result.groups.length / result.totalProcessed;

    // Группируем ошибки по типам
    for (const error of result.errors) {
      const type = error.type || ParseErrorType.INVALID_FORMAT;
      this.metrics.errorsByType[type] =
        (this.metrics.errorsByType[type] || 0) + 1;
    }
  }
}
```

**Преимущества:**
- Структурированное логирование
- Метрики производительности
- Легко отслеживать проблемы
- Полезно для оптимизации

---

## 3. Приоритезация изменений

### Фаза 1: Критические изменения (Must Have)
**Цель**: Улучшить архитектуру и тестируемость

1. ✅ **Разделение ответственностей**
   - Создать отдельные классы: FileReader, GroupLineParser, GroupUrlBuilder, DuplicateChecker
   - Рефакторить FileParser как оркестратор
   - Оценка: 8-12 часов

2. ✅ **Паттерн Strategy для парсинга**
   - Создать интерфейс GroupParsingStrategy
   - Реализовать 5 стратегий для разных форматов
   - Рефакторить GroupLineParser с использованием стратегий
   - Оценка: 6-8 часов

3. ✅ **Dependency Injection и тестируемость**
   - Заменить статические методы на instance методы
   - Создать интерфейсы для зависимостей
   - Реализовать FileParserFactory
   - Оценка: 4-6 часов

4. ✅ **Написать unit-тесты**
   - Тесты для всех парсинг-стратегий
   - Тесты для GroupLineParser
   - Тесты для FileParser с моками
   - Покрытие минимум 80%
   - Оценка: 10-12 часов

**Итого Фаза 1**: 28-38 часов (~4-5 дней)

---

### Фаза 2: Важные улучшения (Should Have)
**Цель**: Улучшить типизацию и обработку ошибок

1. ✅ **Строгая типизация TypeScript**
   - Создать enum ParseErrorType
   - Типизировать все интерфейсы с generic
   - Убрать использование any
   - Оценка: 3-4 часа

2. ✅ **Улучшенная обработка ошибок**
   - Иерархия кастомных ошибок
   - Result type для безопасной обработки
   - Разделение критичных/некритичных ошибок
   - Оценка: 4-6 часов

3. ✅ **Расширенное логирование**
   - Создать FileParserLogger
   - Добавить метрики производительности
   - Структурированное логирование
   - Оценка: 3-4 часа

**Итого Фаза 2**: 10-14 часов (~1.5-2 дня)

---

### Фаза 3: Желательные оптимизации (Nice to Have)
**Цель**: Оптимизировать производительность и расширяемость

1. ✅ **Stream-based парсинг**
   - Реализовать StreamFileParser
   - Поддержка callback прогресса
   - Тесты для больших файлов
   - Оценка: 6-8 часов

2. ✅ **Батчевая обработка**
   - Реализовать BatchFileParser
   - Параллельная обработка батчей
   - Оценка: 4-6 часов

3. ✅ **Гибкая конфигурация**
   - FileParserConfig с builder
   - Возможность добавлять кастомные стратегии
   - Оценка: 3-4 часа

4. ✅ **Документация и примеры**
   - JSDoc для всех публичных методов
   - README с примерами использования
   - Миграционный гайд от старого API
   - Оценка: 4-6 часов

**Итого Фаза 3**: 17-24 часа (~2-3 дня)

---

## 4. Итоговая структура проекта

```
backend/src/
├── utils/
│   ├── fileParser/
│   │   ├── index.ts                    // Главный экспорт
│   │   ├── FileParser.ts               // Оркестратор
│   │   ├── FileParserFactory.ts        // Фабрика
│   │   ├── FileReader.ts               // Чтение/валидация файлов
│   │   ├── GroupLineParser.ts          // Парсинг строк
│   │   ├── GroupUrlBuilder.ts          // Построение URL
│   │   ├── DuplicateChecker.ts         // Проверка дубликатов
│   │   ├── FileParserLogger.ts         // Логирование
│   │   ├── strategies/
│   │   │   ├── GroupParsingStrategy.ts // Базовый интерфейс
│   │   │   ├── UrlClubStrategy.ts
│   │   │   ├── UrlScreenNameStrategy.ts
│   │   │   ├── NegativeIdStrategy.ts
│   │   │   ├── PositiveIdStrategy.ts
│   │   │   └── ScreenNameStrategy.ts
│   │   ├── config/
│   │   │   ├── FileParserConfig.ts     // Интерфейсы конфига
│   │   │   ├── FileParserConfigBuilder.ts
│   │   │   └── defaultConfig.ts        // Дефолтные значения
│   │   ├── errors/
│   │   │   ├── FileParserError.ts
│   │   │   ├── FileValidationError.ts
│   │   │   └── GroupParseError.ts
│   │   └── types/
│   │       ├── ParseResult.ts
│   │       ├── ParsingMetrics.ts
│   │       └── interfaces.ts
│   └── fileParser.ts                   // Backward compatibility wrapper
├── types/
│   └── common.ts                       // Обновленные типы
└── tests/
    └── unit/
        └── fileParser/
            ├── FileParser.test.ts
            ├── GroupLineParser.test.ts
            ├── strategies/
            │   ├── UrlClubStrategy.test.ts
            │   ├── NegativeIdStrategy.test.ts
            │   └── ... (остальные стратегии)
            ├── FileReader.test.ts
            ├── GroupUrlBuilder.test.ts
            └── DuplicateChecker.test.ts
```

---

## 5. Backward Compatibility

Для сохранения совместимости с существующим кодом:

```typescript
// backend/src/utils/fileParser.ts
// Старый API (deprecated)
import { FileParserFactory } from './fileParser/FileParserFactory';
import { FileParseResult, ValidationResult } from '@/types/common';

/**
 * @deprecated Use FileParserFactory.create() instead
 * Этот класс оставлен для обратной совместимости и будет удален в v2.0.0
 */
class FileParser {
  /**
   * @deprecated Use FileParserFactory.create().parseGroupsFile() instead
   */
  static async parseGroupsFile(
    filePath: string,
    encoding: BufferEncoding = 'utf-8'
  ): Promise<FileParseResult> {
    const parser = FileParserFactory.create();
    return parser.parseGroupsFile(filePath, encoding);
  }

  /**
   * @deprecated Use FileParserFactory.create() with custom config instead
   */
  static async validateFile(filePath: string): Promise<ValidationResult> {
    const parser = FileParserFactory.create();
    return parser.validateFile(filePath);
  }

  // ... остальные статические методы с @deprecated
}

export default FileParser;
```

---

## 6. Миграционный путь для существующего кода

### До:
```typescript
import FileParser from '@/utils/fileParser';

const result = await FileParser.parseGroupsFile('./groups.txt');
```

### После (рекомендуется):
```typescript
import { FileParserFactory } from '@/utils/fileParser';

// Вариант 1: С дефолтной конфигурацией
const parser = FileParserFactory.create();
const result = await parser.parseGroupsFile('./groups.txt');

// Вариант 2: С кастомной конфигурацией
const config = new FileParserConfigBuilder()
  .withMaxFileSize(20)
  .withEncoding('utf-8')
  .build();

const parser = FileParserFactory.create(config);
const result = await parser.parseGroupsFile('./groups.txt');

// Вариант 3: С кастомными стратегиями парсинга
class CustomVkFormat implements GroupParsingStrategy {
  priority = 0;
  formatDescription = 'custom format';
  // ... реализация
}

const parser = FileParserFactory.create();
parser.addParsingStrategy(new CustomVkFormat());
const result = await parser.parseGroupsFile('./groups.txt');
```

---

## 7. Метрики успеха рефакторинга

После завершения рефакторинга проверяем:

### Качество кода
- ✅ Test coverage >= 80%
- ✅ Все методы имеют JSDoc документацию
- ✅ Нет использования `any` в типах
- ✅ ESLint проходит без ошибок
- ✅ TypeScript strict mode включен

### Архитектура
- ✅ Каждый класс имеет одну ответственность
- ✅ Зависимости инжектятся через конструктор
- ✅ Нет циклических зависимостей
- ✅ Легко добавлять новые форматы парсинга

### Производительность
- ✅ Парсинг 10MB файла < 5 секунд
- ✅ Memory usage не растет линейно с размером файла
- ✅ Поддержка прогресса для длительных операций

### Поддерживаемость
- ✅ Все публичные API задокументированы
- ✅ Есть примеры использования
- ✅ Обратная совместимость сохранена
- ✅ Migration guide написан

---

## 8. Риски и митигация

### Риск 1: Ломающие изменения для существующего кода
**Митигация**:
- Сохранить старый API с @deprecated
- Написать миграционный гайд
- Добавить runtime warnings при использовании deprecated API

### Риск 2: Снижение производительности из-за дополнительных абстракций
**Митигация**:
- Провести benchmarking до и после рефакторинга
- Использовать stream-based подход для больших файлов
- Оптимизировать критичные пути

### Риск 3: Увеличение сложности для простых use-cases
**Митигация**:
- FileParserFactory.create() с разумными дефолтами
- Сохранить простоту использования для типичных случаев
- Гибкость только там, где нужна

### Риск 4: Недостаточное покрытие тестами
**Митигация**:
- Написать тесты ДО рефакторинга текущего кода
- Использовать TDD для новых компонентов
- Добавить integration тесты

---

## 9. Чеклист выполнения

### Фаза 1: Критические изменения
- [ ] Создать структуру директорий
- [ ] Реализовать FileReader
- [ ] Реализовать GroupUrlBuilder
- [ ] Реализовать DuplicateChecker
- [ ] Создать интерфейс GroupParsingStrategy
- [ ] Реализовать 5 парсинг-стратегий
- [ ] Реализовать GroupLineParser с стратегиями
- [ ] Рефакторить FileParser как оркестратор
- [ ] Создать FileParserFactory
- [ ] Написать unit-тесты для всех компонентов
- [ ] Достичь 80%+ test coverage
- [ ] Обновить существующие integration тесты

### Фаза 2: Важные улучшения
- [ ] Создать enum ParseErrorType
- [ ] Добавить строгую типизацию
- [ ] Реализовать иерархию ошибок
- [ ] Добавить Result type
- [ ] Создать FileParserLogger
- [ ] Добавить метрики производительности
- [ ] Обновить тесты с новыми типами

### Фаза 3: Желательные оптимизации
- [ ] Реализовать StreamFileParser
- [ ] Реализовать BatchFileParser
- [ ] Создать FileParserConfig и Builder
- [ ] Добавить поддержку кастомных стратегий
- [ ] Написать JSDoc для всех публичных API
- [ ] Создать README с примерами
- [ ] Написать migration guide
- [ ] Провести benchmarking

### Финализация
- [ ] Добавить backward compatibility wrapper
- [ ] Обновить все импорты в проекте
- [ ] Запустить все тесты
- [ ] Проверить ESLint и TypeScript compilation
- [ ] Code review
- [ ] Обновить документацию проекта
- [ ] Коммит и пуш

---

## 10. Примеры использования после рефакторинга

### Базовое использование
```typescript
import { FileParserFactory } from '@/utils/fileParser';

const parser = FileParserFactory.create();
const result = await parser.parseGroupsFile('./groups.txt');

console.log(`Parsed ${result.groups.length} groups`);
console.log(`Errors: ${result.errors.length}`);
console.log(`Success rate: ${result.metadata.successRate}%`);
```

### С кастомной конфигурацией
```typescript
import { FileParserConfigBuilder } from '@/utils/fileParser/config';
import { FileParserFactory } from '@/utils/fileParser';

const config = new FileParserConfigBuilder()
  .withMaxFileSize(20)
  .withEncoding('windows-1251')
  .skipComments(false)
  .build();

const parser = FileParserFactory.create(config);
const result = await parser.parseGroupsFile('./groups.txt');
```

### С кастомной стратегией парсинга
```typescript
import {
  FileParserFactory,
  GroupParsingStrategy
} from '@/utils/fileParser';

// Кастомный формат: @username
class MentionFormatStrategy implements GroupParsingStrategy {
  priority = 0;
  formatDescription = '@username';

  canParse(line: string): boolean {
    return line.startsWith('@');
  }

  parse(line: string): { id: null; name: string } | null {
    if (this.canParse(line)) {
      return { id: null, name: line.slice(1) };
    }
    return null;
  }
}

const parser = FileParserFactory.create();
parser.addParsingStrategy(new MentionFormatStrategy());

const result = await parser.parseGroupsFile('./groups.txt');
```

### С отслеживанием прогресса
```typescript
import { StreamFileParser } from '@/utils/fileParser';

const parser = new StreamFileParser(config);

const result = await parser.parseGroupsFileStream(
  './large-groups.txt',
  (progress) => {
    console.log(`Progress: ${progress.toFixed(2)}%`);
  }
);
```

### В тестах с моками
```typescript
import { FileParserFactory } from '@/utils/fileParser';
import { MockFileReader } from '@/tests/mocks';

const mockFileReader = new MockFileReader();
mockFileReader.readFile.mockResolvedValue('club123\n-456');

const parser = FileParserFactory.createForTesting({
  fileReader: mockFileReader
});

const result = await parser.parseGroupsFile('test.txt');

expect(result.groups).toHaveLength(2);
```

---

## Заключение

Этот план рефакторинга предлагает поэтапное улучшение fileParser.ts с сохранением обратной совместимости. Основные преимущества:

1. **Лучшая архитектура**: SOLID принципы, разделение ответственностей
2. **Тестируемость**: Dependency Injection, легкое мокирование
3. **Расширяемость**: Strategy pattern, гибкая конфигурация
4. **Типобезопасность**: Строгая типизация TypeScript
5. **Производительность**: Stream-based парсинг, батчевая обработка
6. **Поддерживаемость**: Подробная документация, примеры, тесты

Рефакторинг можно выполнять поэтапно, начиная с критичных изменений (Фаза 1), которые дадут наибольшую ценность.

**Общая оценка времени**: 55-76 часов (~7-10 рабочих дней)

---

**Автор плана**: Claude Code
**Дата**: 2025-09-30
**Версия**: 1.0