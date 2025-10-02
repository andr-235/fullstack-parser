/**
 * @fileoverview Winston Logger Configuration
 *
 * Конфигурация для продвинутого логирования с Winston
 */

import path from 'path';

/**
 * Уровни логирования
 */
export const LOG_LEVELS = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
} as const;

/**
 * Цвета для уровней логирования
 */
export const LOG_COLORS = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'blue',
} as const;

/**
 * Конфигурация логирования
 */
export interface LogConfig {
  level: string;
  console: {
    enabled: boolean;
    colorize: boolean;
  };
  file: {
    enabled: boolean;
    directory: string;
    maxSize: string;
    maxFiles: string;
    datePattern: string;
  };
  errorFile: {
    enabled: boolean;
  };
}

/**
 * Получает уровень логирования из ENV или по умолчанию
 */
function getLogLevel(): string {
  const envLevel = process.env.LOG_LEVEL?.toLowerCase();
  const nodeEnv = process.env.NODE_ENV;

  // Явно указанный уровень
  if (envLevel && Object.keys(LOG_LEVELS).includes(envLevel)) {
    return envLevel;
  }

  // По умолчанию в зависимости от окружения
  switch (nodeEnv) {
    case 'production':
      return 'info';
    case 'test':
      return 'error';
    case 'development':
    default:
      return 'debug';
  }
}

/**
 * Директория для логов
 */
const logsDirectory = process.env.LOGS_DIR || path.join(process.cwd(), 'logs');

/**
 * Конфигурация логирования по умолчанию
 */
export const logConfig: LogConfig = {
  level: getLogLevel(),

  // Консольный вывод
  console: {
    enabled: true,
    colorize: process.env.NODE_ENV !== 'production',
  },

  // Файловое логирование
  file: {
    enabled: process.env.ENABLE_FILE_LOGGING === 'true' || process.env.NODE_ENV === 'production',
    directory: logsDirectory,
    maxSize: '20m', // 20 мегабайт
    maxFiles: '14d', // 14 дней
    datePattern: 'YYYY-MM-DD',
  },

  // Отдельный файл для ошибок
  errorFile: {
    enabled: process.env.ENABLE_ERROR_FILE === 'true' || process.env.NODE_ENV === 'production',
  },
};

/**
 * Метаданные по умолчанию для всех логов
 */
export const defaultMetadata = {
  service: process.env.SERVICE_NAME || 'vk-backend',
  environment: process.env.NODE_ENV || 'development',
  hostname: process.env.HOSTNAME || 'localhost',
};
