/**
 * @fileoverview FileParserAdapter - адаптер для file parser
 *
 * Адаптирует существующий FileParser к интерфейсу IFileParser из Application Layer.
 */

import { IFileParser, FileParseResult, FileValidationResult } from '@domain/repositories/IFileParser';
import { FileParserFactory } from '@infrastructure/utils/fileParser/FileParserFactory';
import { FileParser } from '@infrastructure/utils/fileParser/FileParser';
import logger from '@infrastructure/utils/logger';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

/**
 * Адаптер для существующего FileParser
 *
 * @description
 * Адаптирует legacy FileParser к новому интерфейсу IFileParser.
 * Обеспечивает совместимость между Infrastructure и Application слоями.
 */
export class FileParserAdapter implements IFileParser {
  private readonly parser: FileParser;

  constructor() {
    this.parser = FileParserFactory.create();
    logger.info('FileParserAdapter initialized');
  }

  /**
   * Парсит файл с группами
   */
  async parseGroupsFile(
    filePath: string | Buffer,
    encoding: BufferEncoding
  ): Promise<FileParseResult> {
    let actualFilePath: string;
    let tempPath: string | null = null;

    try {
      // Если это Buffer, сохраняем во временный файл
      if (Buffer.isBuffer(filePath)) {
        const tempDir = path.join(os.tmpdir(), 'vk-uploads');
        await fs.mkdir(tempDir, { recursive: true });

        tempPath = path.join(
          tempDir,
          `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.txt`
        );

        await fs.writeFile(tempPath, filePath);
        actualFilePath = tempPath;

        logger.debug('Buffer saved to temp file', { tempPath });
      } else {
        actualFilePath = filePath;
      }

      // Парсим файл через legacy parser
      const result = await this.parser.parseGroupsFile(actualFilePath, encoding);

      // Маппим результат к новому формату
      const groups = result.groups.map(group => ({
        id: group.id,
        name: group.name || 'Unknown',
        screenName: group.screenName,
        url: group.url
      }));

      logger.info('File parsed successfully', {
        groupsCount: groups.length,
        errorsCount: result.errors.length
      });

      // Удаляем временный файл
      if (tempPath) {
        await fs.unlink(tempPath);
      }

      return {
        groups,
        errors: result.errors
      };
    } catch (error) {
      // Очистка временного файла при ошибке
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch {
          // Игнорируем ошибки удаления
        }
      }

      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('File parsing failed', { error: errorMsg });
      throw new Error(`Failed to parse file: ${errorMsg}`);
    }
  }

  /**
   * Валидирует файл
   */
  async validateFile(
    filePath: string | Buffer
  ): Promise<FileValidationResult> {
    let actualFilePath: string;
    let tempPath: string | null = null;

    try {
      // Если это Buffer, сохраняем во временный файл для валидации
      if (Buffer.isBuffer(filePath)) {
        const tempDir = path.join(os.tmpdir(), 'vk-uploads');
        await fs.mkdir(tempDir, { recursive: true });

        tempPath = path.join(
          tempDir,
          `validate-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.txt`
        );

        await fs.writeFile(tempPath, filePath);
        actualFilePath = tempPath;
      } else {
        actualFilePath = filePath;
      }

      // Используем метод валидации legacy parser'а
      const result = await this.parser.validateFile(actualFilePath);

      // Удаляем временный файл
      if (tempPath) {
        await fs.unlink(tempPath);
      }

      logger.debug('File validated', {
        isValid: result.isValid,
        errorsCount: result.errors.length
      });

      return result;
    } catch (error) {
      // Очистка временного файла при ошибке
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch {
          // Игнорируем ошибки удаления
        }
      }

      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('File validation failed', { error: errorMsg });

      return {
        isValid: false,
        errors: [errorMsg]
      };
    }
  }
}
