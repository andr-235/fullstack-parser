import fs from 'fs';
import defaultLogger from '@/utils/logger';
import { Logger } from '@/types/common';
import { ValidationError } from '@/utils/errors';
import {
  FileParseResult,
  LegacyParsedGroup,
  ValidationResult
} from '@/types/common';
import { GroupLineParser } from './GroupLineParser';
import { FILE_PARSER_CONSTANTS } from './constants';

/**
 * Конфигурация для FileParser
 */
export interface FileParserConfig {
  /** Максимальный размер файла в MB */
  maxFileSizeMb: number;

  /** Разрешенные расширения файлов */
  allowedExtensions: readonly string[];

  /** Кодировка файла по умолчанию */
  encoding: BufferEncoding;

  /** Количество групп для примера в логах */
  sampleGroupsCount: number;

  /** Базовый URL VK */
  vkBaseUrl: string;
}

/**
 * Конфигурация по умолчанию
 */
export const defaultConfig: FileParserConfig = {
  maxFileSizeMb: FILE_PARSER_CONSTANTS.MAX_FILE_SIZE_MB,
  allowedExtensions: FILE_PARSER_CONSTANTS.ALLOWED_EXTENSIONS,
  encoding: FILE_PARSER_CONSTANTS.DEFAULT_ENCODING,
  sampleGroupsCount: FILE_PARSER_CONSTANTS.SAMPLE_GROUPS_COUNT,
  vkBaseUrl: FILE_PARSER_CONSTANTS.VK_BASE_URL
};

/**
 * Метаданные результата парсинга
 */
export interface FileParseMetadata {
  parseTimeMs: number;
  successRate: number;
  duplicatesFound: number;
  emptyLinesSkipped: number;
  strategiesUsed: Record<string, number>;
}

/**
 * Расширенный результат парсинга с метаданными
 */
export interface ExtendedFileParseResult extends FileParseResult {
  metadata?: FileParseMetadata;
}

/**
 * FileParser - парсер файлов с VK группами.
 * Использует Dependency Injection и паттерн Strategy для гибкости и тестируемости.
 */
export class FileParser {
  private config: FileParserConfig;
  private logger: Logger;
  private lineParser: GroupLineParser;
  private metrics: {
    startTime: number;
    strategiesUsed: Map<string, number>;
    duplicatesFound: number;
    emptyLinesSkipped: number;
  };

  /**
   * @param config - Частичная конфигурация (объединяется с дефолтной)
   * @param logger - Logger для логирования (по умолчанию winston logger)
   * @param lineParser - Парсер строк (по умолчанию GroupLineParser)
   */
  constructor(
    config: Partial<FileParserConfig> = {},
    logger: Logger = defaultLogger,
    lineParser?: GroupLineParser
  ) {
    this.config = { ...defaultConfig, ...config };
    this.logger = logger;
    this.lineParser = lineParser || new GroupLineParser();
    this.metrics = {
      startTime: 0,
      strategiesUsed: new Map(),
      duplicatesFound: 0,
      emptyLinesSkipped: 0
    };
  }

  /**
   * Парсит TXT-файл с группами VK
   * @param filePath - Путь к файлу
   * @param encoding - Кодировка файла (по умолчанию из конфига)
   * @returns Результат парсинга с метаданными
   */
  async parseGroupsFile(
    filePath: string,
    encoding?: BufferEncoding
  ): Promise<ExtendedFileParseResult> {
    this.resetMetrics();
    this.metrics.startTime = Date.now();

    const fileEncoding = encoding || this.config.encoding;

    try {
      const content = await fs.promises.readFile(filePath, fileEncoding);
      const lines = content.split('\n');

      const groups: LegacyParsedGroup[] = [];
      const errors: string[] = [];
      const duplicateIds = new Set<number>();

      for (const [i, line] of lines.entries()) {
        const lineNumber = i + 1;
        const cleanLine = this.cleanLine(line);

        if (!cleanLine) {
          this.metrics.emptyLinesSkipped++;
          continue;
        }

        try {
          const parsed = this.lineParser.parse(cleanLine, lineNumber);

          // Учитываем использованную стратегию
          if (parsed.strategyName) {
            this.trackStrategyUsage(parsed.strategyName);
          }

          // Проверяем дубликаты
          if (!this.checkDuplicates(parsed.id, duplicateIds, lineNumber, errors)) {
            continue;
          }

          const cleanName = this.cleanGroupName(parsed.name);
          const url = this.buildGroupUrl(parsed.id, cleanName);

          groups.push({
            id: parsed.id || 0,
            name: cleanName,
            url
          });
        } catch (error) {
          if (error instanceof ValidationError) {
            // ValidationError уже содержит детали
            errors.push(
              `Line ${lineNumber}: ${error.message} - "${line.trim()}"`
            );
          } else {
            const errorMsg = error instanceof Error ? error.message : String(error);
            errors.push(`Line ${lineNumber}: ${errorMsg} - "${line.trim()}"`);
          }
        }
      }

      const parseTimeMs = Date.now() - this.metrics.startTime;
      const metadata = this.buildMetadata(groups.length, lines.length, parseTimeMs);

      this.logParsingResults(groups, lines.length, errors.length, metadata);

      return {
        groups,
        errors,
        totalProcessed: lines.length,
        metadata
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      this.logger.error('Failed to parse file', error, { filePath });
      throw new Error(`Failed to parse file: ${errorMsg}`);
    }
  }

  /**
   * Валидирует файл перед парсингом
   * @param filePath - Путь к файлу
   * @returns Результат валидации
   */
  async validateFile(filePath: string): Promise<ValidationResult> {
    try {
      const stats = await fs.promises.stat(filePath);
      const errors: string[] = [];

      // Проверяем размер
      if (stats.size > this.config.maxFileSizeMb * 1024 * 1024) {
        errors.push(
          `File size exceeds ${this.config.maxFileSizeMb}MB limit`
        );
      }

      // Проверяем расширение
      const ext = filePath.toLowerCase().split('.').pop();
      if (!this.config.allowedExtensions.includes(`.${ext}`)) {
        errors.push(
          `File must have one of extensions: ${this.config.allowedExtensions.join(', ')}`
        );
      }

      const isValid = errors.length === 0;

      if (!isValid) {
        this.logger.error('File validation failed', undefined, { filePath, errors });
      }

      return {
        isValid,
        errors,
        data: isValid ? { size: stats.size, extension: ext } : undefined
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      this.logger.error('File validation failed', error, { filePath });

      return {
        isValid: false,
        errors: [errorMsg]
      };
    }
  }

  /**
   * Проверяет доступность файла для чтения
   */
  async isFileAccessible(filePath: string): Promise<boolean> {
    try {
      await fs.promises.access(filePath, fs.constants.R_OK);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Получает статистику файла
   */
  async getFileStats(filePath: string): Promise<fs.Stats | null> {
    try {
      return await fs.promises.stat(filePath);
    } catch {
      return null;
    }
  }

  /**
   * Возвращает текущий LineParser (для добавления кастомных стратегий)
   */
  getLineParser(): GroupLineParser {
    return this.lineParser;
  }

  // ============ Приватные методы ============

  private resetMetrics(): void {
    this.metrics.startTime = 0;
    this.metrics.strategiesUsed.clear();
    this.metrics.duplicatesFound = 0;
    this.metrics.emptyLinesSkipped = 0;
  }

  private trackStrategyUsage(strategyName: string): void {
    const current = this.metrics.strategiesUsed.get(strategyName) || 0;
    this.metrics.strategiesUsed.set(strategyName, current + 1);
  }

  private cleanLine(line: string): string | null {
    const trimmed = line.trim();
    if (!trimmed) return null;

    // Удаляем комментарии (#)
    const clean = trimmed.split('#')[0].trim();
    if (!clean) return null;

    return clean;
  }

  private checkDuplicates(
    id: number | null,
    duplicateIds: Set<number>,
    lineNumber: number,
    errors: string[]
  ): boolean {
    if (id !== null && id !== undefined) {
      if (duplicateIds.has(id)) {
        errors.push(`Line ${lineNumber}: Duplicate group ID ${id}`);
        this.metrics.duplicatesFound++;
        return false;
      }
      duplicateIds.add(id);
    }
    return true;
  }

  private cleanGroupName(name: string | null): string {
    if (!name) return '';
    let cleanName = name;
    if (cleanName.startsWith('https://vk.com/')) {
      cleanName = cleanName.replace('https://vk.com/', '');
    }
    return cleanName;
  }

  private buildGroupUrl(id: number | null, name: string): string {
    if (id) {
      return `${this.config.vkBaseUrl}/club${id}`;
    }
    if (name) {
      return `${this.config.vkBaseUrl}/${name}`;
    }
    return '';
  }

  private buildMetadata(
    validGroups: number,
    totalLines: number,
    parseTimeMs: number
  ): FileParseMetadata {
    return {
      parseTimeMs,
      successRate: totalLines > 0 ? validGroups / totalLines : 0,
      duplicatesFound: this.metrics.duplicatesFound,
      emptyLinesSkipped: this.metrics.emptyLinesSkipped,
      strategiesUsed: Object.fromEntries(this.metrics.strategiesUsed)
    };
  }

  private logParsingResults(
    groups: LegacyParsedGroup[],
    totalLines: number,
    errorsCount: number,
    metadata: FileParseMetadata
  ): void {
    const sampleGroups = groups.slice(0, this.config.sampleGroupsCount);

    this.logger.info('Sample parsed groups', {
      sample: sampleGroups.map(g => ({ id: g.id, name: g.name, url: g.url })),
      totalLines,
      validGroups: groups.length,
      errors: errorsCount
    });

    this.logger.info('File parsing completed', {
      parseTimeMs: metadata.parseTimeMs,
      throughput: `${(totalLines / (metadata.parseTimeMs / 1000)).toFixed(2)} lines/sec`,
      successRate: `${(metadata.successRate * 100).toFixed(2)}%`,
      totalLines,
      validGroups: groups.length,
      errors: errorsCount,
      duplicatesFound: metadata.duplicatesFound,
      emptyLinesSkipped: metadata.emptyLinesSkipped,
      strategiesUsed: metadata.strategiesUsed
    });
  }
}