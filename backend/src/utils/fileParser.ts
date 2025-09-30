import fs from 'fs';
import logger from './logger';
import { 
  FileParseResult, 
  ParsedGroup, 
  ParseError, 
  ProcessedGroup, 
  ValidationResult 
} from '@/types/common';

/**
 * Константы для парсера файлов с группами VK.
 */
const FILE_PARSER_CONSTANTS = {
  MAX_FILE_SIZE_MB: 10,
  SAMPLE_GROUPS_COUNT: 5,
  VK_BASE_URL: 'https://vk.com',
  CLUB_PREFIX: 'club'
} as const;

/**
 * Кастомная ошибка парсинга группы.
 * @extends {Error}
 */
class GroupParseError extends Error {
  public parseError: ParseError;

  /**
   * @param {ParseError} parseError - Детали ошибки парсинга.
   */
  constructor(parseError: ParseError) {
    super(parseError.error);
    this.name = 'GroupParseError';
    this.parseError = parseError;
  }
}

/**
 * @classdesc Класс для парсинга TXT-файлов с данными о группах VK.
 * Следует принципам SOLID: Single Responsibility для методов парсинга.
 * Использует константы для магических чисел и кастомные ошибки для обработки ошибок.
 * Поддерживает форматы: ID (положительный/отрицательный), screen_name, URL (club/ID или screen_name).
 */
class FileParser {
  /**
   * Парсит TXT-файл с группами VK.
   * Читает файл, очищает строки, парсит каждую, проверяет дубликаты и строит URL.
   * @param {string} filePath - Путь к TXT-файлу с группами.
   * @param {BufferEncoding} [encoding='utf-8'] - Кодировка файла.
   * @returns {Promise<FileParseResult>} Результат парсинга: группы, ошибки, общее количество строк.
   * @throws {Error} Если не удалось прочитать файл (e.g., не существует или нет прав).
   * @example
   * const result = await FileParser.parseGroupsFile('./groups.txt');
   * console.log(result.groups); // [{ id: 123, name: 'group', url: 'https://vk.com/club123' }]
   * console.log(result.errors); // [] если успешно
   */
  static async parseGroupsFile(
    filePath: string,
    encoding: BufferEncoding = 'utf-8'
  ): Promise<FileParseResult> {
    try {
      const content = await fs.promises.readFile(filePath, encoding);
      const lines = content.split('\n');

      const groups: ProcessedGroup[] = [];
      const errors: string[] = [];
      const duplicateIds = new Set<number>();

      for (const [i, line] of lines.entries()) {
        const lineNumber = i + 1;
        const cleanLine = FileParser.cleanLine(line, lineNumber, errors);
        if (!cleanLine) continue;

        try {
          const parsed = FileParser.parseGroupLine(cleanLine, lineNumber);
          if (parsed) {
            if (!FileParser.checkDuplicates(parsed.id, duplicateIds, lineNumber, errors)) {
              continue;
            }

            const cleanName = FileParser.cleanGroupName(parsed.name);
            const url = FileParser.buildGroupUrl(parsed.id, cleanName);

            groups.push({
              id: parsed.id || 0,
              name: cleanName,
              url
            });
          }
        } catch (error) {
          if (error instanceof GroupParseError) {
            errors.push(
              `Line ${lineNumber}: ${error.message} - "${line.trim()}" ` +
              `(expected: ${error.parseError.expectedFormat || 'valid VK group format'})`
            );
          } else {
            const errorMsg = error instanceof Error ? error.message : String(error);
            errors.push(`Line ${lineNumber}: ${errorMsg} - "${line.trim()}"`);
          }
        }
      }

      FileParser.logParsingResults(groups, lines.length, errors.length);

      return {
        groups,
        errors,
        totalProcessed: lines.length
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to parse file', { filePath, error: errorMsg });
      throw new Error(`Failed to parse file: ${errorMsg}`);
    }
  }

  /**
   * Очищает строку от комментариев (#) и лишних пробелов.
   * Игнорирует пустые строки.
   * @param {string} line - Исходная строка из файла.
   * @param {number} lineNumber - Номер строки для логирования ошибок.
   * @param {string[]} errors - Массив для добавления ошибок (если нужно).
   * @returns {string | null} Очищенная строка или null если пустая/комментарий.
   * @private
   */
  private static cleanLine(
    line: string,
    lineNumber: number,
    errors: string[]
  ): string | null {
    const trimmed = line.trim();
    if (!trimmed) return null;

    const clean = trimmed.split('#')[0].trim();
    if (!clean) return null;

    return clean;
  }

  /**
   * Проверяет ID группы на дубликаты.
   * Добавляет в Set если уникальный.
   * @param {number | null} id - ID группы для проверки.
   * @param {Set<number>} duplicateIds - Множество существующих ID.
   * @param {number} lineNumber - Номер строки для ошибки.
   * @param {string[]} errors - Массив для добавления ошибок.
   * @returns {boolean} true если уникальный или null ID, false если дубликат.
   * @private
   */
  private static checkDuplicates(
    id: number | null,
    duplicateIds: Set<number>,
    lineNumber: number,
    errors: string[]
  ): boolean {
    if (id !== null && id !== undefined) {
      if (duplicateIds.has(id)) {
        errors.push(`Line ${lineNumber}: Duplicate group ID ${id}`);
        return false;
      }
      duplicateIds.add(id);
    }
    return true;
  }

  /**
   * Очищает имя группы от префикса VK URL если присутствует.
   * @param {string | null} name - Исходное имя или screen_name.
   * @returns {string} Очищенное имя (пустая строка если null).
   * @private
   */
  private static cleanGroupName(name: string | null): string {
    if (!name) return '';
    let cleanName = name;
    if (cleanName.startsWith('https://vk.com/')) {
      cleanName = cleanName.replace('https://vk.com/', '');
    }
    return cleanName;
  }

  /**
   * Строит полный URL группы VK на основе ID или screen_name.
   * Для ID использует формат /club<ID>, для screen_name — /screen_name.
   * @param {number | null} id - ID группы (положительный).
   * @param {string} name - Screen_name или очищенное имя.
   * @returns {string} Полный URL или пустая строка если оба null.
   * @private
   */
  private static buildGroupUrl(id: number | null, name: string): string {
    if (id) {
      return `${FILE_PARSER_CONSTANTS.VK_BASE_URL}/club${id}`;
    }
    if (name) {
      return `${FILE_PARSER_CONSTANTS.VK_BASE_URL}/${name}`;
    }
    return '';
  }

  /**
   * Логирует результаты парсинга: сэмпл групп и статистику.
   * @param {ProcessedGroup[]} groups - Список успешно обработанных групп.
   * @param {number} totalLines - Общее количество строк в файле.
   * @param {number} errorsCount - Количество ошибок.
   * @private
   */
  private static logParsingResults(
    groups: ProcessedGroup[],
    totalLines: number,
    errorsCount: number
  ): void {
    const sampleGroups = groups.slice(0, FILE_PARSER_CONSTANTS.SAMPLE_GROUPS_COUNT);
    logger.info('Sample parsed groups (first 5)', {
      sample: sampleGroups.map(g => ({ id: g.id, name: g.name, url: g.url })),
      totalLines,
      validGroups: groups.length,
      errors: errorsCount
    });

    logger.info('File parsed successfully', {
      totalLines,
      validGroups: groups.length,
      errors: errorsCount
    });
  }

  /**
   * Парсит одну строку файла в объект группы VK.
   * Поддерживает форматы: URL (club/ID, screen_name), ID (+/-), screen_name.
   * @param {string} line - Строка для парсинга (очищенная).
   * @param {number} lineNumber - Номер строки в файле.
   * @returns {ParsedGroup} Объект с id, name и lineNumber.
   * @throws {GroupParseError} Если формат строки неверный.
   * @example
   * const parsed = FileParser.parseGroupLine('-123', 1);
   * // { id: 123, name: null, lineNumber: 1 }
   * @example
   * const parsed = FileParser.parseGroupLine('https://vk.com/durov', 2);
   * // { id: null, name: 'durov', lineNumber: 2 }
   */
  static parseGroupLine(line: string, lineNumber: number): ParsedGroup {
    const parseResult = FileParser.parseUrlClub(line);
    if (parseResult) return { ...parseResult, lineNumber };

    const screenNameResult = FileParser.parseUrlScreenName(line);
    if (screenNameResult) return { ...screenNameResult, lineNumber };

    const negativeIdResult = FileParser.parseNegativeId(line);
    if (negativeIdResult) return { ...negativeIdResult, lineNumber };

    const positiveIdResult = FileParser.parsePositiveId(line);
    if (positiveIdResult) return { ...positiveIdResult, lineNumber };

    const screenNameResult2 = FileParser.parseScreenName(line);
    if (screenNameResult2) return { ...screenNameResult2, lineNumber };

    throw new GroupParseError({
      line: lineNumber,
      content: line,
      error: 'Invalid group format',
      expectedFormat: 
        'VK group ID (e.g., -123 or 123), screen_name (e.g., durov), ' +
        'or URL (e.g., https://vk.com/club123)'
    });
  }

  /**
   * Парсит URL формата https://vk.com/club<ID>.
   * @param {string} line - Строка для парсинга.
   * @returns {Omit<ParsedGroup, 'lineNumber'> | null} {id, name: null} или null.
   * @private
   */
  private static parseUrlClub(line: string): Omit<ParsedGroup, 'lineNumber'> | null {
    const match = line.match(
      new RegExp(`^https://vk\\.com/${FILE_PARSER_CONSTANTS.CLUB_PREFIX}(\\d+)$`, 'i')
    );
    if (match) {
      const groupId = parseInt(match[1], 10);
      if (!isNaN(groupId) && groupId > 0) {
        return { id: groupId, name: null };
      }
    }
    return null;
  }

  /**
   * Парсит URL screen_name (https://vk.com/screen_name, не club).
   * @param {string} line - Строка для парсинга.
   * @returns {Omit<ParsedGroup, 'lineNumber'> | null} {id: null, name} или null.
   * @private
   */
  private static parseUrlScreenName(
    line: string
  ): Omit<ParsedGroup, 'lineNumber'> | null {
    const match = line.match(/^https:\/\/vk\.com\/([a-zA-Z0-9_]+)$/i);
    if (match) {
      const screenName = match[1];
      if (screenName !== FILE_PARSER_CONSTANTS.CLUB_PREFIX) {
        return { id: null, name: screenName };
      }
    }
    return null;
  }

  /**
   * Парсит отрицательный ID группы (e.g., -123).
   * Возвращает абсолютное значение ID.
   * @param {string} line - Строка для парсинга.
   * @returns {Omit<ParsedGroup, 'lineNumber'> | null} {id: abs, name: null} или null.
   * @private
   */
  private static parseNegativeId(line: string): Omit<ParsedGroup, 'lineNumber'> | null {
    if (line.startsWith('-') && /^-\d+$/.test(line)) {
      const groupId = parseInt(line, 10);
      if (groupId < 0) {
        return { id: Math.abs(groupId), name: null };
      }
    }
    return null;
  }

  /**
   * Парсит положительный ID группы (e.g., 123).
   * @param {string} line - Строка для парсинга.
   * @returns {Omit<ParsedGroup, 'lineNumber'> | null} {id, name: null} или null если <=0.
   * @private
   */
  private static parsePositiveId(line: string): Omit<ParsedGroup, 'lineNumber'> | null {
    if (/^\d+$/.test(line)) {
      const groupId = parseInt(line, 10);
      if (groupId > 0) {
        return { id: groupId, name: null };
      }
    }
    return null;
  }

  /**
   * Парсит screen_name (e.g., club123 или durov).
   * Если club\\d+ — парсит как ID с name=club123.
   * @param {string} line - Строка для парсинга (не ID, не отрицательный).
   * @returns {Omit<ParsedGroup, 'lineNumber'> | null} {id, name} или {null, name}.
   * @private
   */
  private static parseScreenName(line: string): Omit<ParsedGroup, 'lineNumber'> | null {
    if (line.startsWith('-') || /^\d+$/.test(line)) return null;

    const match = line.match(
      new RegExp(`^${FILE_PARSER_CONSTANTS.CLUB_PREFIX}(\\d+)$`, 'i')
    );
    if (match) {
      const groupId = parseInt(match[1], 10);
      if (groupId > 0) {
        return { id: groupId, name: line };
      }
    }

    // Просто screen_name
    return { id: null, name: line };
  }

  /**
   * Валидирует файл перед парсингом: размер, расширение.
   * @param {string} filePath - Путь к файлу.
   * @returns {Promise<ValidationResult>} Результат: isValid, errors, data (size, ext).
   * @example
   * const validation = await FileParser.validateFile('./groups.txt');
   * if (validation.isValid) {
   *   // Proceed to parse
   * }
   */
  static async validateFile(filePath: string): Promise<ValidationResult> {
    try {
      const stats = await fs.promises.stat(filePath);
      const errors: string[] = [];

      // Проверяем размер файла
      if (stats.size > FILE_PARSER_CONSTANTS.MAX_FILE_SIZE_MB * 1024 * 1024) {
        errors.push(
          `File size exceeds ${FILE_PARSER_CONSTANTS.MAX_FILE_SIZE_MB}MB limit`
        );
      }

      // Проверяем расширение
      const ext = filePath.toLowerCase().split('.').pop();
      if (ext !== 'txt') {
        errors.push('File must have .txt extension');
      }

      const isValid = errors.length === 0;

      if (!isValid) {
        logger.error('File validation failed', { filePath, errors });
      }

      return {
        isValid,
        errors,
        data: isValid ? { size: stats.size, extension: ext } : undefined
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('File validation failed', { filePath, error: errorMsg });

      return {
        isValid: false,
        errors: [errorMsg]
      };
    }
  }

  /**
   * Проверяет доступность файла для чтения.
   * @param {string} filePath - Путь к файлу.
   * @returns {Promise<boolean>} true если файл доступен для чтения.
   */
  static async isFileAccessible(filePath: string): Promise<boolean> {
    try {
      await fs.promises.access(filePath, fs.constants.R_OK);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Получает статистику файла (размер, права и т.д.).
   * @param {string} filePath - Путь к файлу.
   * @returns {Promise<fs.Stats | null>} Статистика или null если ошибка.
   */
  static async getFileStats(filePath: string): Promise<fs.Stats | null> {
    try {
      return await fs.promises.stat(filePath);
    } catch {
      return null;
    }
  }
}

export default FileParser;