/**
 * Winston logger instance для VK backend с поддержкой context enrichment и structured logging.
 *
 * Основное использование:
 * ```typescript
 * import logger from '@/utils/logger';
 * logger.info('Message', { meta: 'data' });
 * ```
 *
 * С контекстом:
 * ```typescript
 * import { withContext } from '@/utils/logger';
 * const ctxLogger = withContext(logger, { requestId: req.id, userId: 'user-123' });
 * ctxLogger.info('User action');
 * ```
 */

import winston, { Logger as WinstonLogger } from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import path from 'path';
import { Logger, LogLevel } from '@/types/common';
import { Environment } from '@/types/database';

/**
 * Контекст для обогащения логов дополнительной информацией
 */
export interface LoggerContext {
  requestId?: string;
  userId?: string;
  taskId?: string;
  [key: string]: any;
}

/**
 * Опции для создания logger instance
 */
export interface LoggerOptions {
  level?: LogLevel;
  service?: string;
  environment?: Environment;
  logDir?: string;
}

/**
 * Создает Winston logger с правильной конфигурацией
 *
 * @param options - Параметры конфигурации logger
 * @returns Настроенный Winston logger instance
 */
export function createLogger(options: LoggerOptions = {}): WinstonLogger {
  const {
    level = (process.env.LOG_LEVEL as LogLevel) || 'info',
    service = 'vk-backend',
    environment = (process.env.NODE_ENV as Environment) || 'development',
    logDir = process.env.LOG_DIR || 'backend/logs'
  } = options;

  return winston.createLogger({
    level,
    defaultMeta: { service, environment },
    format: winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      winston.format.errors({ stack: true }),
      winston.format.json()
    ),
    transports: createTransports(level, environment, logDir)
  });
}

/**
 * Создает transports для Winston logger
 *
 * @param level - Уровень логирования
 * @param environment - Окружение (development, production, test)
 * @param logDir - Директория для файлов логов
 * @returns Массив Winston transports
 */
function createTransports(
  level: LogLevel,
  environment: Environment,
  logDir: string
): winston.transport[] {
  const transports: winston.transport[] = [
    new winston.transports.Console({
      level,
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ level, message, timestamp, service, ...meta }) => {
          const metaStr = Object.keys(meta).length > 0 ? JSON.stringify(meta) : '';
          return `${timestamp} [${service}] ${level}: ${message} ${metaStr}`;
        })
      )
    })
  ];

  // В тестовом окружении не пишем в файлы
  if (environment === 'test') {
    return transports;
  }

  // Rotation для error логов
  transports.push(
    new DailyRotateFile({
      filename: path.join(logDir, 'error-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: process.env.LOG_MAX_SIZE || '5m',
      maxFiles: process.env.LOG_MAX_FILES || '5',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      )
    })
  );

  // Rotation для всех логов
  transports.push(
    new DailyRotateFile({
      filename: path.join(logDir, 'combined-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      level: 'info',
      maxSize: process.env.LOG_MAX_SIZE || '5m',
      maxFiles: process.env.LOG_MAX_FILES || '5',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      )
    })
  );

  return transports;
}

/**
 * Создает child logger с добавленным контекстом
 *
 * @param logger - Базовый Winston logger
 * @param context - Контекст для добавления в каждый лог
 * @returns Child logger с контекстом
 */
export function withContext(logger: WinstonLogger, context: LoggerContext): WinstonLogger {
  return logger.child(context);
}

/**
 * Форматирует объект Error для структурированного логирования
 *
 * @param error - Объект ошибки
 * @returns Объект с детальной информацией об ошибке
 */
export function formatError(error: Error): Record<string, any> {
  const formatted: Record<string, any> = {
    message: error.message,
    name: error.name,
    stack: error.stack
  };

  // Добавляем cause если он присутствует (ES2022 feature)
  if ('cause' in error && (error as any).cause) {
    formatted.cause = (error as any).cause;
  }

  return formatted;
}

/**
 * Wrapper класс для обратной совместимости с существующим кодом
 */
class AppLogger implements Logger {
  private winston: WinstonLogger;

  constructor(options: LoggerOptions = {}) {
    this.winston = createLogger(options);
  }

  info(message: string, meta?: any): void {
    this.winston.info(message, meta);
  }

  error(message: string, error?: Error | any, meta?: any): void {
    if (error instanceof Error) {
      this.winston.error(message, {
        error: formatError(error),
        ...meta
      });
    } else if (error) {
      this.winston.error(message, { error, ...meta });
    } else {
      this.winston.error(message, meta);
    }
  }

  warn(message: string, meta?: any): void {
    this.winston.warn(message, meta);
  }

  debug(message: string, meta?: any): void {
    this.winston.debug(message, meta);
  }

  setLevel(level: LogLevel): void {
    this.winston.level = level;
  }

  getLevel(): string {
    return this.winston.level;
  }
}

// Singleton instance для обратной совместимости
const logger = new AppLogger();

export default logger;
export { AppLogger };
export type { Logger };