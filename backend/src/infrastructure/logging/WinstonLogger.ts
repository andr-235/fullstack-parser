/**
 * @fileoverview Winston Logger Implementation
 *
 * Продвинутый логгер на основе Winston с поддержкой:
 * - Множественных транспортов (консоль, файлы)
 * - Ротации логов по дням
 * - Structured logging (JSON)
 * - Контекстного логирования
 */

import winston from 'winston';
import { Logger } from '@shared/types/common';
import { LOG_LEVELS, logConfig, defaultMetadata } from './config';
import { createTransports } from './transports';
import fs from 'fs';
import path from 'path';

/**
 * Winston Logger Adapter
 *
 * Адаптирует Winston к интерфейсу Logger из shared
 */
class WinstonLogger implements Logger {
  private logger: winston.Logger;
  private static instance: WinstonLogger | null = null;

  private constructor() {
    // Создаем директорию для логов, если её нет
    this.ensureLogsDirectory();

    // Создаем Winston logger
    this.logger = winston.createLogger({
      levels: LOG_LEVELS,
      level: logConfig.level,
      defaultMeta: defaultMetadata,
      transports: createTransports(),
      exitOnError: false,
    });

    // Добавляем цвета для уровней
    winston.addColors({
      error: 'red',
      warn: 'yellow',
      info: 'green',
      http: 'magenta',
      debug: 'blue',
    });

    this.logger.info('Winston Logger initialized', {
      level: logConfig.level,
      fileLogging: logConfig.file.enabled,
      logsDirectory: logConfig.file.directory,
    });
  }

  /**
   * Singleton instance
   */
  public static getInstance(): WinstonLogger {
    if (!WinstonLogger.instance) {
      WinstonLogger.instance = new WinstonLogger();
    }
    return WinstonLogger.instance;
  }

  /**
   * Создает директорию для логов
   */
  private ensureLogsDirectory(): void {
    if (logConfig.file.enabled) {
      const logsDir = logConfig.file.directory;

      if (!fs.existsSync(logsDir)) {
        fs.mkdirSync(logsDir, { recursive: true });
      }
    }
  }

  /**
   * Нормализует метаданные
   */
  private normalizeMeta(meta?: any): object {
    if (!meta) {
      return {};
    }

    // Если это Error, извлекаем stack
    if (meta instanceof Error) {
      return {
        error: meta.message,
        stack: meta.stack,
        name: meta.name,
      };
    }

    // Если это объект, возвращаем как есть
    if (typeof meta === 'object') {
      return meta;
    }

    // Иначе оборачиваем в объект
    return { data: meta };
  }

  /**
   * INFO уровень
   */
  info(message: string, meta?: any): void {
    this.logger.info(message, this.normalizeMeta(meta));
  }

  /**
   * ERROR уровень
   */
  error(message: string, error?: Error | any, meta?: any): void {
    const errorMeta = this.normalizeMeta(error);
    const additionalMeta = this.normalizeMeta(meta);

    this.logger.error(message, {
      ...errorMeta,
      ...additionalMeta,
    });
  }

  /**
   * WARN уровень
   */
  warn(message: string, meta?: any): void {
    this.logger.warn(message, this.normalizeMeta(meta));
  }

  /**
   * DEBUG уровень
   */
  debug(message: string, meta?: any): void {
    this.logger.debug(message, this.normalizeMeta(meta));
  }

  /**
   * HTTP уровень (для логирования HTTP запросов)
   */
  http(message: string, meta?: any): void {
    this.logger.log('http', message, this.normalizeMeta(meta));
  }

  /**
   * Логирование с произвольным уровнем
   */
  log(level: string, message: string, meta?: any): void {
    this.logger.log(level, message, this.normalizeMeta(meta));
  }

  /**
   * Создает child logger с дополнительным контекстом
   */
  child(context: object): Logger {
    const childLogger = this.logger.child(context);

    // Возвращаем обертку, которая реализует Logger интерфейс
    return {
      info: (message: string, meta?: any) => {
        childLogger.info(message, this.normalizeMeta(meta));
      },
      error: (message: string, error?: Error | any, meta?: any) => {
        const errorMeta = this.normalizeMeta(error);
        const additionalMeta = this.normalizeMeta(meta);
        childLogger.error(message, { ...errorMeta, ...additionalMeta });
      },
      warn: (message: string, meta?: any) => {
        childLogger.warn(message, this.normalizeMeta(meta));
      },
      debug: (message: string, meta?: any) => {
        childLogger.debug(message, this.normalizeMeta(meta));
      },
    };
  }

  /**
   * Получает нативный Winston logger (для продвинутого использования)
   */
  getWinstonLogger(): winston.Logger {
    return this.logger;
  }

  /**
   * Graceful shutdown
   */
  async close(): Promise<void> {
    return new Promise((resolve) => {
      this.logger.on('finish', () => {
        resolve();
      });
      this.logger.end();
    });
  }
}

// Экспортируем singleton instance
const logger = WinstonLogger.getInstance();

export default logger;
export { WinstonLogger };
