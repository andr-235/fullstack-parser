import { FileParser, FileParserConfig } from './FileParser';
import { GroupLineParser } from './GroupLineParser';
import { Logger } from '@/types/common';

/**
 * Фабрика для создания экземпляров FileParser.
 * Упрощает создание парсеров с различными конфигурациями.
 */
export class FileParserFactory {
  /**
   * Создает FileParser с дефолтной или кастомной конфигурацией
   * @param config - Частичная конфигурация
   * @returns Новый экземпляр FileParser
   */
  static create(config?: Partial<FileParserConfig>): FileParser {
    return new FileParser(config);
  }

  /**
   * Создает FileParser для тестирования с моками
   * @param config - Конфигурация
   * @param mockLogger - Мок logger
   * @param mockLineParser - Мок line parser
   * @returns Новый экземпляр FileParser с моками
   */
  static createForTesting(
    config?: Partial<FileParserConfig>,
    mockLogger?: Logger,
    mockLineParser?: GroupLineParser
  ): FileParser {
    return new FileParser(config, mockLogger, mockLineParser);
  }

  /**
   * Создает FileParser с увеличенным лимитом размера файла
   * @param maxFileSizeMb - Максимальный размер в MB
   * @returns Новый экземпляр FileParser
   */
  static createWithLargeFileSupport(maxFileSizeMb: number): FileParser {
    return new FileParser({ maxFileSizeMb });
  }

  /**
   * Создает FileParser с кастомной кодировкой
   * @param encoding - Кодировка файла
   * @returns Новый экземпляр FileParser
   */
  static createWithEncoding(encoding: BufferEncoding): FileParser {
    return new FileParser({ encoding });
  }
}