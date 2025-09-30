import { promises as fs } from 'fs';
import { Stats } from 'fs';
import logger from './logger';
import { FileParseResult, ProcessedGroup, ValidationResult } from '@/types/common';

interface ParseError {
  line: number;
  content: string;
  error: string;
  expectedFormat?: string;
  groupId?: number;
}

interface ParsedGroup {
  id: number | null;
  name: string | null;
  lineNumber: number;
}

class FileParser {
  /**
   * Парсит TXT файл с группами VK
   */
  static async parseGroupsFile(
    filePath: string,
    encoding: BufferEncoding = 'utf-8'
  ): Promise<FileParseResult> {
    try {
      const content = await fs.readFile(filePath, encoding);
      const lines = content.split('\n');

      const groups: ProcessedGroup[] = [];
      const errors: string[] = [];
      const duplicateIds = new Set<number>();

      for (let i = 0; i < lines.length; i++) {
        const lineNumber = i + 1;
        const line = lines[i]?.trim() || '';

        // Пропускаем пустые строки
        if (!line) continue;

        // Удаляем комментарии после #
        const cleanLine = line.split('#')[0]?.trim() || '';
        if (!cleanLine) continue;

        try {
          const parsed = this.parseGroupLine(cleanLine, lineNumber);
          if (parsed) {
            // Проверяем на дубликаты только для групп с ID
            if (parsed.id !== null && parsed.id !== undefined) {
              if (duplicateIds.has(parsed.id)) {
                errors.push(`Line ${lineNumber}: Duplicate group ID ${parsed.id}`);
                continue;
              }
              duplicateIds.add(parsed.id);
            }

            // Очищаем name от URL префикса, если он есть
            let cleanName = parsed.name || '';
            if (cleanName.startsWith('https://vk.com/')) {
              cleanName = cleanName.replace('https://vk.com/', '');
            }

            groups.push({
              id: parsed.id || 0,
              name: cleanName,
              url: parsed.id ? `https://vk.com/club${parsed.id}` : (cleanName ? `https://vk.com/${cleanName}` : '')
            });
          }
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          errors.push(`Line ${lineNumber}: ${errorMsg} - "${line}"`);
        }
      }

      // Log sample parsed groups for debugging
      const sampleGroups = groups.slice(0, 5);
      logger.info('Sample parsed groups (first 5)', {
        sample: sampleGroups.map(g => ({ id: g.id, name: g.name, url: g.url })),
        totalLines: lines.length,
        validGroups: groups.length,
        errors: errors.length
      });

      logger.info('File parsed successfully', {
        totalLines: lines.length,
        validGroups: groups.length,
        errors: errors.length
      });

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
   * Парсит одну строку с группой
   */
  static parseGroupLine(line: string, lineNumber: number): ParsedGroup | null {
    // 1. Проверяем URL формата https://vk.com/club12345
    const urlClubMatch = line.match(/^https:\/\/vk\.com\/club(\d+)$/i);
    if (urlClubMatch) {
      const groupId = parseInt(urlClubMatch[1], 10);
      if (isNaN(groupId) || groupId <= 0) {
        throw new Error('Invalid group ID in URL');
      }
      return {
        id: groupId,
        name: null,
        lineNumber
      };
    }

    // 2. Проверяем URL формата https://vk.com/screen_name (НЕ club)
    const urlScreenNameMatch = line.match(/^https:\/\/vk\.com\/([a-zA-Z0-9_]+)$/i);
    if (urlScreenNameMatch) {
      const screenName = urlScreenNameMatch[1];
      // Если это не "club", значит это screen_name - сохраняем как имя для дальнейшего резолвинга
      return {
        id: null,
        name: screenName,
        lineNumber
      };
    }

    // 3. Проверяем, является ли строка ID группы (отрицательное число)
    if (line.startsWith('-') && /^-\d+$/.test(line)) {
      const groupId = parseInt(line, 10);
      if (groupId >= 0) {
        throw new Error('Group ID must be negative');
      }
      return {
        id: Math.abs(groupId), // Храним положительный в БД
        name: null,
        lineNumber
      };
    }

    // 4. Если строка является положительным числом (прямой ID)
    if (/^\d+$/.test(line)) {
      const groupId = parseInt(line, 10);
      if (groupId > 0) {
        return {
          id: groupId,
          name: null,
          lineNumber
        };
      }
      throw new Error('Group ID must be positive');
    }

    // 5. Если строка начинается с - но не является отрицательным числом
    if (line.startsWith('-') && !/^-\d+$/.test(line)) {
      throw new Error('Invalid group format');
    }

    // 6. Проверяем, является ли строка screen_name без URL (club123 или просто строка)
    if (!line.startsWith('-') && !/^\d+$/.test(line)) {
      // Если это screen_name типа "club123", извлекаем число
      const screenMatch = line.match(/^club(\d+)$/i);
      if (screenMatch) {
        const groupId = parseInt(screenMatch[1], 10);
        if (groupId > 0) {
          return {
            id: groupId,
            name: line,
            lineNumber
          };
        }
      }
      // Иначе просто screen_name группы без ID - сохраняем для дальнейшего резолвинга
      return {
        id: null,
        name: line,
        lineNumber
      };
    }

    // Если мы дошли сюда, значит строка не подходит ни под один формат
    throw new Error('Invalid group format');
  }

  /**
   * Валидирует формат файла
   */
  static async validateFile(filePath: string): Promise<ValidationResult> {
    try {
      const stats: Stats = await fs.stat(filePath);
      const errors: string[] = [];

      // Проверяем размер файла (10MB)
      if (stats.size > 10 * 1024 * 1024) {
        errors.push('File size exceeds 10MB limit');
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
   * Проверяет доступность файла для чтения
   */
  static async isFileAccessible(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath, fs.constants.R_OK);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Получает статистику файла
   */
  static async getFileStats(filePath: string): Promise<Stats | null> {
    try {
      return await fs.stat(filePath);
    } catch {
      return null;
    }
  }
}

export default FileParser;
export { FileParser };
export type { ParsedGroup, ParseError };