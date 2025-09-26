/**
 * Winston logger instance for VK backend.
 * Methods: .info(msg, [meta]), .error(err, [meta]), .warn(msg, [meta]), .debug(msg, [meta]).
 */

import winston, { Logger as WinstonLogger } from 'winston';
import { Logger, LogLevel } from '@/types/common';
import { Environment } from '@/types/database';

interface LoggerOptions {
  level?: LogLevel;
  service?: string;
  environment?: Environment;
}

class AppLogger implements Logger {
  private winston: WinstonLogger;

  constructor(options: LoggerOptions = {}) {
    const {
      level = 'info',
      service = 'vk-backend',
      environment = process.env.NODE_ENV as Environment || 'development'
    } = options;

    this.winston = winston.createLogger({
      level,
      defaultMeta: { service, environment },
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      transports: this.createTransports(level, environment)
    });
  }

  private createTransports(level: LogLevel, environment: Environment): winston.transport[] {
    const transports: winston.transport[] = [
      new winston.transports.Console({
        level,
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.simple()
        )
      })
    ];

    if (environment !== 'test') {
      transports.push(
        new winston.transports.File({
          filename: 'backend/logs/error.log',
          level: 'error'
        }),
        new winston.transports.File({
          filename: 'backend/logs/combined.log',
          level: 'info',
          maxsize: 5242880,
          maxFiles: 5
        })
      );
    }

    return transports;
  }

  info(message: string, meta?: any): void {
    this.winston.info(message, meta);
  }

  error(message: string, error?: Error | any, meta?: any): void {
    if (error instanceof Error) {
      this.winston.error(message, { error: error.message, stack: error.stack, ...meta });
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

const logger = new AppLogger();

export default logger;
export { AppLogger };
export type { Logger };