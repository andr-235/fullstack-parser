import { PrismaClient } from '@prisma/client';
import logger from '../utils/logger';

// Расширенный тип Prisma Client с custom методами
export type ExtendedPrismaClient = PrismaClient;

// Конфигурация логирования для разных окружений
const getLogLevel = () => {
  const environment = process.env.NODE_ENV || 'development';

  switch (environment) {
    case 'development':
      return ['query', 'info', 'warn', 'error'] as const;
    case 'production':
      return ['warn', 'error'] as const;
    case 'test':
      return ['error'] as const;
    default:
      return ['warn', 'error'] as const;
  }
};

// Конфигурация connection pooling через DB_URL parameters
const getDatabaseUrl = (): string => {
  const baseUrl = process.env.DB_URL || process.env.DATABASE_URL;
  if (!baseUrl) {
    throw new Error('DB_URL or DATABASE_URL environment variable is required');
  }

  // Добавляем параметры connection pooling если их нет
  const url = new URL(baseUrl);

  // Настройки connection pool
  if (!url.searchParams.has('connection_limit')) {
    url.searchParams.set('connection_limit', '20');
  }
  if (!url.searchParams.has('pool_timeout')) {
    url.searchParams.set('pool_timeout', '10');
  }
  if (!url.searchParams.has('connect_timeout')) {
    url.searchParams.set('connect_timeout', '5');
  }

  return url.toString();
};

// Singleton паттерн для Prisma Client с connection pooling
class PrismaService {
  private static instance: PrismaClient | null = null;
  private static isConnected = false;
  private static reconnectAttempts = 0;
  private static maxReconnectAttempts = 5;
  private static reconnectDelay = 1000; // 1 секунда

  static getInstance(): PrismaClient {
    if (!PrismaService.instance) {
      try {
        PrismaService.instance = new PrismaClient({
          log: getLogLevel().map(level => ({
            level,
            emit: 'event' as const
          })),
          errorFormat: 'pretty',
          datasources: {
            db: {
              url: getDatabaseUrl()
            }
          }
        });

        // Настройка обработчиков логирования
        PrismaService.setupLogHandlers();
      } catch (error) {
        logger.error('Failed to create Prisma Client instance', error);
        throw error;
      }
    }

    return PrismaService.instance;
  }

  private static setupLogHandlers(): void {
    // Логирование будет добавлено позже после исправления типов
    // TODO: Добавить обработчики событий Prisma
    logger.info('Prisma log handlers will be set up after type fixes');
  }

  /**
   * Подключение к базе данных с retry механизмом
   */
  static async connect(): Promise<void> {
    if (PrismaService.isConnected) {
      return;
    }

    try {
      const prisma = PrismaService.getInstance();
      await prisma.$connect();
      PrismaService.isConnected = true;
      PrismaService.reconnectAttempts = 0; // Сброс счетчика при успешном подключении

      logger.info('Prisma connected to database successfully', {
        database: 'vk_analyzer',
        provider: 'postgresql',
        connectionUrl: getDatabaseUrl().replace(/password=[^&]*/, 'password=***')
      });
    } catch (error) {
      logger.error('Failed to connect to database via Prisma', error);
      await PrismaService.handleConnectionError(error);
    }
  }

  /**
   * Обработка ошибок подключения с retry механизмом
   */
  private static async handleConnectionError(error: any): Promise<void> {
    if (PrismaService.reconnectAttempts < PrismaService.maxReconnectAttempts) {
      PrismaService.reconnectAttempts++;
      const delay = PrismaService.reconnectDelay * Math.pow(2, PrismaService.reconnectAttempts - 1);

      logger.warn(`Attempting to reconnect to database (${PrismaService.reconnectAttempts}/${PrismaService.maxReconnectAttempts}) in ${delay}ms`, {
        error: error instanceof Error ? error.message : String(error)
      });

      await new Promise(resolve => setTimeout(resolve, delay));
      await PrismaService.connect();
    } else {
      const errorMessage = `Database connection failed after ${PrismaService.maxReconnectAttempts} attempts: ${error instanceof Error ? error.message : String(error)}`;
      logger.error('Max reconnection attempts reached. Database unavailable.', {
        attempts: PrismaService.reconnectAttempts,
        error: error instanceof Error ? error.message : String(error)
      });
      throw new Error(errorMessage);
    }
  }

  /**
   * Отключение от базы данных
   */
  static async disconnect(): Promise<void> {
    if (!PrismaService.instance || !PrismaService.isConnected) {
      return;
    }

    try {
      await PrismaService.instance.$disconnect();
      PrismaService.isConnected = false;
      PrismaService.instance = null;

      logger.info('Prisma disconnected from database');
    } catch (error) {
      logger.error('Error disconnecting from database via Prisma', error);
      throw error;
    }
  }

  /**
   * Проверка здоровья подключения с расширенной диагностикой
   */
  static async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    latency?: number;
    error?: string;
    connectionStats?: any;
  }> {
    const start = Date.now();

    try {
      const prisma = PrismaService.getInstance();
      await prisma.$queryRaw`SELECT 1`;

      // Получение статистики подключений
      const connectionStats = await PrismaService.getConnectionStats();

      return {
        status: 'healthy',
        latency: Date.now() - start,
        connectionStats
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      return {
        status: 'unhealthy',
        latency: Date.now() - start,
        error: errorMsg
      };
    }
  }

  /**
   * Получение статистики подключений к базе данных
   */
  static async getConnectionStats(): Promise<any> {
    try {
      const prisma = PrismaService.getInstance();
      const result = await prisma.$queryRaw`
        SELECT
          count(*) as total_connections,
          count(*) FILTER (WHERE state = 'active') as active_connections,
          count(*) FILTER (WHERE state = 'idle') as idle_connections,
          count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
        FROM pg_stat_activity
        WHERE datname = current_database()
      `;
      return result;
    } catch (error) {
      logger.error('Failed to get connection stats', error);
      return null;
    }
  }

  /**
   * Очистка idle соединений
   */
  static async cleanupConnections(): Promise<void> {
    try {
      const prisma = PrismaService.getInstance();
      // Завершение idle соединений старше 5 минут
      await prisma.$queryRaw`
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = current_database()
          AND state = 'idle'
          AND state_change < NOW() - INTERVAL '5 minutes'
          AND pid <> pg_backend_pid()
      `;
      logger.info('Cleaned up idle connections');
    } catch (error) {
      logger.error('Failed to cleanup connections', error);
    }
  }

  /**
   * Проверка состояния подключения
   */
  static isHealthy(): boolean {
    return PrismaService.isConnected && PrismaService.instance !== null;
  }

  /**
   * Выполнение миграций (для development)
   */
  static async runMigrations(): Promise<void> {
    try {
      const prisma = PrismaService.getInstance();
      // Prisma migrations запускаются через CLI, но можно проверить схему
      await prisma.$executeRaw`SELECT 1`;
      logger.info('Database schema is accessible');
    } catch (error) {
      logger.error('Error accessing database schema', error);
      throw error;
    }
  }

  /**
   * Сброс соединения (полезно для тестов)
   */
  static async reset(): Promise<void> {
    await PrismaService.disconnect();
    PrismaService.instance = null;
    PrismaService.isConnected = false;
  }
}

// Ленивый экспорт singleton instance (только при первом использовании)
export const prisma = new Proxy({} as PrismaClient, {
  get: (target, prop) => {
    const instance = PrismaService.getInstance();
    const value = (instance as any)[prop];
    return typeof value === 'function' ? value.bind(instance) : value;
  }
});

// Экспорт класса для управления соединением
export { PrismaService };

// Экспорт типов из сгенерированного Prisma Client
export type {
  groups as Group,
  posts as Post,
  comments as Comment,
  tasks as Task,
  Prisma,
} from '@prisma/client';

// Graceful shutdown для production
if (process.env.NODE_ENV === 'production') {
  process.on('SIGINT', async () => {
    await PrismaService.disconnect();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    await PrismaService.disconnect();
    process.exit(0);
  });
}

export default prisma;