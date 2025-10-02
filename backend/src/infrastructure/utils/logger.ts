/**
 * Простой и надежный логгер для VK backend
 */

import { Logger } from '@shared/types/common';

/**
 * Простая имплементация логгера с выводом в консоль
 */
class SimpleLogger implements Logger {
  private getTimestamp(): string {
    return new Date().toISOString();
  }

  private formatMeta(meta?: any): string {
    if (!meta || Object.keys(meta).length === 0) {
      return '';
    }
    try {
      return ' ' + JSON.stringify(meta);
    } catch {
      return ' [meta serialization failed]';
    }
  }

  info(message: string, meta?: any): void {
    console.log(`[${this.getTimestamp()}] INFO: ${message}${this.formatMeta(meta)}`);
  }

  error(message: string, error?: Error | any, meta?: any): void {
    const errorInfo = error instanceof Error
      ? ` - ${error.message}\n${error.stack}`
      : error
        ? ` - ${JSON.stringify(error)}`
        : '';
    console.error(`[${this.getTimestamp()}] ERROR: ${message}${errorInfo}${this.formatMeta(meta)}`);
  }

  warn(message: string, meta?: any): void {
    console.warn(`[${this.getTimestamp()}] WARN: ${message}${this.formatMeta(meta)}`);
  }

  debug(message: string, meta?: any): void {
    if (process.env.LOG_LEVEL === 'debug' || process.env.NODE_ENV === 'development') {
      console.log(`[${this.getTimestamp()}] DEBUG: ${message}${this.formatMeta(meta)}`);
    }
  }
}

const logger = new SimpleLogger();

// Тестовый лог при инициализации
logger.info('Logger initialized successfully');

export default logger;