/**
 * @fileoverview Winston Transports
 *
 * Транспорты для вывода логов в различные назначения
 */

import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import path from 'path';
import { logConfig } from '../config';
import { getConsoleFormat, jsonFileFormat, errorFormat } from '../formatters';

/**
 * Консольный транспорт
 */
export function createConsoleTransport(): winston.transport {
  return new winston.transports.Console({
    level: logConfig.level,
    format: getConsoleFormat(logConfig.console.colorize),
  });
}

/**
 * Файловый транспорт с ротацией (все логи)
 */
export function createCombinedFileTransport(): winston.transport | null {
  if (!logConfig.file.enabled) {
    return null;
  }

  return new DailyRotateFile({
    level: logConfig.level,
    dirname: logConfig.file.directory,
    filename: 'combined-%DATE%.log',
    datePattern: logConfig.file.datePattern,
    maxSize: logConfig.file.maxSize,
    maxFiles: logConfig.file.maxFiles,
    format: jsonFileFormat,
    auditFile: path.join(logConfig.file.directory, '.audit-combined.json'),
  });
}

/**
 * Файловый транспорт только для ошибок
 */
export function createErrorFileTransport(): winston.transport | null {
  if (!logConfig.errorFile.enabled || !logConfig.file.enabled) {
    return null;
  }

  return new DailyRotateFile({
    level: 'error',
    dirname: logConfig.file.directory,
    filename: 'error-%DATE%.log',
    datePattern: logConfig.file.datePattern,
    maxSize: logConfig.file.maxSize,
    maxFiles: logConfig.file.maxFiles,
    format: errorFormat,
    auditFile: path.join(logConfig.file.directory, '.audit-error.json'),
  });
}

/**
 * HTTP access log транспорт
 */
export function createHttpFileTransport(): winston.transport | null {
  if (!logConfig.file.enabled) {
    return null;
  }

  return new DailyRotateFile({
    level: 'http',
    dirname: logConfig.file.directory,
    filename: 'http-%DATE%.log',
    datePattern: logConfig.file.datePattern,
    maxSize: logConfig.file.maxSize,
    maxFiles: logConfig.file.maxFiles,
    format: jsonFileFormat,
    auditFile: path.join(logConfig.file.directory, '.audit-http.json'),
  });
}

/**
 * Создает массив всех активных транспортов
 */
export function createTransports(): winston.transport[] {
  const transports: winston.transport[] = [];

  // Консоль всегда включена
  if (logConfig.console.enabled) {
    transports.push(createConsoleTransport());
  }

  // Файловые транспорты (если включены)
  const combinedTransport = createCombinedFileTransport();
  if (combinedTransport) {
    transports.push(combinedTransport);
  }

  const errorTransport = createErrorFileTransport();
  if (errorTransport) {
    transports.push(errorTransport);
  }

  const httpTransport = createHttpFileTransport();
  if (httpTransport) {
    transports.push(httpTransport);
  }

  return transports;
}
