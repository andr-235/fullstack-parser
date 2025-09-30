/**
 * Unit тесты для logger.ts
 */

import winston from 'winston';
import { createLogger, withContext, formatError, AppLogger, LoggerContext } from '@/utils/logger';

describe('Logger Utils', () => {
  describe('createLogger', () => {
    beforeEach(() => {
      // Очищаем env переменные перед каждым тестом
      delete process.env.LOG_LEVEL;
    });

    it('должен создать logger с дефолтными настройками', () => {
      const logger = createLogger();

      expect(logger).toBeDefined();
      expect(logger.level).toBe('info');
    });

    it('должен создать logger с кастомным уровнем логирования', () => {
      const logger = createLogger({ level: 'debug' });

      expect(logger.level).toBe('debug');
    });

    it('должен создать logger с кастомным service', () => {
      const logger = createLogger({ service: 'test-service' });

      expect(logger.defaultMeta).toMatchObject({ service: 'test-service' });
    });

    it('должен создать logger с кастомным environment', () => {
      const logger = createLogger({ environment: 'production' });

      expect(logger.defaultMeta).toMatchObject({ environment: 'production' });
    });

    it('должен использовать LOG_LEVEL из env', () => {
      process.env.LOG_LEVEL = 'warn';
      const logger = createLogger();

      expect(logger.level).toBe('warn');
      delete process.env.LOG_LEVEL;
    });

    it('должен использовать NODE_ENV из env', () => {
      process.env.NODE_ENV = 'test';
      const logger = createLogger();

      expect(logger.defaultMeta).toMatchObject({ environment: 'test' });
    });
  });

  describe('createLogger transports', () => {
    it('не должен создавать file transports в тестовом окружении', () => {
      const logger = createLogger({ environment: 'test' });

      // В тестовом окружении должен быть только Console transport
      expect(logger.transports).toHaveLength(1);
      expect(logger.transports[0]).toBeInstanceOf(winston.transports.Console);
    });

    it('должен создавать file transports в production окружении', () => {
      const logger = createLogger({ environment: 'production' });

      // В production должны быть Console + 2 file transports (error + combined)
      expect(logger.transports.length).toBeGreaterThan(1);
    });

    it('должен создавать file transports в development окружении', () => {
      const logger = createLogger({ environment: 'development' });

      // В development должны быть Console + 2 file transports
      expect(logger.transports.length).toBeGreaterThan(1);
    });
  });

  describe('withContext', () => {
    it('должен создать child logger с контекстом', () => {
      const baseLogger = createLogger({ environment: 'test' });
      const context: LoggerContext = {
        requestId: 'req-123',
        userId: 'user-456'
      };

      const childLogger = withContext(baseLogger, context);

      expect(childLogger).toBeDefined();
      expect(childLogger).not.toBe(baseLogger);
      // Проверяем что child logger работает
      expect(() => childLogger.info('test')).not.toThrow();
    });

    it('должен сохранить базовые мета-данные родительского logger', () => {
      const baseLogger = createLogger({ service: 'test-service', environment: 'test' });
      const context: LoggerContext = { requestId: 'req-123' };

      const childLogger = withContext(baseLogger, context);

      expect(childLogger).toBeDefined();
      expect(childLogger).not.toBe(baseLogger);
      // Проверяем что базовые мета-данные присутствуют
      expect(childLogger.defaultMeta).toHaveProperty('service', 'test-service');
      expect(childLogger.defaultMeta).toHaveProperty('environment', 'test');
    });

    it('должен поддерживать любые кастомные поля в контексте', () => {
      const baseLogger = createLogger({ environment: 'test' });
      const context: LoggerContext = {
        requestId: 'req-123',
        customField: 'custom-value',
        nested: { field: 'value' }
      };

      const childLogger = withContext(baseLogger, context);

      expect(childLogger).toBeDefined();
      expect(childLogger).not.toBe(baseLogger);
      // Проверяем что child logger может логировать без ошибок
      expect(() => childLogger.info('test with context')).not.toThrow();
    });
  });

  describe('formatError', () => {
    it('должен форматировать стандартный Error', () => {
      const error = new Error('Test error');
      const formatted = formatError(error);

      expect(formatted).toHaveProperty('message', 'Test error');
      expect(formatted).toHaveProperty('name', 'Error');
      expect(formatted).toHaveProperty('stack');
      expect(formatted.stack).toContain('Test error');
    });

    it('должен включать cause если он есть', () => {
      const cause = new Error('Cause error');
      const error = new Error('Main error');
      // Manually add cause property
      (error as any).cause = cause;
      const formatted = formatError(error);

      expect(formatted).toHaveProperty('cause');
      expect(formatted.cause).toBe(cause);
    });

    it('должен обрабатывать кастомные Error классы', () => {
      class CustomError extends Error {
        constructor(message: string) {
          super(message);
          this.name = 'CustomError';
        }
      }

      const error = new CustomError('Custom error');
      const formatted = formatError(error);

      expect(formatted).toHaveProperty('name', 'CustomError');
      expect(formatted).toHaveProperty('message', 'Custom error');
    });
  });

  describe('AppLogger class', () => {
    let logger: AppLogger;

    beforeEach(() => {
      logger = new AppLogger({ environment: 'test' });
    });

    it('должен создать instance класса AppLogger', () => {
      expect(logger).toBeInstanceOf(AppLogger);
    });

    it('должен иметь метод info', () => {
      expect(logger.info).toBeDefined();
      expect(typeof logger.info).toBe('function');
    });

    it('должен иметь метод error', () => {
      expect(logger.error).toBeDefined();
      expect(typeof logger.error).toBe('function');
    });

    it('должен иметь метод warn', () => {
      expect(logger.warn).toBeDefined();
      expect(typeof logger.warn).toBe('function');
    });

    it('должен иметь метод debug', () => {
      expect(logger.debug).toBeDefined();
      expect(typeof logger.debug).toBe('function');
    });

    it('должен иметь метод setLevel', () => {
      expect(logger.setLevel).toBeDefined();
      expect(typeof logger.setLevel).toBe('function');
    });

    it('должен иметь метод getLevel', () => {
      expect(logger.getLevel).toBeDefined();
      expect(typeof logger.getLevel).toBe('function');
    });

    it('должен поддерживать изменение уровня логирования', () => {
      logger.setLevel('debug');
      expect(logger.getLevel()).toBe('debug');

      logger.setLevel('error');
      expect(logger.getLevel()).toBe('error');
    });
  });

  describe('AppLogger logging methods', () => {
    let logger: AppLogger;
    let mockWinston: jest.SpyInstance;

    beforeEach(() => {
      logger = new AppLogger({ environment: 'test' });
      // Mock winston методы для проверки вызовов
      mockWinston = jest.spyOn((logger as any).winston, 'info');
    });

    afterEach(() => {
      mockWinston.mockRestore();
    });

    it('info должен логировать с message и meta', () => {
      logger.info('Test message', { key: 'value' });

      expect(mockWinston).toHaveBeenCalledWith('Test message', { key: 'value' });
    });

    it('error должен форматировать Error объект', () => {
      const errorSpy = jest.spyOn((logger as any).winston, 'error');
      const error = new Error('Test error');

      logger.error('Error occurred', error);

      expect(errorSpy).toHaveBeenCalledWith(
        'Error occurred',
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Test error',
            name: 'Error',
            stack: expect.any(String)
          })
        })
      );

      errorSpy.mockRestore();
    });

    it('error должен логировать без error объекта', () => {
      const errorSpy = jest.spyOn((logger as any).winston, 'error');

      logger.error('Simple error message');

      expect(errorSpy).toHaveBeenCalledWith('Simple error message', undefined);

      errorSpy.mockRestore();
    });

    it('error должен логировать с произвольным error значением', () => {
      const errorSpy = jest.spyOn((logger as any).winston, 'error');
      const errorData = { code: 500, message: 'Server error' };

      logger.error('Error with data', errorData);

      expect(errorSpy).toHaveBeenCalledWith(
        'Error with data',
        expect.objectContaining({
          error: errorData
        })
      );

      errorSpy.mockRestore();
    });

    it('warn должен логировать с message и meta', () => {
      const warnSpy = jest.spyOn((logger as any).winston, 'warn');

      logger.warn('Warning message', { level: 'high' });

      expect(warnSpy).toHaveBeenCalledWith('Warning message', { level: 'high' });

      warnSpy.mockRestore();
    });

    it('debug должен логировать с message и meta', () => {
      const debugSpy = jest.spyOn((logger as any).winston, 'debug');

      logger.debug('Debug message', { details: 'some details' });

      expect(debugSpy).toHaveBeenCalledWith('Debug message', { details: 'some details' });

      debugSpy.mockRestore();
    });
  });

  describe('Обратная совместимость', () => {
    it('default export должен быть instance AppLogger', () => {
      const defaultLogger = require('@/utils/logger').default;

      expect(defaultLogger).toBeInstanceOf(AppLogger);
      expect(defaultLogger.info).toBeDefined();
      expect(defaultLogger.error).toBeDefined();
      expect(defaultLogger.warn).toBeDefined();
      expect(defaultLogger.debug).toBeDefined();
    });

    it('должен поддерживать старый стиль использования', () => {
      const defaultLogger = require('@/utils/logger').default;

      // Эти вызовы не должны выбрасывать ошибки
      expect(() => {
        defaultLogger.info('Test info');
        defaultLogger.warn('Test warn');
        defaultLogger.debug('Test debug');
        defaultLogger.error('Test error');
      }).not.toThrow();
    });
  });
});