/**
 * @fileoverview IFileParser - интерфейс для парсинга файлов
 *
 * Domain Repository Interface для работы с файлами групп.
 */

/**
 * Спарсенная группа из файла
 */
export interface ParsedGroup {
  readonly id?: number;
  readonly name: string;
  readonly screenName?: string;
  readonly url?: string;
}

/**
 * Результат парсинга файла
 */
export interface FileParseResult {
  readonly groups: readonly ParsedGroup[];
  readonly errors: readonly string[];
}

/**
 * Результат валидации файла
 */
export interface FileValidationResult {
  readonly isValid: boolean;
  readonly errors: readonly string[];
}

/**
 * File Parser Repository Interface
 *
 * @description
 * Интерфейс для парсинга и валидации файлов с группами.
 * Infrastructure layer будет предоставлять конкретную реализацию.
 */
export interface IFileParser {
  /**
   * Парсит файл с группами
   *
   * @param filePath - Путь к файлу или Buffer
   * @param encoding - Кодировка файла
   * @returns Результат парсинга с группами и ошибками
   */
  parseGroupsFile(
    filePath: string | Buffer,
    encoding: BufferEncoding
  ): Promise<FileParseResult>;

  /**
   * Валидирует файл перед парсингом
   *
   * @param filePath - Путь к файлу или Buffer
   * @returns Результат валидации
   */
  validateFile(filePath: string | Buffer): Promise<FileValidationResult>;
}
