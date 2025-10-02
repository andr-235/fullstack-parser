/**
 * @fileoverview Winston Log Formatters
 *
 * Форматтеры для различных способов вывода логов
 */

import winston from 'winston';
import { LOG_COLORS } from '../config';

/**
 * Форматтер для консоли (development)
 * Красивый и читаемый формат
 */
export const prettyConsoleFormat = winston.format.combine(
  winston.format.timestamp({ format: 'HH:mm:ss' }),
  winston.format.colorize({ all: true, colors: LOG_COLORS }),
  winston.format.printf(({ timestamp, level, message, service, ...meta }) => {
    const metaStr = Object.keys(meta).length > 0
      ? ` ${JSON.stringify(meta, null, 2)}`
      : '';

    return `${timestamp} ${level} [${service || 'app'}] ${message}${metaStr}`;
  })
);

/**
 * Форматтер для консоли без цветов (production)
 */
export const simpleConsoleFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, service, ...meta }) => {
    const metaStr = Object.keys(meta).length > 0
      ? ` ${JSON.stringify(meta)}`
      : '';

    return `${timestamp} ${level.toUpperCase()} [${service || 'app'}] ${message}${metaStr}`;
  })
);

/**
 * Форматтер для файлов (JSON)
 * Structured logging для парсинга и анализа
 */
export const jsonFileFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  winston.format.metadata({ fillExcept: ['message', 'level', 'timestamp', 'service'] }),
  winston.format.json()
);

/**
 * Форматтер для ошибок
 * Включает stack trace
 */
export const errorFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

/**
 * Получает форматтер для консоли в зависимости от окружения
 */
export function getConsoleFormat(colorize: boolean = true) {
  return colorize ? prettyConsoleFormat : simpleConsoleFormat;
}
